"""Stop-slop quality gate (canonical 5-dimension scorer, 35/50 threshold).

Scoring logic mirrors zernio-prepublish-gate.py so the agent enforces the SAME
standard as the rest of the Crosswalk pipeline. Pure-function scoring — no API
key required. Validated Jun 2026: the user's 4,000-14,000 impression posts all
score 48.5-50/50, so this gate aligns with what actually performs.
"""

import re

PASS_THRESHOLD = 35  # out of 50

SLOP_PATTERNS = {
    "adverbs": r"\b(really|truly|literally|clearly|honestly|simply|basically|actually|definitely|certainly|obviously|absolutely|essentially|quite|rather|fairly|extremely|incredibly|remarkably|undoubtedly|notably|seemingly|perhaps)\b",
    "throat_clearing": r"\b(here's what|the fact is|the truth is|the thing is)\b",
    "passive_voice": r"\b(is|are|was|were|been|be)\s+(said|done|made|given|taken|shown|seen|found|brought|told|asked|called|known|understood|meant|supposed|believed)\b",
    "vague_declaratives": r"\b(the reason|the issue|the problem|the solution|the answer|implications are|reasons are)\b",
    "inanimate_actions": r"\b(the [a-z]+ (emerges|becomes|develops|grows|shifts|transforms|evolves|changes|turns))\b",
    "extremes": r"\b(always|never|everyone|nobody|everything)\b",
    "em_dashes": r"—",
    "meta_joiners": r"\b(as mentioned|as noted|furthermore|additionally|moreover|in addition|the fact that)\b",
}


def score_post(content: str) -> tuple:
    """Return (total_out_of_50, per_dimension_scores, raw_issue_counts)."""
    issues = {dim: len(re.findall(pat, content, re.IGNORECASE | re.MULTILINE))
              for dim, pat in SLOP_PATTERNS.items()}

    scores = {}
    scores["directness"] = max(1, 10 - min(10, (issues["vague_declaratives"] + issues["throat_clearing"]) * 2))

    rhythm = 10 - min(10, issues["em_dashes"] * 3)
    sentences = [s.strip() for s in content.split(".") if s.strip()]
    if len(sentences) > 2:
        lengths = [len(s.split()) for s in sentences[:5]]
        if len(set(lengths)) < 2:
            rhythm -= 3
    scores["rhythm"] = max(1, rhythm)

    scores["trust"] = max(1, 10 - min(10, int((issues["passive_voice"] + issues["extremes"]) * 1.5)))
    scores["authenticity"] = max(1, 10 - min(10, (issues["adverbs"] + issues["inanimate_actions"]) * 2))
    scores["density"] = max(1, 10 - min(10, issues["meta_joiners"] * 2))

    return sum(scores.values()), scores, issues


def recommendations(issues: dict) -> list:
    """Human-readable fixes for whatever tripped the score."""
    recs = []
    if issues["adverbs"]:
        recs.append(f"remove {issues['adverbs']} weak adverbs (really, truly, clearly, etc.)")
    if issues["throat_clearing"]:
        recs.append(f"cut {issues['throat_clearing']} throat-clearing phrases (here's what, the truth is)")
    if issues["passive_voice"]:
        recs.append(f"rewrite {issues['passive_voice']} passive constructions in active voice")
    if issues["vague_declaratives"]:
        recs.append(f"replace {issues['vague_declaratives']} vague declaratives with specifics")
    if issues["inanimate_actions"]:
        recs.append(f"stop {issues['inanimate_actions']} inanimate objects from 'acting'")
    if issues["extremes"]:
        recs.append(f"replace {issues['extremes']} lazy extremes (always, never, everyone)")
    if issues["em_dashes"]:
        recs.append(f"remove all {issues['em_dashes']} em-dashes (use periods or commas)")
    if issues["meta_joiners"]:
        recs.append(f"cut {issues['meta_joiners']} meta-joiners (furthermore, moreover)")
    return recs


def passes(content: str) -> bool:
    total, _, _ = score_post(content)
    return total >= PASS_THRESHOLD
