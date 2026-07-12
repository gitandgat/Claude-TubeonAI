"""
Daily outreach briefing — the safe half of "DM automation".

Pulls from Encharge everyone who showed a buying signal in the last 48h
(new subscribers, quiz takers, tracker users) and drafts a personalized
opener for each, ready to review and send by hand.

Output: CROSSING-SESSION-LAUNCH/briefings/YYYY-MM-DD.md

Run every morning:  python3 outreach-briefing.py
Look back further:  python3 outreach-briefing.py --hours 96
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["ENCHARGE_API_KEY"]
BASE = "https://api.encharge.io/v1"
HEADERS = {"X-Encharge-Token": API_KEY}

BRIEFING_DIR = Path(__file__).parent / "CROSSING-SESSION-LAUNCH" / "briefings"

# Own/test addresses — never outreach targets
EXCLUDED_EMAILS = {
    "totomakus@gmail.com",
    "toto_makus@hotmail.com",
    "sahawat.nil@gmail.com",
    "sahawat@crosswalkwisdom.com",
}
EXCLUDED_DOMAINS = {"example.com", "crosswalkwisdom.com"}

FEAR_OPENERS = {
    "Financial Insecurity": (
        "Saw you took the Fear Audit — money fear scored highest for you. "
        "That one's sneaky because it disguises itself as being responsible. "
        "Did the result match what you expected?"
    ),
    "Fear of Judgment": (
        "Saw you took the Fear Audit — judgment came out as your loudest fear. "
        "In my experience that one belongs to a handful of specific faces, not "
        "'people' in general. Did the result surprise you?"
    ),
    "Identity Loss": (
        "Saw you took the Fear Audit — identity scored highest for you. That's "
        "the deepest of the three: it's not 'what will I do,' it's 'who will I "
        "be.' Did the result match what you expected?"
    ),
}

NEW_SUB_OPENER = (
    "Thanks for subscribing — most people land here from a post about the "
    "identity cage or the cost of staying. Which one hit for you? And what's "
    "your situation — weighing a move, or already mid-crossing?"
)

TRACKER_OPENER = (
    "Saw you used the sunk-cost tracker. That number on the screen usually "
    "stings the first time. Mind if I ask what it came out to — and how long "
    "you've been carrying it?"
)


def get_field(p: dict, key: str):
    return p.get(key) or (p.get("person") or {}).get(key)


def fetch_recent_people(hours: int) -> dict[str, dict]:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    found: dict[str, dict] = {}
    offset = 0
    while True:
        r = requests.get(
            f"{BASE}/people/all", params={"limit": 100, "offset": offset},
            headers=HEADERS, timeout=20,
        )
        r.raise_for_status()
        batch = r.json().get("people", [])
        if not batch:
            break
        for p in batch:
            email = (get_field(p, "email") or "").strip().lower()
            if not email or email in EXCLUDED_EMAILS:
                continue
            if email.rsplit("@", 1)[-1] in EXCLUDED_DOMAINS:
                continue
            seen = max(p.get("createdAt") or "", p.get("lastActivity") or "")
            if seen < cutoff:
                continue
            merged = found.setdefault(email, {"email": email, "seen": seen})
            merged["seen"] = max(merged["seen"], seen)
            for key in ("firstName", "fearType", "financialScore", "judgmentScore", "identityScore"):
                value = get_field(p, key)
                if value not in (None, ""):
                    merged[key] = value
            tags = p.get("tags") or ""
            tag_list = [t.strip() for t in tags.split(",") if t.strip()] if isinstance(tags, str) else tags
            merged.setdefault("tags", set()).update(tag_list)
        offset += 100
        if offset > 5000:
            break
    return found


def draft_for(person: dict) -> tuple[str, str]:
    """Return (signal label, draft opener)."""
    tags = person.get("tags", set())
    if person.get("fearType"):
        opener = FEAR_OPENERS.get(person["fearType"], FEAR_OPENERS["Identity Loss"])
        return f"quiz taker — {person['fearType']}", opener
    if "tracker-sunk-cost" in tags:
        return "sunk-cost tracker user", TRACKER_OPENER
    return "new subscriber", NEW_SUB_OPENER


def main() -> None:
    hours = 48
    if "--hours" in sys.argv:
        hours = int(sys.argv[sys.argv.index("--hours") + 1])

    people = fetch_recent_people(hours)
    today = datetime.now().strftime("%Y-%m-%d")
    BRIEFING_DIR.mkdir(parents=True, exist_ok=True)
    out = BRIEFING_DIR / f"{today}.md"

    lines = [
        f"# Outreach briefing — {today}",
        "",
        f"Encharge signals from the last {hours}h: **{len(people)} people**.",
        "Review each draft, make it yours, send, then log in outreach-tracker.csv.",
        "",
        "## Encharge signals (email or LinkedIn DM if you can find them)",
        "",
    ]

    if not people:
        lines.append("_No new Encharge signals in this window._")
    for person in sorted(people.values(), key=lambda x: x["seen"], reverse=True):
        signal, draft = draft_for(person)
        name = person.get("firstName") or "(no name)"
        lines += [
            f"### {name} — {person['email']}",
            f"- **Signal:** {signal} ({person['seen'][:16]})",
            f"- **Draft:** {draft}",
            "",
        ]

    lines += [
        "## Manual sources (fill your 10)",
        "",
        "- [ ] LinkedIn notifications: list everyone who commented/reacted in 48h",
        "- [ ] Replies to launch emails (warmest people on this list)",
        "- [ ] New members of your Facebook group — welcome them by name",
        "- [ ] One adjacent creator's burnout post: 2-3 thoughtful commenters",
        "",
        "Openers for these scenarios: CROSSING-SESSION-LAUNCH/outreach-kit.md",
    ]

    out.write_text("\n".join(lines))
    print(f"Briefing written: {out}")
    print(f"  {len(people)} Encharge signals in last {hours}h")


if __name__ == "__main__":
    main()
