"""
One-shot activation reminder (Jun 16). Checks the two pending activations and
the morning briefing, writes a status file, and fires a macOS notification.

Fired by launchd job com.crosswalk.activationcheck on Jun 16 ~9am, then the
plist self-unloads so it doesn't nag again.

Run manually any time: python3 activation_check.py
"""

import glob
import os
import subprocess
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

H = {"X-Encharge-Token": os.environ["ENCHARGE_API_KEY"]}
QUIZ_TAKERS = [
    "omololaonamusi@gmail.com", "sonjams123@gmail.com", "tasique@gmail.com",
    "ajay@calmstudio.in", "afshan.m.samee@gmail.com", "swati0648@gmail.com",
]
EXCLUDE = {"totomakus@gmail.com", "toto_makus@hotmail.com", "sahawat.nil@gmail.com"}
EXCLUDE_DOMAINS = {"example.com", "test.com", "crosswalkwisdom.com"}
HERE = os.path.dirname(os.path.abspath(__file__))


def check_quiz_followup() -> tuple[bool, str]:
    """The 6 quiz-takers were enrolled into the live crossing-launch offer flow
    (story -> $97 offer -> last call), not the dedicated quiz-followup email."""
    enrolled = 0
    for email in QUIZ_TAKERS:
        r = requests.get(
            "https://api.encharge.io/v1/people",
            params={"people[0][email]": email}, headers=H, timeout=15,
        )
        u = (r.json().get("users") or [{}])[0]
        if "crossing-launch" in (u.get("tags") or ""):
            enrolled += 1
    if enrolled == len(QUIZ_TAKERS):
        return True, f"✅ 6 quiz-takers in offer flow ({enrolled}/6) — getting story → $97 offer → last call."
    return False, (
        f"⏳ Only {enrolled}/6 quiz-takers enrolled. Re-run the crossing-launch tagging."
    )


def check_cold_capture() -> tuple[bool, str]:
    seen = {}
    offset = 0
    while True:
        r = requests.get(
            "https://api.encharge.io/v1/people/all",
            params={"limit": 100, "offset": offset}, headers=H, timeout=20,
        )
        batch = r.json().get("people", [])
        if not batch:
            break
        for p in batch:
            e = (p.get("email") or (p.get("person") or {}).get("email") or "").strip().lower()
            if not e or e in EXCLUDE or e.rsplit("@", 1)[-1] in EXCLUDE_DOMAINS:
                continue
            seen[e] = max(seen.get(e, ""), p.get("createdAt") or "")
        offset += 100
        if offset > 5000:
            break
    new = [e for e, c in seen.items() if c >= "2026-06-15"]
    if new:
        return True, f"✅ Capture working — {len(new)} new signup(s) since Jun 15. (Fear Audit auto-posts in every post's first comment — zero wiring.)"
    return False, (
        "ℹ️ No new signups yet — normal early on. Capture is fully automatic now "
        "(Fear Audit link in every post's first comment). Optional: pin ONE "
        "'Comment FEAR' post and wire it once in Sendpilot for the DM path."
    )


def latest_briefing() -> str:
    files = sorted(glob.glob(os.path.join(HERE, "CROSSING-SESSION-LAUNCH", "briefings", "*.md")))
    return os.path.basename(files[-1]) if files else "(none yet — runs 7am daily)"


def main() -> None:
    ok1, msg1 = check_quiz_followup()
    ok2, msg2 = check_cold_capture()
    briefing = latest_briefing()

    report = (
        f"CROSSWALK ACTIVATION CHECK — {datetime.now():%Y-%m-%d %H:%M}\n\n"
        f"1. {msg1}\n\n2. {msg2}\n\n"
        f"3. 📋 Work today's warm briefing: CROSSING-SESSION-LAUNCH/briefings/{briefing}\n"
        "   Open it, send a few genuine 1:1 replies, log in outreach-tracker.csv.\n"
    )
    out = os.path.join(HERE, "CROSSING-SESSION-LAUNCH", "ACTIVATION-STATUS.txt")
    with open(out, "w") as f:
        f.write(report)
    print(report)

    pending = sum(1 for ok in (ok1, ok2) if not ok)
    summary = "All live ✓ — just work the briefing" if pending == 0 else f"{pending} activation(s) still pending"
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{summary}" with title "Crosswalk: morning check" sound name "Glass"'],
            check=False,
        )
    except Exception:
        pass


if __name__ == "__main__":
    main()
