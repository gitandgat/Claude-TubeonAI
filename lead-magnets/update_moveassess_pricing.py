#!/usr/bin/env python3
"""Add confirmed pricing ($97 founding / $147 list) to MoveAssess E5 + E7.

E5 = 467332 (offer intro), E7 = 467334 (retest close). Uses the sanctioned
crosswalk-encharge-email helper (self-verifying updates).
"""

import sys
from pathlib import Path

SKILL_DIR = Path.home() / ".claude" / "skills" / "crosswalk-encharge-email"
sys.path.insert(0, str(SKILL_DIR))

from encharge_email import button, link, p, update_email  # noqa: E402

APP = "https://physical-assessment-app.vercel.app"
PROGRAM = "https://glute.crosswalkwisdom.com"
FIRST = "{{ person.firstName | default: 'there' }}"
CASE = "{{ person.moveassessCaseName | default: 'your movement pattern' }}"

E5_SUBJECT = "The protocol fixes the pattern. This keeps it fixed."
E5_BODY = (
    p(f"Hey {FIRST},")
    + p(
        "The 14-day protocol does one job: it corrects "
        f"<strong>{CASE}</strong>. But a corrected pattern that never "
        "gets loaded goes right back to sleep. The question after the "
        "retest isn't \"did it work\" — it's \"what keeps it working "
        "for the next 20 years?\""
    )
    + p("That's the job of the <strong>Glute Longevity program</strong>:")
    + p(
        "• Progressive training built on the same clinical logic as "
        "your protocol — 15 minutes a day, no gym required<br>"
        "• The full corrective library, programmed for you instead of "
        "self-managed<br>"
        "• Nutrition support for the muscle you're building<br>"
        "• The retest loop built in, so progress is measured, not felt"
    )
    + p(
        "<strong>Founding-cohort pricing:</strong> the program is $147. "
        "The first cohort joins at <strong>$97</strong> — in exchange, I ask "
        "for your day-30 retest result and honest feedback. When the founding "
        "cohort fills, the price goes to $147 and stays there."
    )
    + button(PROGRAM, "Join the Founding Cohort — $97")
    + p(
        "It's built by a former physician for one specific outcome: moving at "
        "70 the way you did at 40. And it's covered by the measurement you "
        "already trust: retest at day 30 — if your pattern hasn't measurably "
        "improved, full refund."
    )
)

E7_SUBJECT = "Run the retest, then decide"
E7_BODY = (
    p(f"Hey {FIRST},")
    + p(
        "It's been about two weeks since you found "
        f"<strong>{CASE}</strong>. Time to close the loop:"
    )
    + p(
        "<strong>1.</strong> "
        + link(APP, "Run the assessment again")
        + ". Same test, honest look."
    )
    + p(
        "<strong>2.</strong> If the pattern improved — the protocol worked, "
        "and you've proven your body still adapts. That's exactly the "
        "adaptation the Glute Longevity program is built to compound, year "
        "after year."
    )
    + p(
        "<strong>3.</strong> If it didn't improve — in my experience that's "
        "almost never the protocol. It's consistency without structure. Ten "
        "minutes \"when I remember\" isn't a dose. Programming and "
        "accountability are precisely what the program adds."
    )
    + p(
        "Either result points the same direction. Here are the exact terms, "
        "so you can decide cleanly:"
    )
    + p(
        "• <strong>$97 founding-cohort price</strong> — $147 once the first "
        "cohort fills<br>"
        "• 15 minutes a day, no gym required<br>"
        "• <strong>The guarantee:</strong> retest at day 30. If your pattern "
        "hasn't measurably improved, full refund — the same free assessment "
        "you've already used is the referee."
    )
    + button(PROGRAM, "Join the Founding Cohort — $97")
    + p(
        "This is the last email in the series — no drip-forever sequence. "
        "The assessment stays free either way. Use it."
    )
)


def main() -> int:
    for eid, subject, body in [
        (467332, E5_SUBJECT, E5_BODY),
        (467334, E7_SUBJECT, E7_BODY),
    ]:
        result = update_email(eid, subject, body)
        print(f"  {eid} updated + verified: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
