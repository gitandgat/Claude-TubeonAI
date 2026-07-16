"""
Resumable cold-connection drip for the grassroots health-coach freelance list.

Sends N LinkedIn connection requests/day via SendPilot (/inbox/connect), with the
approved "peer / no agenda" note, rendering each lead's first name. Tracks state
in the leads JSON (connect_sent + connect_date) so it resumes across days and
never double-sends. Safe to re-run.

    python3 freelance-leads/connect_drip.py            # send next 20
    python3 freelance-leads/connect_drip.py --n 25     # custom batch
    python3 freelance-leads/connect_drip.py --dry-run  # preview only

After leads accept, follow up with a DM (separate step, approved copy).
"""

import argparse
import json
import os
import re
import sys
import time

SKILL = "/Users/toto/.claude/skills/sendpilot-outreach"
sys.path.insert(0, SKILL)

# Load the repo .env explicitly (works regardless of cwd, e.g. under launchd)
# BEFORE importing the client, whose SP() reads SENDPILOT_API_KEY at init.
from dotenv import load_dotenv  # noqa: E402
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
from sendpilot import SP  # noqa: E402

LEADS_FILE = os.path.join(os.path.dirname(__file__), "health-coaches-2026-06-21.json")

NOTE = ("Hi {fn}, fellow health-world person here — former physician. I like "
        "connecting with coaches and practitioners building something of their "
        "own. No agenda, just good people to know in this space.")

# Credential tokens that show up in the first_name field instead of a real name.
CREDS = {"msc", "mcc", "phd", "nbc", "nc", "rd", "rdn", "fntp", "ms", "ma",
         "dr", "dc", "np", "pa", "rn", "lcsw", "nbc-hwc", "cnc", "ihp"}


def clean_first_name(raw: str) -> str:
    """Return a usable first name, or 'there' if the field is junk/credentials."""
    if not raw:
        return "there"
    name = re.sub(r"[^A-Za-z'\-]", "", raw).strip("-'")
    if not name or name.lower() in CREDS:
        return "there"
    if name.isupper() and len(name) <= 4:  # e.g. 'MCC', 'NBC' -> credential
        return "there"
    return name.title() if name.isupper() else name  # 'SMITHA' -> 'Smitha'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=15, help="connections to send")
    ap.add_argument("--sleep", type=float, default=12.0, help="seconds between sends")
    ap.add_argument("--note", action="store_true",
                    help="attach the note (LinkedIn Premium only; 500s otherwise)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(LEADS_FILE) as f:
        leads = json.load(f)

    # Daily quota guard: a manual run and the launchd run on the same day
    # share the N/day budget instead of stacking (LinkedIn invite pacing).
    today = time.strftime("%Y-%m-%d")
    sent_today = sum(1 for l in leads
                     if l.get("connect_sent") and l.get("connect_date") == today)
    budget = max(0, args.n - sent_today)
    if sent_today:
        print(f"{sent_today} connects already sent today; budget now {budget}")

    pending = [l for l in leads if not l.get("connect_sent")]
    batch = pending[:budget]
    print(f"{len(leads)} total | {len(pending)} not yet contacted | "
          f"sending {len(batch)} this run{' (DRY RUN)' if args.dry_run else ''}\n")

    if not args.dry_run:
        s = SP().senders()[0]
        print(f"Sender: {s['name']} — {s['remainingMessages']}/{s['dailyMessageLimit']} left today\n")

    sp = SP()
    sent = errors = consecutive_errors = 0
    for i, lead in enumerate(batch):
        fn = clean_first_name(lead.get("first_name", ""))
        # Note-less by default: LinkedIn gates invite notes to Premium and
        # SendPilot 500s on note-bearing connects for non-Premium senders.
        note = NOTE.format(fn=fn) if args.note else ""
        url = lead.get("linkedin_url")
        who = f"{lead.get('full_name','?')} ({lead.get('company','—')})"
        if args.dry_run:
            print(f"  · would connect → {who}" + (f"\n    {note}" if note else " (no note)"))
            continue
        try:
            sp.send_connection(url, message=note)
            lead["connect_sent"] = True
            lead["connect_date"] = time.strftime("%Y-%m-%d")
            sent += 1
            consecutive_errors = 0
            print(f"  ✓ {who}")
        except Exception as e:
            body = e.response.text[:120] if getattr(e, "response", None) is not None else str(e)
            errors += 1
            consecutive_errors += 1
            print(f"  ✗ {who} — {body}")
            if consecutive_errors >= 3:
                # 500s here mean LinkedIn is throttling invites — hammering the
                # rest of the batch risks the account. Stop; tomorrow's run resumes.
                print("\n  3 consecutive errors — LinkedIn likely throttling; aborting batch.")
                break
        if i < len(batch) - 1:
            time.sleep(args.sleep)

    if not args.dry_run:
        with open(LEADS_FILE, "w") as f:
            json.dump(leads, f, indent=2)
        remaining = sum(1 for l in leads if not l.get("connect_sent"))
        print(f"\nDONE: {sent} sent, {errors} errors. {remaining} leads left for future runs.")


if __name__ == "__main__":
    main()
