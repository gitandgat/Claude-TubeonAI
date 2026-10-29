"""Controlled experiments for the learning loop.

The loop already enforces the proven first-person format. To DISCOVER new wins
(not just confirm old ones) we vary ONE dimension at a time across posts, tag
each post with its arm, and read age-matched results per arm.

First experiment targets the real bottleneck: shares are ~0, so we test which
CLOSING MECHANIC drives engagement/shares. Keep the story identical; vary only
the ending. One variable = clean attribution.
"""

from datetime import datetime

ACTIVE_EXPERIMENT = "closing_mechanic"

EXPERIMENTS = {
    "closing_mechanic": {
        "dimension": "How the post ends (the share/engagement driver)",
        "arms": {
            "reflective_question": "End with one open, reflective question that invites the reader to share their own version of this story.",
            "tag_someone": "End by asking the reader to tag one specific person who needs to hear this today.",
            "share_if": "End with a single line that invites the reader to repost this if they have lived it, so it reaches someone who needs it.",
            "lesson_ask": "End by asking the reader what their own detour taught them, inviting a comment with their lesson.",
        },
    },
}


def assign_arm(experiment: str = ACTIVE_EXPERIMENT, when: datetime = None) -> str:
    """Deterministically rotate arms by run slot (date + hour), so the 5 daily
    posts spread evenly across arms over time."""
    arms = list(EXPERIMENTS[experiment]["arms"].keys())
    when = when or datetime.now()
    idx = (when.toordinal() * 24 + when.hour) % len(arms)
    return arms[idx]


def arm_instruction(arm: str, experiment: str = ACTIVE_EXPERIMENT) -> str:
    return EXPERIMENTS[experiment]["arms"].get(arm, "")
