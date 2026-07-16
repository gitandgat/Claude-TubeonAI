#!/usr/bin/env python3
"""
Last-mile execution agent for the Crossing Session launch.

The problem this solves: the daily briefing (outreach-briefing.py) already tells
you what to do. You don't do it. This is the layer that collapses the gap between
knowing and doing — it picks the SINGLE highest-leverage move, puts the finished
text on your clipboard, tracks progress to 10 sales, and nags harder when you skip.

It never sends anything itself. It prepares the artifact to one paste; you ship it.

Usage:
  python3 execute.py            # show today's ONE move + progress (default)
  python3 execute.py done       # mark the current top move done
  python3 execute.py dm <n>     # log n outreach messages sent today
  python3 execute.py sale "Name" [price]   # log a sale, update progress
  python3 execute.py status     # progress dashboard only
  python3 execute.py notify      # fire a macOS notification of the top move
  python3 execute.py text        # print just the artifact text (for piping)
"""

import json
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_PATH = HERE / ".execution_state.json"
TRACKER_PATH = HERE / "outreach-tracker.csv"
BRIEFINGS_DIR = HERE / "briefings"

GUMROAD_URL = "https://sahawat.gumroad.com/l/crossing-session"
FEAR_AUDIT_URL = "https://fear-audit.vercel.app"

GOAL_SALES = 10
PRICE = 97
DEADLINE = date(2026, 7, 17)  # 30 days from launch-agent build (2026-06-17)
DM_TARGET_PER_DAY = 10

# ---------------------------------------------------------------------------
# The finished artifacts — URLs already filled, ready to paste. No more editing.
# ---------------------------------------------------------------------------

EMAILS = {
    "email_1": {
        "subject": "The day I stopped waiting for the traffic to clear",
        "audience": "Encharge tag: Burnout Subscribers (~115 people) — send as a plain-text broadcast from Sahawat (a person, not the brand).",
        "body": f"""Hi {{{{person.firstName | default: "there"}}}},

I want to tell you about the worst part of my own crossing.

It wasn't the leaving. It wasn't the money, and it wasn't telling my family.
It was the two years *before* — the years I spent standing at the curb,
watching the traffic, waiting for a gap that never came.

I had a system, even. I'd tell myself: when the savings hit this number.
When this credential comes through. When things calm down at work.
The number moved. The credential came and I set a new one. Things never
calmed down, because they don't.

What finally moved me wasn't courage. It was arithmetic. I sat down one
evening and wrote out what staying was costing me — not in money, in
mornings. The dread before shifts. The version of myself I was becoming.
When I saw it on paper, waiting stopped looking safe. It was just slower.

I built a 3-minute audit around that exercise. It scores the three fears
that keep people at the curb — money, judgment, identity — and tells you
which one is actually running your decisions. Most people guess wrong
about their own.

Take it here (free, 3 minutes): {FEAR_AUDIT_URL}

Later this week I'll tell you about something I'm opening up for the first
time — for ten people only. But start with the audit. It's the map.

— Sahawat
From the Ward to the World""",
    },
    "email_2": {
        "subject": "I'm opening 10 one-on-one sessions (first time)",
        "audience": "Encharge tag: Burnout Subscribers — same audience as email 1.",
        "body": f"""Hi {{{{person.firstName | default: "there"}}}},

For two years I've written about crossings — the identity cage, the cost of
staying, the fears that keep smart people at the curb. And the most common
reply I get is some version of: "This is exactly me. Now what?"

Fair question. Posts can name your situation. They can't sit with *your*
numbers, *your* license, *your* mortgage, *your* particular fear. So I'm
opening something I haven't offered before:

**The Crossing Session.** One hour, one-on-one, on your actual situation.

Here's the shape of it:

1. Before we talk, you take the 3-minute Fear Audit, so we start from a map
   of which fear is really driving — money, judgment, or identity.
2. On the call, we separate the real risks from the inherited ones, put a
   price on staying, and work out your first concrete step.
3. Within 48 hours you get a one-page Crossing Plan in writing: your
   situation, your constraint, your next three moves.

A few honest caveats. I'm not going to tell you to quit your job — some
people leave this call with a plan to stay, on purpose, with the fear named
and priced. That's a real outcome too. And if you finish the hour with no
more clarity than you came with, tell me and I'll refund every dollar.

I'm taking ten people at the founding rate of $97. After ten,
it goes to $147 and I can't promise when the next batch opens.

Claim a spot: {GUMROAD_URL}

— Sahawat
From the Ward to the World""",
    },
    "email_3": {
        "subject": "What's your curb tax?",
        "audience": "Encharge tag: Burnout Subscribers — same audience. Last call.",
        "body": f"""Hi {{{{person.firstName | default: "there"}}}},

Quick one, and then I'll stop talking about this.

There's a number I ask people to calculate on every Crossing Session.
I call it the curb tax: what one more year of waiting actually costs you.

Not just salary you could be earning elsewhere. The shifts you dread.
The energy your family gets — the version of you they get. The compounding
of one more year of "I'll decide next year," which, as you may have noticed,
has a way of renewing itself automatically.

Nobody's curb tax has ever come out to less than $97.

That's the whole pitch. One hour on your actual situation, a written plan
within 48 hours, full refund if you leave without clarity. The founding
spots are nearly gone, and the price goes to $147 when they are.

Take a spot: {GUMROAD_URL}

And if it's a no — genuinely fine. The Fear Audit stays free
({FEAR_AUDIT_URL}), the posts keep coming, and I'll keep
holding the sign at the crosswalk either way.

— Sahawat
From the Ward to the World""",
    },
}

EMAIL_ORDER = ["email_1", "email_2", "email_3"]
EMAIL_GAP_DAYS = 2  # don't send the next launch email within this many days


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def default_state():
    return {
        "steps": {k: {"done": False, "done_at": None} for k in EMAIL_ORDER},
        "dm_log": {},          # {"YYYY-MM-DD": count}
        "sales": [],           # [{"name": ..., "price": ..., "at": ...}]
        "last_shown_key": None,
        "last_shown_date": None,
    }


def load_state():
    if STATE_PATH.exists():
        data = json.loads(STATE_PATH.read_text())
        base = default_state()
        base.update(data)
        return base
    return default_state()


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def today_str():
    return date.today().isoformat()


def days_left():
    return (DEADLINE - date.today()).days


def days_since(iso):
    if not iso:
        return 999
    then = datetime.fromisoformat(iso).date()
    return (date.today() - then).days


def copy_to_clipboard(text):
    try:
        subprocess.run(["pbcopy"], input=text.encode(), check=True)
        return True
    except Exception:
        return False


def read_today_briefing():
    path = BRIEFINGS_DIR / f"{today_str()}.md"
    if path.exists():
        return path.read_text(), path
    # fall back to the most recent briefing
    files = sorted(BRIEFINGS_DIR.glob("*.md"))
    if files:
        return files[-1].read_text(), files[-1]
    return None, None


def revenue(state):
    return sum(s.get("price", PRICE) for s in state["sales"])


def sales_count(state):
    return len(state["sales"])


def dms_today(state):
    return state["dm_log"].get(today_str(), 0)


# ---------------------------------------------------------------------------
# The decision: what is the single highest-leverage move right now?
# ---------------------------------------------------------------------------

def top_move(state):
    steps = state["steps"]

    # 1. Launch email #1 — biggest single lever, reaches the whole warm list.
    if not steps["email_1"]["done"]:
        e = EMAILS["email_1"]
        return {
            "key": "email_1",
            "kind": "email",
            "title": "Send launch email #1 (the story, no pitch)",
            "why": "One paste reaches ~115 warm subscribers. It was scheduled Jun 12 and never went out. Nothing else you can do today comes close to this leverage.",
            "destination": "Encharge → Broadcasts → new plain-text broadcast",
            "audience": e["audience"],
            "subject": e["subject"],
            "artifact": e["body"],
        }

    # 2/3. Follow-up launch emails, spaced out.
    for prev, cur in (("email_1", "email_2"), ("email_2", "email_3")):
        if not steps[cur]["done"]:
            gap = days_since(steps[prev]["done_at"])
            if gap >= EMAIL_GAP_DAYS:
                e = EMAILS[cur]
                return {
                    "key": cur,
                    "kind": "email",
                    "title": f"Send launch {cur.replace('_', ' ')} — {e['subject']}",
                    "why": f"Email {prev[-1]} went out {gap} days ago. The sequence converts on the offer + last-call emails, not the story alone.",
                    "destination": "Encharge → Broadcasts → new plain-text broadcast",
                    "audience": e["audience"],
                    "subject": e["subject"],
                    "artifact": e["body"],
                }
            break  # next email isn't due yet → fall through to DMs

    # 4. Daily 1:1 outreach from the warm briefing.
    briefing, path = read_today_briefing()
    done_today = dms_today(state)
    remaining = max(0, DM_TARGET_PER_DAY - done_today)
    first_draft = extract_first_draft(briefing) if briefing else None
    return {
        "key": f"dm:{today_str()}",
        "kind": "dm",
        "title": f"Send {remaining} personalized openers to warm leads ({done_today}/{DM_TARGET_PER_DAY} done today)",
        "why": "The launch emails are out. Now it's daily 1:1 reps with people already showing intent. This is where the sessions actually close.",
        "destination": f"Email or LinkedIn DM — drafts in {path.name if path else 'briefings/'}",
        "audience": None,
        "subject": None,
        "artifact": first_draft or "No briefing found. Run: python3 outreach-briefing.py",
        "briefing_path": str(path) if path else None,
    }


# Owner / test rows that the briefing sometimes includes — never outreach targets.
_DM_SKIP = ("toto", "sahawat", "welyfe", "example.com")
_DM_SKIP_NAMES = {"me", "toto", "test"}


def _is_owner_row(name, email):
    n = (name or "").strip().lower()
    e = (email or "").strip().lower()
    return n in _DM_SKIP_NAMES or any(x in e for x in _DM_SKIP)


def extract_first_draft(briefing_text):
    """First real '- **Draft:**' in today's briefing, skipping owner/test rows."""
    name = email = None
    for line in briefing_text.splitlines():
        s = line.strip()
        if s.startswith("### "):
            head = s[4:].split("—")
            name = head[0].strip()
            email = head[1].strip() if len(head) > 1 else None
        elif "**Draft:**" in s:
            draft = s.split("**Draft:**", 1)[1].strip()
            if _is_owner_row(name, email):
                name = email = None
                continue
            return f"To: {name} <{email}>\n\n{draft}" if name else draft
    return None


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

BAR_W = 24


def progress_bar(done, total):
    filled = int(BAR_W * min(done, total) / total) if total else 0
    return "█" * filled + "░" * (BAR_W - filled)


def render_status(state):
    sc, rev, dl = sales_count(state), revenue(state), days_left()
    need = max(0, GOAL_SALES - sc)
    pace = f"{need / dl:.1f} sales/day" if dl > 0 else "DEADLINE PASSED"
    lines = [
        "",
        "  CROSSING SESSION  →  $1,000 in 30 days",
        "  " + "─" * 44,
        f"  Sales    {progress_bar(sc, GOAL_SALES)}  {sc}/{GOAL_SALES}",
        f"  Revenue  ${rev}  /  ${GOAL_SALES * PRICE}",
        f"  Days left: {dl}    Need: {need} more    Pace: {pace}",
        f"  Outreach today: {dms_today(state)}/{DM_TARGET_PER_DAY}",
        "",
    ]
    return "\n".join(lines)


def render_move(move, state, escalate):
    out = [render_status(state)]
    if escalate:
        out += [
            "  ⚠  You were shown this exact move last time and skipped it.",
            "     This is the single thing between you and the next sale.",
            "",
        ]
    out += [
        "  ▶ TODAY'S ONE MOVE",
        "  " + "─" * 44,
        f"  {move['title']}",
        "",
        f"  Why: {move['why']}",
        "",
        f"  Where: {move['destination']}",
    ]
    if move.get("audience"):
        out.append(f"  Audience: {move['audience']}")
    if move.get("subject"):
        out.append(f"  Subject: {move['subject']}")
    out += [
        "",
        "  ── PASTE THIS (already on your clipboard) " + "─" * 8,
        "",
    ]
    for line in move["artifact"].splitlines():
        out.append("  " + line)
    out += [
        "",
        "  " + "─" * 44,
    ]
    if move["kind"] == "email":
        out += [
            "  When sent:   python3 execute.py done",
            "  When a sale lands:   python3 execute.py sale \"First name\"",
        ]
    else:
        out += [
            "  After each send:   python3 execute.py dm 1",
            "  When a sale lands: python3 execute.py sale \"First name\"",
            f"  Full draft list:   open {move.get('briefing_path', 'briefings/')}",
        ]
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_show(state):
    move = top_move(state)
    escalate = (
        state.get("last_shown_key") == move["key"]
        and state.get("last_shown_date") not in (None, today_str())
    )
    copied = copy_to_clipboard(move["artifact"])
    print(render_move(move, state, escalate))
    if not copied:
        print("  (clipboard copy unavailable — copy the block above manually)\n")
    state["last_shown_key"] = move["key"]
    state["last_shown_date"] = today_str()
    save_state(state)


def cmd_done(state):
    move = top_move(state)
    if move["kind"] != "email":
        print("  Top move isn't an email step. Use: python3 execute.py dm <n>")
        return
    state["steps"][move["key"]]["done"] = True
    state["steps"][move["key"]]["done_at"] = today_str()
    save_state(state)
    print(f"  ✓ Marked done: {move['title']}\n")
    cmd_show(state)


def cmd_dm(state, n):
    state["dm_log"][today_str()] = dms_today(state) + n
    save_state(state)
    print(f"  ✓ Logged {n} outreach message(s). Today: {dms_today(state)}/{DM_TARGET_PER_DAY}\n")
    cmd_show(state)


def cmd_sale(state, name, price):
    state["sales"].append({
        "name": name,
        "price": price,
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    save_state(state)
    sc, rev = sales_count(state), revenue(state)
    print(f"\n  🎉 SALE #{sc}: {name} — ${price}.  Total: ${rev}/${GOAL_SALES * PRICE}.")
    if sc >= GOAL_SALES:
        print("  🏁 You hit 10. Founding rate closes — raise the price to $147.\n")
    else:
        print(f"  {GOAL_SALES - sc} to go.\n")


def cmd_notify(state):
    move = top_move(state)
    title = "Crossing Session — today's one move"
    msg = move["title"].replace('"', "'")
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification "{msg}" with title "{title}"'],
            check=True,
        )
    except Exception as e:
        print(f"  notify failed: {e}")


def main():
    state = load_state()
    args = sys.argv[1:]
    if not args or args[0] == "show":
        cmd_show(state)
    elif args[0] == "status":
        print(render_status(state))
    elif args[0] == "done":
        cmd_done(state)
    elif args[0] == "dm":
        cmd_dm(state, int(args[1]) if len(args) > 1 else 1)
    elif args[0] == "sale":
        if len(args) < 2:
            print('  Usage: python3 execute.py sale "First name" [price]')
            return
        price = int(args[2]) if len(args) > 2 else PRICE
        cmd_sale(state, args[1], price)
    elif args[0] == "notify":
        cmd_notify(state)
    elif args[0] == "text":
        print(top_move(state)["artifact"])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
