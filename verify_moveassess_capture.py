#!/usr/bin/env python3
"""Re-verify the MoveAssess capture funnel plumbing end-to-end.

Fires a live capture through the deployed Vercel endpoint, then reads the
person back from Encharge to confirm the moveassess-lead tag + case fields.
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

API_KEY = os.environ["ENCHARGE_API_KEY"]
BASE = "https://api.encharge.io/v1"
HEADERS = {"X-Encharge-Token": API_KEY}
LIVE_ENDPOINT = "https://physical-assessment-app.vercel.app/api/capture"
TEST_EMAIL = "totomakus+moveassess-test@gmail.com"
TEST_CASE = "gluteal-inhibition"


def main() -> int:
    r = requests.post(
        LIVE_ENDPOINT,
        json={
            "email": TEST_EMAIL,
            "caseId": TEST_CASE,
            "caseName": "Gluteal Inhibition (Underactive Glutes)",
        },
        timeout=30,
    )
    print(f"live capture: HTTP {r.status_code} — {r.text[:200]}")
    if not r.ok:
        return 1

    r = requests.get(
        f"{BASE}/people", headers=HEADERS, params={"people[0][email]": TEST_EMAIL}
    )
    users = (r.json() if r.ok else {}).get("users") or []
    if not users:
        print(f"person lookup failed: HTTP {r.status_code} — {r.text[:300]}")
        return 1

    person = users[0]
    print(f"person found: {person.get('email')}")
    print(f"  tags: {person.get('tags')}")
    print(f"  case: {person.get('moveassessCase')} / {person.get('moveassessCaseName')}")
    ok = (
        "moveassess-lead" in str(person.get("tags") or "")
        and person.get("moveassessCase") == TEST_CASE
    )
    print("VERIFIED" if ok else "INCOMPLETE — check tag/field wiring")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
