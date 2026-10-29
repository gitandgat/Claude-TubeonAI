"""
Create + prep the quiz-taker follow-up email in Encharge.

- Creates one warm, reply-driving email asset (richtext, nested editor format).
- Tags the 6 quiz-takers who are NOT already in the crossing-launch flow
  (avoids double-emailing the 2 who get today's offer broadcast).
- Send mechanism: user activates a 1-step flow (trigger: tag 'quiz-followup'
  -> send this email), same proven pattern as the launch flow.

Run: python3 create_quiz_followup_email.py
"""

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["ENCHARGE_API_KEY"]
BASE = "https://api.encharge.io/v1"
HEADERS = {"X-Encharge-Token": API_KEY, "Content-Type": "application/json"}

ACCOUNT_ID = 156229
COMMUNICATION_CAT_ID = 289738
FROM_EMAIL = "sahawat@crosswalkwisdom.com"
FROM_NAME = "Sahawat at Crosswalk Wisdom"
LOGO_URL = "https://d231yrez0cpae9.cloudfront.net/1750037512272-Crosswalk%20wisdom%20logo%20white%20BG.png"
SESSION_URL = "https://sahawat.gumroad.com/l/crossing-session"

FOLLOWUP_TAG = "quiz-followup"

# 6 quiz-takers NOT in crossing-launch (Ceinwen + Emile excluded — already in flow)
TARGETS = [
    "omololaonamusi@gmail.com",
    "sonjams123@gmail.com",
    "tasique@gmail.com",
    "ajay@calmstudio.in",
    "afshan.m.samee@gmail.com",
    "swati0648@gmail.com",
]

P = '<p style="font-family: Georgia, serif; font-size: 16px; line-height: 180%; color: #1A1917;">'
E = "</p>"

BODY = (
    f'<p style="text-align:center;padding:16px 0;"><img src="{LOGO_URL}" alt="Crosswalk Wisdom" width="150" style="max-width:150px;"></p>'
    f'{P}Hi {{{{ person.firstName | default: "there" }}}},{E}'
    f"{P}A little while ago you took the Fear Audit. I read every result that "
    f"comes through, and yours stuck with me.{E}"
    f"{P}Here's the part most people miss: knowing which fear scores highest is "
    f"the easy bit. The hard part is that the fear never feels like fear. It "
    f"feels like being responsible. Or realistic. Or loyal. That disguise is "
    f"exactly what keeps good people standing at the curb for years.{E}"
    f"{P}So I'm curious — when you saw your result, did it match what you "
    f"expected? Or did it name something you'd quietly been talking yourself "
    f"out of?{E}"
    f"{P}Just hit reply. These come to me, and I answer them myself.{E}"
    f"{P}&mdash; Sahawat{E}"
    f'<p style="font-family: Georgia, serif; font-size: 14px; color: #888888;">'
    f"P.S. If you'd rather not wait, I'm opening ten one-on-one "
    f'<a href="{SESSION_URL}" style="color:#2C5F4A;">Crossing Sessions</a> at a '
    f"founding rate — one hour on your actual situation, with a written plan "
    f"after. But a reply to this email is a perfectly good place to start.</p>"
    f'<p style="text-align:center;font-size:13px;color:#95a5a6;font-family:Georgia,serif;">'
    f"Crosswalk Wisdom<br>{{{{account.mailingAddress}}}}<br>"
    f"{{{{person.unsubscribeLink}}}}</p>"
)


def create_email() -> int | None:
    payload = {
        "name": "Quiz Follow-up — Jun 14",
        "subject": "The fear you scored highest on — one question",
        "fromEmail": FROM_EMAIL,
        "fromName": FROM_NAME,
        "replyTo": FROM_EMAIL,
        "accountId": ACCOUNT_ID,
        "communicationCategoryId": COMMUNICATION_CAT_ID,
        "editor": {"type": "richtext", "state": BODY},
    }
    r = requests.post(f"{BASE}/emails", headers=HEADERS, json=payload, timeout=30)
    if r.status_code in (200, 201):
        eid = r.json().get("email", {}).get("id") or r.json().get("id")
        print(f"  email created -> ID {eid}")
        return eid
    print(f"  FAILED to create email: {r.status_code} {r.text[:200]}")
    return None


def tag_targets() -> None:
    for email in TARGETS:
        r = requests.post(
            f"{BASE}/tags", json={"tag": FOLLOWUP_TAG, "email": email},
            headers=HEADERS, timeout=20,
        )
        print(f"  tag {FOLLOWUP_TAG} -> {email}: {r.status_code}")
        time.sleep(0.3)


if __name__ == "__main__":
    import sys

    if "--tag" in sys.argv:
        # Step 2: run ONLY after the flow is built + activated, or the tag-add
        # event fires into nothing and won't re-trigger.
        print(f"Tagging {len(TARGETS)} quiz-takers with '{FOLLOWUP_TAG}' (fires the flow)...")
        tag_targets()
        print("\nDONE — flow should now be sending to all 6.")
    else:
        # Step 1: safe, sends nothing.
        print("Creating quiz follow-up email asset (nothing is sent)...")
        eid = create_email()
        print(
            f"\nEmail asset ready (ID {eid}). NOTHING SENT YET.\n"
            "NEXT (you, 2 clicks): Encharge -> Flows -> new flow,\n"
            "  trigger 'Tag added: quiz-followup' -> Send email 'Quiz Follow-up — Jun 14'"
            f" (ID {eid}) -> Activate.\n"
            "THEN tell me 'follow-up flow live' and I run: python3 create_quiz_followup_email.py --tag\n"
            "(tagging must come AFTER activation or it won't fire — same as the launch flow)."
        )
