"""
Ghostwriting-lane morning briefing — the human's daily ammo, drafted by machine.

Sections:
  1. INBOX — every received LinkedIn message (unread or last 72h) via SendPilot,
     with a slop-gated draft reply for simple acks and a "reply personally"
     flag + angle for anything substantive. Replies are never auto-sent.
  2. ENGAGE — 10 rotating engagement targets from the health-coach list with a
     starter comment line + angle. The starter must be adapted to whatever
     their actual latest post says; it is ammo, not copy-paste.
  3. SCORECARD — funnel numbers (see scorecard.py) incl. live accept counts.

Output: freelance-leads/briefings/YYYY-MM-DD.md  (+ macOS notification)
Run:    python3 freelance-leads/ghostwriting_briefing.py
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

SKILL = "/Users/toto/.claude/skills/sendpilot-outreach"
sys.path.insert(0, SKILL)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, HERE)

from dotenv import load_dotenv  # noqa: E402
load_dotenv(os.path.join(REPO_ROOT, ".env"))
from sendpilot import SP  # noqa: E402

import scorecard  # noqa: E402
from connect_drip import clean_first_name  # noqa: E402
from linkedin_agent.stop_slop_gate import score_post  # noqa: E402

LEADS_FILE = os.path.join(HERE, "health-coaches-2026-06-21.json")
REPLIES_FILE = os.path.join(HERE, "replies-inbox.json")
BRIEFING_DIR = os.path.join(HERE, "briefings")
TRACKING_CAMPAIGN_ID = "cmr64vwoi037z0a01nvq9z4wt"

INBOX_WINDOW_HOURS = 72
ENGAGE_TARGETS_PER_DAY = 10

# Comment angles by specialty keyword. Starter lines get adapted by the human
# to the target's actual latest post; the angle explains the play.
ANGLE_BANK = {
    "nutrition": (
        "Ask which habit or marker shifted first for their client.",
        "From my clinic years, the lab number people ignore is the one that moves first.",
    ),
    "coach": (
        "Ask what made their client finally act after months of knowing.",
        "I saw this in medicine too: information rarely changes behavior, identity does.",
    ),
    "fitness": (
        "Ask how they get clients past week 3, where adherence usually dies.",
        "As a physician I watched prescriptions fail for the same reason programs do.",
    ),
    "mental": (
        "Ask what sign tells them a client is ready for the harder work.",
        "The waiting room taught me people book help long after they needed it.",
    ),
    "default": (
        "Ask one specific question about how they deliver their service.",
        "Former physician here, your take maps to what I saw with patients.",
    ),
}


def pick_angle(lead: dict) -> tuple:
    blob = " ".join(str(lead.get(k, "")) for k in
                    ("job_title", "industry", "profile_summary", "company")).lower()
    for key, angle in ANGLE_BANK.items():
        if key != "default" and key in blob:
            return angle
    return ANGLE_BANK["default"]


def draft_ack_reply(name_hint: str, lead: dict | None) -> str | None:
    """Reply for a bare 'thanks for connecting' message. Slop-gated."""
    fn = clean_first_name(lead.get("first_name", "")) if lead else \
        (name_hint.split()[0] if name_hint else "there")
    thing = (lead or {}).get("company") or ""
    if thing:
        msg = (f"Good to be connected, {fn}. I looked at {thing} and wondered: "
               f"where do most of your new clients come from these days? "
               f"I ask because I compare notes with other health practitioners.")
    else:
        msg = (f"Good to be connected, {fn}. What are you working on this "
               f"season? I like hearing what other health folks are building.")
    total, _, _ = score_post(msg)
    return msg if total >= 35 else None


def looks_like_pitch(content: str) -> bool:
    """Mass-DM / automated pitch heuristic: link drops, promo phrasing."""
    low = content.lower()
    if "http" in low or "www." in low:
        return True
    return any(p in low for p in (
        "playbook", "save up to", "you could save", "great fit for",
        "we're bringing together", "curated group", "special offer",
        "eligible to study", "book a demo", "free trial"))


def inbox_section(sp: SP, leads_by_name: dict) -> list[str]:
    lines = ["## 1. Inbox — answer these first (revenue lives here)", ""]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=INBOX_WINDOW_HOURS)
    convos = sp._get("/inbox/conversations", limit=100).get("conversations", [])
    fresh, seen = [], set()
    for c in convos:
        lm = c.get("lastMessage") or {}
        if lm.get("direction") != "received":
            continue
        ts = lm.get("sentAt", "")
        try:
            when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if when < cutoff:
            continue
        who = (c.get("participants") or [{}])[0].get("name", "?")
        content = (lm.get("content") or "").strip()
        if (who, content[:60]) in seen:
            continue
        seen.add((who, content[:60]))
        fresh.append((who, content, leads_by_name.get(who.lower())))
    # Health-coach leads first, pitches last.
    fresh.sort(key=lambda t: (t[2] is None, looks_like_pitch(t[1])))

    pitches = []
    for who, content, lead in fresh:
        if looks_like_pitch(content) and lead is None:
            pitches.append(who)
            continue
        lines.append(f"### {who}" + ("  ← health-coach lead" if lead else ""))
        lines.append(f"> {content}")
        is_bare_ack = "thank" in content.lower() and len(content) < 90
        if is_bare_ack:
            draft = draft_ack_reply(who, lead)
            if draft:
                lines.append(f"**Draft reply (tweak, then send):** {draft}")
        else:
            lines.append("**Substantive message — reply personally.** Angle: "
                         "answer their actual point first, one genuine question "
                         "back, no pitch until they ask what you do.")
        lines.append("")
    if pitches:
        lines.append(f"_Skipped {len(pitches)} likely pitch/automated message(s): "
                     f"{', '.join(sorted(set(pitches)))}._\n")
    if not fresh:
        lines.append("_No new received messages in the window._\n")
    # Watcher-flagged replies not yet handled
    if os.path.exists(REPLIES_FILE):
        with open(REPLIES_FILE) as f:
            flagged = [r for r in json.load(f) if not r.get("handled")]
        for r in flagged:
            lines.append(f"- Watcher flag: **{r['name']}** ({r.get('company','—')}) "
                         f"replied on {r['flagged']} — {r['linkedin_url']}")
        if flagged:
            lines.append("")
    return lines


def engage_section(leads: list, statuses: dict) -> list[str]:
    lines = [f"## 2. Engage — {ENGAGE_TARGETS_PER_DAY} comment targets (~15 min)",
             "",
             "_Open the profile, read their latest post, adapt the starter. "
             "A real comment beats a clever one._", ""]
    # Priority: connect sent but not yet accepted (comments lift accept rate),
    # then accepted (stay warm). Rotate daily so targets differ each morning.
    pending = [l for l in leads if l.get("connect_sent")
               and statuses.get(l.get("sp_lead_id")) == "CONNECTION_SENT"]
    warm = [l for l in leads if l.get("connect_sent")
            and statuses.get(l.get("sp_lead_id")) in
            ("CONNECTION_ACCEPTED", "MESSAGE_SENT", "REPLY_RECEIVED")]
    pool = pending + warm
    if not pool:
        return lines + ["_No targets yet — drip starts filling this daily._", ""]
    day = int(time.strftime("%j"))
    start = (day * ENGAGE_TARGETS_PER_DAY) % len(pool)
    targets = (pool + pool)[start:start + ENGAGE_TARGETS_PER_DAY][:len(pool)]
    for l in targets:
        ask, starter = pick_angle(l)
        state = statuses.get(l.get("sp_lead_id"), "?").replace("_", " ").lower()
        lines.append(f"- **{l['full_name']}** — {l.get('job_title','?')} @ "
                     f"{l.get('company','—')} ({state})")
        lines.append(f"  {l['linkedin_url']}")
        lines.append(f"  Angle: {ask}")
        lines.append(f"  Starter: \"{starter}\"")
        lines.append("")
    return lines


def main() -> None:
    with open(LEADS_FILE) as f:
        leads = json.load(f)
    leads_by_name = {l.get("full_name", "").lower(): l for l in leads}

    sp = SP()
    statuses = {cl["id"]: cl.get("status", "?")
                for cl in sp.leads(TRACKING_CAMPAIGN_ID)}

    card = scorecard.compute(campaign_statuses=statuses)
    today = time.strftime("%Y-%m-%d")
    doc = [f"# Ghostwriting lane — {today}", "",
           f"**Scorecard:** {scorecard.render(card)}", ""]
    # Accept-sync sentinel: SendPilot's LinkedIn sync flipping leads to
    # CONNECTION_ACCEPTED is an unvalidated assumption for connects sent
    # outside a campaign (see accept_watcher.py docstring). If nothing has
    # flipped by day 5, the sync is probably blind — surface the fallback.
    if card["campaign_day"] >= 5 and card["connects_sent"] >= 10 and card["accepted"] == 0:
        doc += ["> ⚠️ **Accept-sync check failed?** 0 accepts after "
                f"{card['campaign_day']} days across {card['connects_sent']} connects. "
                "Open LinkedIn → My Network → Connections (sort: recently added) and "
                "cross-check. If people HAVE accepted, the tracker sync is blind — "
                "switch accept_watcher.py to probe-DM mode (see its docstring fallback).", ""]
    doc += inbox_section(sp, leads_by_name)
    doc += engage_section(leads, statuses)
    doc += ["---",
            "Log your work: `python3 freelance-leads/scorecard.py log touch <n>` "
            "| `log call \"Name\"` | `log client \"Name\" <mrr>`"]

    os.makedirs(BRIEFING_DIR, exist_ok=True)
    out = os.path.join(BRIEFING_DIR, f"{today}.md")
    with open(out, "w") as f:
        f.write("\n".join(doc) + "\n")
    print(f"briefing written: {out}")

    inbox_count = sum(1 for line in doc if line.startswith("### "))
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{inbox_count} inbox item(s), '
             f'{ENGAGE_TARGETS_PER_DAY} engage targets ready" '
             f'with title "Ghostwriting briefing {today}"'],
            check=False, timeout=10)
    except Exception:
        pass


if __name__ == "__main__":
    main()
