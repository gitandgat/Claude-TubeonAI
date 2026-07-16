"""
Enroll Burnout Subscribers into the Crossing Session launch flow.

Adds the tag `crossing-launch` to every person tagged `Burnout Subscribers`,
which triggers the flow (emails 461554 -> 461555 -> 461556).

ONLY RUN AFTER the flow is built and ACTIVATED in Encharge,
otherwise the tag fires into nothing and re-tagging won't re-trigger.

Usage:
  python3 tag-crossing-launch.py --dry-run   # list who would be tagged
  python3 tag-crossing-launch.py             # tag them (asks for confirmation)
"""

import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["ENCHARGE_API_KEY"]
BASE = "https://api.encharge.io/v1"
HEADERS = {"X-Encharge-Token": API_KEY, "Content-Type": "application/json"}

SOURCE_TAG = "Burnout Subscribers"
LAUNCH_TAG = "crossing-launch"


def extract_email(p: dict) -> str:
    """Email lives at top level or nested under 'person' for merged records."""
    return (p.get("email") or (p.get("person") or {}).get("email") or "").strip().lower()


def fetch_burnout_subscribers() -> list[str]:
    """Return deduplicated emails of source-tag people not yet enrolled."""
    emails, offset = {}, 0
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
            email = extract_email(p)
            if not email:
                continue
            tags = p.get("tags") or ""
            tag_list = [t.strip() for t in tags.split(",")] if isinstance(tags, str) else tags
            already = emails.get(email, {"source": False, "launch": False})
            emails[email] = {
                "source": already["source"] or SOURCE_TAG in tag_list,
                "launch": already["launch"] or LAUNCH_TAG in tag_list,
            }
        offset += 100
        if offset > 5000:
            break
    return [e for e, flags in emails.items() if flags["source"] and not flags["launch"]]


def add_launch_tag(email: str) -> bool:
    r = requests.post(
        f"{BASE}/tags", json={"tag": LAUNCH_TAG, "email": email},
        headers=HEADERS, timeout=20,
    )
    return r.status_code in (200, 201)


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    emails = fetch_burnout_subscribers()
    print(f"{len(emails)} unique '{SOURCE_TAG}' people without '{LAUNCH_TAG}'\n")

    if dry_run:
        for e in emails[:10]:
            print(f"  would tag: {e}")
        if len(emails) > 10:
            print(f"  ... and {len(emails) - 10} more")
        return

    answer = input(f"Tag {len(emails)} people with '{LAUNCH_TAG}' and start the flow? [yes/no] ")
    if answer.strip().lower() != "yes":
        print("Aborted.")
        return

    ok, failed = 0, 0
    for email in emails:
        if add_launch_tag(email):
            ok += 1
        else:
            failed += 1
            print(f"  FAILED: {email}")
        time.sleep(0.3)

    print(f"\nDone: {ok} enrolled, {failed} failed")


if __name__ == "__main__":
    main()
