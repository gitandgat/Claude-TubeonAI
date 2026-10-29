"""Job Pilot — Telegram front-end for the ottawa-job-agent pipeline.

Wraps tracker.py / agent_config.py / run.sh behind a small set of Claude
Agent SDK tools so Sahawat can check status, review pending applications,
correct outcomes, toggle review-only mode, and trigger a manual run from
Telegram instead of the terminal. Restricted to a single allowlisted
Telegram user id — this exposes tools that can trigger real automation.

Run: ./telegram_venv/bin/python3 telegram_bot.py
"""

import asyncio
import logging
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    create_sdk_mcp_server,
    tool,
)

import agent_config
import tracker

BASE = Path(__file__).resolve().parent
load_dotenv(BASE.parent / ".env")

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ["TELEGRAM_ALLOWED_USER_ID"])

RUN_SCRIPT = BASE / "run.sh"
MANUAL_DIR = BASE / "manual_applications"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("job_pilot")

# Set once main() creates the bot Application, so the trigger_run tool can
# push a proactive "run finished" message without waiting on the caller.
_bot_app: Application | None = None
_run_in_progress = False


# ---------------------------------------------------------------------------
# Tools — thin wrappers over the real pipeline modules, nothing reimplemented.
# ---------------------------------------------------------------------------

@tool("get_status", "Summarize the job application tracker: counts by status and the most recently updated applications.", {})
async def get_status(args: dict) -> dict:
    counts = tracker.stats()
    data = tracker._load()
    recent = sorted(
        data.values(),
        key=lambda e: (e.get("history") or [{}])[-1].get("date", ""),
        reverse=True,
    )[:8]

    lines = ["Counts by status:"]
    for status, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"  {tracker.STATUS_LABELS.get(status, status)}: {n}")
    lines.append("")
    lines.append("Recently updated:")
    for e in recent:
        last = (e.get("history") or [{}])[-1]
        lines.append(f"  [{e.get('status')}] {e.get('title')} @ {e.get('company')} — {last.get('date', '?')}")
    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


PENDING_REVIEW_LIMIT = 15


@tool("list_pending_review", "List applications needing Sahawat's own action: tracker entries stuck as 'pending' or 'draft_ready', plus prefilled packages waiting in manual_applications/. Shows only the top candidates by fit score — the pending pile is large and most of it is low-value noise the pipeline couldn't safely auto-apply to.", {})
async def list_pending_review(args: dict) -> dict:
    data = tracker._load()
    pending = [e for e in data.values() if e.get("status") in ("pending", "draft_ready")]
    pending.sort(key=lambda e: e.get("score") or 0, reverse=True)

    lines = []
    if pending:
        lines.append(f"{len(pending)} tracker items needing you — top {min(PENDING_REVIEW_LIMIT, len(pending))} by fit score:")
        for e in pending[:PENDING_REVIEW_LIMIT]:
            reason = e.get("no_apply_reason", "")
            lines.append(
                f"  [{e.get('status')}] {e.get('title')} @ {e.get('company')} "
                f"(score {e.get('score', '?')}/10){' — ' + reason if reason else ''}"
            )
    else:
        lines.append("No tracker items pending review.")

    manual_files = sorted(MANUAL_DIR.glob("*")) if MANUAL_DIR.exists() else []
    if manual_files:
        lines.append("")
        lines.append("Prefilled packages waiting in manual_applications/:")
        for f in manual_files:
            lines.append(f"  {f.name}")

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


def _find_matching_keys(query: str, data: dict) -> list:
    """AND-match every word of query against company+title combined.

    tracker.update_status() only checks whether the *whole* match string is a
    substring of company OR title alone, so a natural phrase like "GoodLife
    Fitness wellness coordinator" (company + title combined) never matches
    either field on its own. This resolves to a real tracker key first so
    update_status() hits its exact-key fast path instead.
    """
    words = query.lower().split()
    if not words:
        return []
    keys = []
    for k, v in data.items():
        haystack = f"{v.get('company', '')} {v.get('title', '')}".lower()
        if all(w in haystack for w in words):
            keys.append(k)
    return keys


@tool(
    "update_application",
    "Update the status of one tracked application, fuzzy-matched by company or job title.",
    {
        "type": "object",
        "properties": {
            "match": {"type": "string", "description": "Company name or job title (fuzzy match)."},
            "status": {
                "type": "string",
                "enum": list(tracker.STATUS_LABELS.keys()),
                "description": "New status.",
            },
            "note": {"type": "string", "description": "Optional note to record with this update."},
        },
        "required": ["match", "status"],
    },
)
async def update_application(args: dict) -> dict:
    match = args["match"]
    status = args["status"]
    note = args.get("note", "")

    data = tracker._load()
    key = match if match in data else None
    if key is None:
        candidates = _find_matching_keys(match, data)
        if len(candidates) > 1:
            lines = [f"'{match}' matches {len(candidates)} tracked applications — be more specific:"]
            for k in candidates[:8]:
                e = data[k]
                lines.append(f"  {e.get('title')} @ {e.get('company')}")
            return {"content": [{"type": "text", "text": "\n".join(lines)}], "is_error": True}
        if len(candidates) == 1:
            key = candidates[0]

    if key is None:
        return {
            "content": [{"type": "text", "text": f"No application found matching '{match}'."}],
            "is_error": True,
        }

    try:
        entry = tracker.update_status(key, status, note)
    except ValueError as e:
        return {"content": [{"type": "text", "text": str(e)}], "is_error": True}
    return {
        "content": [{
            "type": "text",
            "text": f"Updated: {entry['title']} @ {entry['company']} -> {status}",
        }]
    }


@tool(
    "review_mode",
    "Get or set the pipeline's review-only mode. When on, applications are filled but not auto-submitted.",
    {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["on", "off", "status"]},
        },
        "required": ["action"],
    },
)
async def review_mode(args: dict) -> dict:
    action = args["action"]
    if action == "status":
        state = "ON (applications held for review)" if agent_config.is_review_only() else "OFF (auto-submitting)"
        text = f"review_only: {state}"
    elif action == "on":
        agent_config.set_review_only(True)
        text = "review_only set to ON — applications will be filled but not submitted."
    else:
        agent_config.set_review_only(False)
        text = "review_only set to OFF — pipeline will auto-submit as before."
    return {"content": [{"type": "text", "text": text}]}


@tool("trigger_run", "Kick off a manual run of the job-search/apply pipeline right now, instead of waiting for the next scheduled 4-hour run. Runs in the background; you'll get a follow-up message when it finishes.", {})
async def trigger_run(args: dict) -> dict:
    global _run_in_progress
    if _run_in_progress:
        return {"content": [{"type": "text", "text": "A run is already in progress — I'll message you when it finishes."}]}

    _run_in_progress = True
    counts_before = tracker.stats()
    asyncio.create_task(_run_and_notify(counts_before))
    return {"content": [{"type": "text", "text": "Started a manual run. I'll message you here when it's done."}]}


async def _run_and_notify(counts_before: dict) -> None:
    global _run_in_progress
    try:
        proc = await asyncio.create_subprocess_exec(
            "/bin/bash", str(RUN_SCRIPT),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=BASE,
        )
        await proc.wait()
        counts_after = tracker.stats()
        diff_lines = []
        for status in set(counts_before) | set(counts_after):
            delta = counts_after.get(status, 0) - counts_before.get(status, 0)
            if delta:
                diff_lines.append(f"  {tracker.STATUS_LABELS.get(status, status)}: {'+' if delta > 0 else ''}{delta}")
        summary = "Manual run finished.\n" + ("\n".join(diff_lines) if diff_lines else "No changes to tracker counts.")
        if _bot_app is not None:
            await _bot_app.bot.send_message(chat_id=ALLOWED_USER_ID, text=summary)
    except Exception:
        log.exception("Manual run failed")
        if _bot_app is not None:
            await _bot_app.bot.send_message(chat_id=ALLOWED_USER_ID, text="Manual run crashed — check job_agent.log.")
    finally:
        _run_in_progress = False


JOB_PILOT_TOOLS = create_sdk_mcp_server(
    name="job_pilot",
    tools=[get_status, list_pending_review, update_application, review_mode, trigger_run],
)

SYSTEM_PROMPT = """You are Job Pilot, a Telegram assistant for Sahawat's fully-automated
Ottawa job-search pipeline (ottawa-job-agent). You have tools to check application
status, list items needing his own review, correct an application's tracked status,
toggle review-only mode, and trigger a manual pipeline run.

Valid statuses: pending, interested, draft_ready, applied, interview_scheduled, offer,
rejected_after_application, rejected_after_interview, ghosted, withdrawn, not_interested.

Be concise — this is a chat interface, not a report. Use plain text, short lines, no
heavy markdown. Never invent numbers; always call a tool to check real data before
answering a status/review question. Only call trigger_run when he clearly asks for a
fresh run right now."""


# ---------------------------------------------------------------------------
# Telegram wiring
# ---------------------------------------------------------------------------

class JobPilotSession:
    """One persistent Claude Agent SDK conversation for the whole bot process."""

    def __init__(self) -> None:
        self._client: ClaudeSDKClient | None = None
        self._lock = asyncio.Lock()

    async def _ensure_connected(self) -> ClaudeSDKClient:
        if self._client is None:
            options = ClaudeAgentOptions(
                system_prompt=SYSTEM_PROMPT,
                mcp_servers={"job_pilot": JOB_PILOT_TOOLS},
                tools=[],  # disable all built-in tools (Bash, Read, Write, WebFetch, ...) — job_pilot's 5 MCP tools are the only surface this bot should expose
                allowed_tools=[
                    "mcp__job_pilot__get_status",
                    "mcp__job_pilot__list_pending_review",
                    "mcp__job_pilot__update_application",
                    "mcp__job_pilot__review_mode",
                    "mcp__job_pilot__trigger_run",
                ],
                permission_mode="bypassPermissions",  # headless under launchd, no TTY to answer an interactive prompt
                cwd=str(BASE),
                setting_sources=[],  # isolate from ~/.claude/rules, monorepo CLAUDE.md, memory — irrelevant here and large enough to overflow the SDK's 1MB message buffer on first turn
            )
            self._client = ClaudeSDKClient(options)
            await self._client.connect()
        return self._client

    async def ask(self, text: str) -> str:
        async with self._lock:
            client = await self._ensure_connected()
            try:
                await client.query(text)
                reply_parts = []
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                reply_parts.append(block.text)
                return "\n".join(reply_parts).strip() or "(no reply)"
            except Exception:
                # Transport/session is now in an unknown state — drop it so the
                # next message reconnects fresh instead of reusing a dead client.
                self._client = None
                raise


session = JobPilotSession()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None or update.effective_user.id != ALLOWED_USER_ID:
        log.warning("Ignored message from unauthorized user id %s", update.effective_user.id if update.effective_user else None)
        return
    if not update.message or not update.message.text:
        return

    async def _keep_typing() -> None:
        # Telegram's "typing" indicator expires after ~5s; the agent's first
        # cold-start turn can take well over a minute, so refresh it until done.
        while True:
            await update.message.chat.send_action("typing")
            await asyncio.sleep(4)

    typing_task = asyncio.create_task(_keep_typing())
    try:
        reply = await asyncio.wait_for(session.ask(update.message.text), timeout=180)
    except asyncio.TimeoutError:
        log.error("Timed out waiting for agent response")
        reply = "That's taking too long — try again in a bit."
    except Exception:
        log.exception("Failed to answer message")
        reply = "Something went wrong on my end — check the bot's logs."
    finally:
        typing_task.cancel()
    await update.message.reply_text(reply)


def main() -> None:
    global _bot_app
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    _bot_app = app
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    log.info("Job Pilot bot starting (allowlisted user id: %s)", ALLOWED_USER_ID)
    app.run_polling()


if __name__ == "__main__":
    main()
