#!/usr/bin/env python3
"""Create the 7-email MoveAssess -> Glute Longevity nurture sequence.

E1 instant, E2 d1, E3 d2, E4 d4, E5 d6, E6 d8, E7 d10 — trigger: tag
`moveassess-lead` (added by the MoveAssess capture endpoint). Emails are
created via the sanctioned crosswalk-encharge-email helper (richtext state +
html + subject, self-verifying). The flow itself is assembled in the
Encharge UI — see moveassess-flow-build-instructions.md.
"""

import sys
from pathlib import Path

SKILL_DIR = Path.home() / ".claude" / "skills" / "crosswalk-encharge-email"
sys.path.insert(0, str(SKILL_DIR))

from encharge_email import button, create_email, link, p  # noqa: E402

APP = "https://physical-assessment-app.vercel.app"
LIBRARY_PDF = f"{APP}/protocols/protocol-library.pdf"
PROGRAM = "https://glute.crosswalkwisdom.com"
FIRST = "{{ person.firstName | default: 'there' }}"
CASE = "{{ person.moveassessCaseName | default: 'your movement pattern' }}"

EMAILS = [
    {
        "name": "MoveAssess 1 — Protocol Delivery",
        "subject": "Your corrective protocol (start with Phase 1 tonight)",
        "body": (
            p(f"Hey {FIRST},")
            + p(
                f"You ran the assessment and found <strong>{CASE}</strong>. "
                "Here is the full corrective protocol library — eight clinical "
                "patterns, each with the same three-phase arc: release what is "
                "overworking, wake up what went quiet, then rebuild the pattern "
                "under load."
            )
            + button(LIBRARY_PDF, "Download the Protocol Library (PDF)")
            + p(
                "Don't read all of it. Find your pattern, do Phase 1 tonight — "
                "it takes about ten minutes on the floor in front of the TV. "
                "That's the whole ask today."
            )
            + p(
                "In two weeks, "
                + link(f"{APP}", "run the assessment again")
                + " and compare. The retest is the point: this is a measurement "
                "system, not a stretching routine."
            )
        ),
    },
    {
        "name": "MoveAssess 2 — Ward to World Story",
        "subject": "What I learned watching people lose their independence",
        "body": (
            p(f"Hey {FIRST},")
            + p(
                "I'm a former physician. Before I ever coached anyone, I spent "
                "years on hospital wards watching the same story end the same "
                "way: someone in their 60s or 70s comes in after a fall, and the "
                "fall was never the real problem. The real problem started ten "
                "years earlier — a hip that stopped extending, glutes that went "
                "quiet, a shuffle that crept into their gait so slowly nobody "
                "named it."
            )
            + p(
                "By the time it's a hospital problem, the options are bad. But "
                "ten years earlier? The same person needed ten minutes a day and "
                "someone to show them what was actually weak."
            )
            + p(
                f"That's why the assessment you took exists. <strong>{CASE}</strong> "
                "isn't a diagnosis to worry about — it's the early warning that "
                "ward patients never got."
            )
            + p(
                "Tomorrow I'll show you how one quiet muscle turns into a chain "
                "of compensations — and why the sore spot is almost never the "
                "problem spot."
            )
            + p("— Sahawat")
        ),
    },
    {
        "name": "MoveAssess 3 — Compensation Cascade",
        "subject": "The sore spot is never the problem spot",
        "body": (
            p(f"Hey {FIRST},")
            + p(
                "Here's the pattern behind almost every case in the library, "
                f"including <strong>{CASE}</strong>:"
            )
            + p(
                "<strong>1. A muscle goes quiet.</strong> Usually from sitting, "
                "an old injury, or simple disuse. It doesn't hurt. You don't "
                "notice."
            )
            + p(
                "<strong>2. A neighbour picks up the slack.</strong> Your body "
                "doesn't cancel the movement — it re-routes it. The TFL covers "
                "for the glute med. The lumbar erectors cover for the glute max. "
                "The upper traps cover for the serratus."
            )
            + p(
                "<strong>3. The substitute wears out.</strong> That's the part "
                "you feel — the tight IT band, the cranky lower back, the pinchy "
                "shoulder. So you stretch and massage the substitute… while the "
                "original muscle stays asleep, and the loop repeats."
            )
            + p(
                "This is why the protocol has three phases and why the order "
                "matters. Release alone feels good for a day. Release, then "
                "activate, then integrate — that rewires the pattern."
            )
            + p(
                "If you haven't started Phase 1 yet: "
                + link(LIBRARY_PDF, "the protocol library is here")
                + ". Ten minutes tonight."
            )
        ),
    },
    {
        "name": "MoveAssess 4 — What Change Looks Like",
        "subject": "Week 2 is when people stop believing me (then this happens)",
        "body": (
            p(f"Hey {FIRST},")
            + p(
                "The most common arc I saw across years of clinical work and "
                "coaching goes like this:"
            )
            + p(
                "<strong>Days 1–4:</strong> the release work feels good, the "
                "activation work feels like nothing. \"Am I even doing this "
                "right?\" (Yes. Quiet muscles fire weakly at first — that's the "
                "whole point.)"
            )
            + p(
                "<strong>Days 5–10:</strong> the doubt window. No dramatic "
                "change, and this is where most people quit — usually right "
                "before the nervous system consolidates the new pattern."
            )
            + p(
                "<strong>Days 11–14:</strong> the shift. You stand up from a "
                "chair and something feels different — less braced, more "
                "automatic. The retest confirms what you feel: the compensation "
                "is measurably smaller."
            )
            + p(
                "You're somewhere in that arc right now. The instruction is "
                "boring on purpose: don't add anything, don't skip the "
                "activation phase because it feels easy. "
                + link(f"{APP}", "Retest at day 14")
                + " and let the assessment tell you the truth."
            )
        ),
    },
    {
        "name": "MoveAssess 5 — Glute Longevity Offer",
        "subject": "The protocol fixes the pattern. This keeps it fixed.",
        "body": (
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
            + button(PROGRAM, "See the Glute Longevity Program")
            + p(
                "It's built by a former physician for one specific outcome: "
                "moving at 70 the way you did at 40. The assessment you already "
                "took is the front door."
            )
        ),
    },
    {
        "name": "MoveAssess 6 — Objections",
        "subject": "\"I've tried programs before\" — fair. Read this.",
        "body": (
            p(f"Hey {FIRST},")
            + p("Three things people tell me before they start, answered honestly:")
            + p(
                "<strong>\"I've tried programs before.\"</strong> Generic "
                "programs fail for a specific reason: they load a pattern that's "
                "still broken. If your glute med is asleep, squats train your "
                "TFL to compensate harder. Glute Longevity starts from your "
                f"assessment — <strong>{CASE}</strong> — so you load the "
                "corrected pattern, not the compensation."
            )
            + p(
                "<strong>\"I don't have time.\"</strong> The sessions are 15 "
                "minutes. Not 15-minutes-that-becomes-an-hour — 15 minutes, "
                "designed for the floor of your living room. The program assumes "
                "a real life."
            )
            + p(
                "<strong>\"At my age, is it too late?\"</strong> This one has a "
                "clean answer from the research: muscle responds to progressive "
                "load at every age it's been studied — 60s, 70s, 80s. What "
                "changes with age isn't whether you adapt. It's how expensive "
                "waiting becomes."
            )
            + button(PROGRAM, "See the Program")
        ),
    },
    {
        "name": "MoveAssess 7 — Retest Close",
        "subject": "Run the retest, then decide",
        "body": (
            p(f"Hey {FIRST},")
            + p(
                "It's been about two weeks since you found "
                f"<strong>{CASE}</strong>. Time to close the loop:"
            )
            + p(
                "<strong>1.</strong> "
                + link(f"{APP}", "Run the assessment again")
                + ". Same test, honest look."
            )
            + p(
                "<strong>2.</strong> If the pattern improved — the protocol "
                "worked, and you've proven your body still adapts. That's "
                "exactly the adaptation the Glute Longevity program is built to "
                "compound, year after year."
            )
            + p(
                "<strong>3.</strong> If it didn't improve — in my experience "
                "that's almost never the protocol. It's consistency without "
                "structure. Ten minutes \"when I remember\" isn't a dose. "
                "Programming and accountability are precisely what the program "
                "adds."
            )
            + p(
                "Either result points the same direction, which is why I'm "
                "comfortable making this the last email in the series:"
            )
            + button(PROGRAM, "Start Glute Longevity")
            + p(
                "This is the last one from me on this — no drip-forever "
                "sequence. The assessment stays free either way. Use it."
            )
        ),
    },
]


def main() -> int:
    created = []
    for e in EMAILS:
        eid = create_email(name=e["name"], subject=e["subject"], body_html=e["body"])
        created.append((eid, e["name"]))
        print(f"  {eid}  {e['name']}")
    print(f"\n{len(created)} emails created + verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
