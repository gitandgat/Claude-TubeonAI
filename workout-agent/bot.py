"""Workout Telegram bot — type a session, get volume, PRs and whether you're progressing.

Runs on its own bot token. Telegram allows exactly ONE long-poller per token, and
TELEGRAM_BOT_TOKEN (Job Pilot) and TELEGRAM_NUTRITION_BOT_TOKEN (nutrition bot) are
both already held by running bots — reusing either would 409 a live service off the
air. This bot needs TELEGRAM_WORKOUT_BOT_TOKEN from a fresh BotFather registration.
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.error import Conflict, NetworkError, TimedOut
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import config
import parsing
import profile
import store
import workout

BASE = Path(__file__).resolve().parent
load_dotenv(BASE.parent / ".env")

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("workout-bot")

def _required(name: str, hint: str) -> str:
    """Fail with an instruction, not a KeyError. launchd KeepAlive restarts this
    every 30s, so a bare traceback becomes hundreds of identical useless log lines."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"{name} is not set in {BASE.parent / '.env'}.\n{hint}")
    return value


BOT_TOKEN = _required(
    "TELEGRAM_WORKOUT_BOT_TOKEN",
    "Register a NEW bot with @BotFather and put its token there. Do not reuse "
    "TELEGRAM_BOT_TOKEN or TELEGRAM_NUTRITION_BOT_TOKEN: Telegram allows one "
    "long-poller per token, so sharing one would 409 a running bot off the air.",
)
ALLOWED_USER_ID = int(
    _required("TELEGRAM_ALLOWED_USER_ID", "Your numeric Telegram user id.")
)

HELP = (
    "Type your session and I'll give you volume load, estimated 1RM, any PR, and how "
    "it compares to the last time you trained that lift.\n\n"
    "`bench 3x8 @ 80kg, squat 5,5,5 @ 100, pullups 3x12 bodyweight`\n\n"
    "Varying loads work too — `squat 100x5, 110x3, 120x1`.\n\n"
    "• /today — today's session\n"
    "• /week — volume and sets by muscle group vs your weekly targets\n"
    "• /pr <exercise> — history for one lift\n"
    "• /bodyweight <kg> — update the load used for pull-ups, dips, push-ups\n\n"
    "No calories-burned estimate: for resistance training those numbers are too "
    "inaccurate to act on, and a wrong one would corrupt the nutrition bot's targets."
)


def _authorized(update: Update) -> bool:
    user = update.effective_user
    if user is None or user.id != ALLOWED_USER_ID:
        log.warning("Ignored message from unauthorized user id %s", user.id if user else None)
        return False
    return True


async def _hold_typing(update: Update) -> None:
    # Telegram's typing indicator lapses after ~5s; a session takes longer.
    while True:
        await update.message.chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(4)


async def _run(update: Update, work, *args) -> None:
    """Run blocking work off the event loop, holding the typing indicator."""
    typing = asyncio.create_task(_hold_typing(update))
    try:
        reply = await asyncio.wait_for(
            asyncio.to_thread(work, *args), timeout=config.ANALYSIS_TIMEOUT
        )
    except asyncio.TimeoutError:
        log.error("Operation timed out")
        reply = "That took too long — try again?"
    except parsing.ParseError as exc:
        # Unreadable input is the sender's problem, not a crash. Showing it as
        # "Something broke" made a normal nudge look like a bug.
        log.info("Could not parse input: %s", exc)
        reply = str(exc)
    except store.StoreError as exc:
        log.exception("Supabase call failed")
        reply = f"Couldn't reach the workout database — {exc}"
    except Exception as exc:
        log.exception("Operation failed")
        reply = f"Something broke: {exc}"
    finally:
        typing.cancel()
    # No parse_mode: an error string can contain _ or * and would otherwise fail
    # to send at all, turning a readable message into silence.
    await update.message.reply_text(reply, parse_mode=None if reply.startswith(("Couldn", "Something", "That took")) else "Markdown")


def _log_and_format(text: str) -> str:
    try:
        report = workout.analyze(text)
    except parsing.ParseError:
        # Log a short preview so an unparseable message is diagnosable later.
        # Without this the log says only "no sets found" and the input is lost.
        log.warning("Unparseable session text (first 200 chars): %r", text[:200])
        raise
    return workout.format_session(workout.log_session(report, text))


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update) or not update.message or not update.message.text:
        return
    await _run(update, _log_and_format, update.message.text)


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if _authorized(update):
        await _run(update, workout.format_today)


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if _authorized(update):
        await _run(update, workout.format_week)


async def pr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        return
    query = " ".join(context.args or [])
    if not query:
        await update.message.reply_text("Which lift? e.g. /pr bench")
        return
    await _run(update, workout.format_pr, query)


async def bodyweight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        return
    current = profile.bodyweight_kg()
    if not context.args:
        await update.message.reply_text(
            f"Bodyweight is {current} kg. Change it with /bodyweight 85"
            if current
            else "Bodyweight isn't set. Set it with /bodyweight 85"
        )
        return
    try:
        stored = profile.set_bodyweight_kg(float(context.args[0]))
    except ValueError as exc:
        await update.message.reply_text(f"{exc} Try /bodyweight 85")
        return
    await update.message.reply_text(
        f"Bodyweight set to {stored} kg — used as the load for pull-ups, dips and push-ups "
        "from now on. Sessions already logged keep the load they were logged with."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if _authorized(update):
        await update.message.reply_text(HELP, parse_mode="Markdown")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Without a handler, python-telegram-bot dumps a full traceback for every
    transient polling hiccup (a concurrent getUpdates, a dropped connection),
    which buries real failures in the log."""
    error = context.error
    if isinstance(error, (NetworkError, TimedOut, Conflict)):
        log.warning("Transient Telegram error: %s: %s", type(error).__name__, error)
        return
    log.error("Unhandled error: %s", error, exc_info=error)


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(on_error)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(CommandHandler("pr", pr))
    app.add_handler(CommandHandler("bodyweight", bodyweight))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    log.info("Workout bot starting (allowlisted user id: %s)", ALLOWED_USER_ID)
    app.run_polling()


if __name__ == "__main__":
    main()
