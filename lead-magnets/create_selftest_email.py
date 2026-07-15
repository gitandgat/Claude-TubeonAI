#!/usr/bin/env python3
"""Create the MoveAssess Self-Test delivery email (front-door lead magnet).

Trigger (assemble in Encharge UI): tag `moveassess-selftest` -> send this email.
It delivers the 60-Second Movement Self-Test PDF and bridges to the full
assessment + nurture. Built via the sanctioned crosswalk-encharge-email helper.
"""

import sys
from pathlib import Path

SKILL_DIR = Path.home() / ".claude" / "skills" / "crosswalk-encharge-email"
sys.path.insert(0, str(SKILL_DIR))

from encharge_email import button, create_email, link, p  # noqa: E402

APP = "https://physical-assessment-app.vercel.app"
SELFTEST_PDF = f"{APP}/movement-self-test.pdf"
PROGRAM = "https://glute.crosswalkwisdom.com"
FIRST = "{{ person.firstName | default: 'there' }}"

BODY = (
    p(f"Hey {FIRST},")
    + p(
        "Here's your <strong>60-Second Movement Self-Test</strong> — seven checks "
        "a clinician uses to find where a body will break down first. A wall, a "
        "chair, a mirror. That's all you need."
    )
    + button(SELFTEST_PDF, "Download the Self-Test (PDF)")
    + p(
        "Do all seven and count your tells. Fewer than three, you're moving well. "
        "<strong>Three or more, you're carrying movement debt</strong> — and it "
        "compounds every year you leave it."
    )
    + p(
        "Once you know you have a tell, the obvious next question is <em>which</em> "
        "pattern is yours. That's what the free assessment is for: "
        + link(APP, "it shows you the exact pattern in 3D")
        + " — the muscles that have gone quiet, the ones compensating — and sends "
        "you the corrective protocol built for it. Do it for 14 days, then retest."
    )
    + p(
        "That retest is the whole point. This is a measurement system, not a "
        "stretching routine."
    )
    + p(
        "— Sahawat"
    )
)


def main() -> int:
    eid = create_email(
        name="MoveAssess Self-Test — Delivery",
        subject="Your 60-Second Movement Self-Test (inside)",
        body_html=BODY,
    )
    print(f"Created + verified email {eid}")
    print("Encharge UI: trigger tag `moveassess-selftest` -> send this email.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
