"""Virality grader (pure-function scorecard, hook weighted 50%).

Ported from the installed `post-grader` Claude skill, adapted to a deterministic
scorer in the same spirit as stop_slop_gate.py: no API key, no network, so it can
run on EVERY post for free and never adds a new failure mode to the live pipeline.

stop_slop_gate.py answers "does this read like AI?" (mechanical cleanliness).
This answers the orthogonal question "would this travel?" (hook strength, curiosity,
emotion, share-worthiness, polarity, platform fit). The two are complementary gates.

Deviation from the skill: the skill's 7th dimension (voice match) needs the brand
brief, so it's omitted here — voice is already enforced by stop_slop_gate + the
first-person check in post_writer. Its weight is redistributed to curiosity/share.

Weights (sum to 10 → score is /100):
    hook 50 | curiosity 15 | emotion 10 | share-worthiness 15 | polarity 5 | platform 5

Calibrated Jun 2026 against this account's data: first-person scenes with real
numbers (the 4k-14k-view posts) score ~85+; abstract second-person advice scores <40.
"""

from __future__ import annotations

import re

VIRALITY_TARGET = 70          # advisory pass mark, out of 100
HOOK_RESCUE_BELOW = 5         # hook sub-score (/10) under this triggers a rewrite

_FIRST_PERSON_OPEN = re.compile(
    r"^(i |i'|my |we |we'|the day i|the year i|the night i|the morning i|"
    r"the moment i|last (week|month|year|night)|years ago|a few years ago)",
    re.IGNORECASE,
)
_SECOND_PERSON_OPEN = re.compile(r"^(you |you'|your )", re.IGNORECASE)
_THROAT_CLEARING_OPEN = re.compile(
    r"^(here's what|the truth is|the thing is|in today's|let me tell|"
    r"imagine |picture this|are you ready|in a world)",
    re.IGNORECASE,
)
_NUMBER = re.compile(r"\$?\d[\d,]*")
_HASHTAG = re.compile(r"(?m)(?:^|\s)#\w+")

_EMOTION_WORDS = (
    "fear", "afraid", "scared", "terrified", "grief", "shame", "ashamed", "proud",
    "pride", "angry", "anger", "cried", "tears", "alone", "lonely", "relief",
    "joy", "broke", "broken", "failed", "failure", "rejection", "rejected",
    "lost", "hope", "regret", "guilt", "panic", "exhausted", "numb", "quit",
)
_POLARITY_MARKERS = (
    "most people", "everyone thinks", "they're wrong", "is wrong", "is dead",
    "is overrated", "myth", "unpopular opinion", "stop doing", "nobody tells",
    "the real question", "isn't the question", "i disagree", "stop putting",
)
_SHARE_CTA = (
    "share this", "share it", "tag someone", "send this", "save this",
    "save it", "dm me", "comment ", "repost", "follow", "tell me i'm wrong",
)


def _first_line(post: str) -> str:
    for ln in post.split("\n"):
        s = ln.strip().lstrip("*# ").strip()
        if s:
            return s
    return ""


def _hook_strength(first_line: str) -> int:
    """0-10. Rewards the account's proven signal: first-person scene + a number."""
    if not first_line:
        return 0
    score = 5
    if _FIRST_PERSON_OPEN.match(first_line):
        score += 3
    if _SECOND_PERSON_OPEN.match(first_line):
        score -= 5
    if _THROAT_CLEARING_OPEN.match(first_line):
        score -= 2
    if _NUMBER.search(first_line):
        score += 2
    n = len(first_line)
    if n <= 160:            # could stand alone as a tweet
        score += 1
    elif n > 280:
        score -= 1
    return max(0, min(10, score))


def _specificity(post: str) -> int:
    """0-10. Concrete numbers are the rawest specificity signal."""
    nums = len(_NUMBER.findall(post))
    return max(0, min(10, 2 + nums * 2))


def _emotion(post: str) -> int:
    low = post.lower()
    hits = sum(1 for w in _EMOTION_WORDS if w in low)
    return max(0, min(10, 2 + hits * 2))


def _share_worthiness(post: str) -> int:
    """0-10. A question (comment driver) + an explicit share/save/DM cue."""
    low = post.lower()
    score = 2
    if "?" in post:
        score += 3
    if any(c in low for c in _SHARE_CTA):
        score += 3
    if any(m in low for m in _POLARITY_MARKERS):
        score += 2
    return max(0, min(10, score))


def _polarity(post: str) -> int:
    low = post.lower()
    hits = sum(1 for m in _POLARITY_MARKERS if m in low)
    return max(0, min(10, 2 + hits * 3))


def _platform_fit(post: str) -> int:
    """0-10. LinkedIn: enough body, sane hashtag count."""
    words = len(post.split())
    tags = len(_HASHTAG.findall(post))
    score = 10
    if words < 60:
        score -= 3
    elif words > 420:
        score -= 2
    if tags == 0:
        score -= 1
    elif tags > 6:
        score -= 3
    return max(0, min(10, score))


def grade(post: str) -> tuple[float, dict, list]:
    """Return (score_out_of_100, per_dimension_scores_0_10, ranked_fixes)."""
    first_line = _first_line(post)
    dims = {
        "hook": _hook_strength(first_line),
        "curiosity": _specificity(post),
        "emotion": _emotion(post),
        "share": _share_worthiness(post),
        "polarity": _polarity(post),
        "platform": _platform_fit(post),
    }
    total = (
        dims["hook"] * 5.0
        + dims["curiosity"] * 1.5
        + dims["emotion"] * 1.0
        + dims["share"] * 1.5
        + dims["polarity"] * 0.5
        + dims["platform"] * 0.5
    )
    return round(total, 1), dims, _fixes(dims, first_line)


def _fixes(dims: dict, first_line: str) -> list:
    """Top fixes, ranked by impact (hook first — it's 50% of the score)."""
    recs: list[str] = []
    if dims["hook"] < 7:
        if _SECOND_PERSON_OPEN.match(first_line or ""):
            recs.append("Opening is second-person advice — rewrite line 1 as a "
                        "first-person scene with a real number (50% of the score).")
        elif not _NUMBER.search(first_line or ""):
            recs.append("Put a concrete number/object in line 1 (e.g. '47 minutes', "
                        "'$18,000') — the hook is 50% of the score.")
        else:
            recs.append("Sharpen line 1: open mid-scene, first person; the first 3 "
                        "words must create pull.")
    if dims["curiosity"] < 6:
        recs.append("Add real specifics — dollars, years, the exact object in the room.")
    if dims["share"] < 6:
        recs.append("Close with a comment-driving question or an explicit share/DM cue.")
    if dims["emotion"] < 5:
        recs.append("Name the feeling from inside the moment (the turn that flips meaning).")
    if dims["platform"] < 7:
        recs.append("Fix length/hashtags for LinkedIn (enough body, 1-5 topic tags).")
    return recs


def passes(post: str) -> bool:
    total, _, _ = grade(post)
    return total >= VIRALITY_TARGET
