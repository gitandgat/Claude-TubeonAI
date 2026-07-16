"""Repetition guard.

At 10 posts/day all seeded from the same 8 proven hooks, the local model keeps
reaching for the same opening and the same signature details ($18,000, 47
minutes, 11 years, the stop sign). To an audience that's repetitive and looks
automated. This module detects overlap against recently published posts so the
writer can regenerate with an avoid-list.
"""

import json
import os
import re

# Signature details the proven hooks lean on — reusing 2+ in one post = stale
SIGNATURE_TOKENS = [
    r"\$18,?000", r"\$19", r"47 minutes", r"11 years", r"13 hours",
    r"stop sign", r"yellow vest", r"white coat", r"6 weeks",
    r"second carms", r"#47", r"ranked #?47",
]

OPENING_WORDS = 18          # compare the first N words (the hook)
OPENING_OVERLAP_LIMIT = 0.6  # Jaccard above this = same opening
SIGNATURE_REUSE_LIMIT = 2    # this many shared signature details = stale


def _normalize(text: str) -> list:
    return re.findall(r"[a-z0-9$#]+", (text or "").lower())


def recent_post_texts(schedule_log_path: str, n: int = 20) -> list:
    """Last N successfully published post bodies, newest last."""
    if not os.path.exists(schedule_log_path):
        return []
    texts = []
    with open(schedule_log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("success") and d.get("post_text"):
                texts.append(d["post_text"])
    return texts[-n:]


def _opening_overlap(a: str, b: str) -> float:
    sa = set(_normalize(a)[:OPENING_WORDS])
    sb = set(_normalize(b)[:OPENING_WORDS])
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _signatures(text: str) -> set:
    low = (text or "").lower()
    return {pat for pat in SIGNATURE_TOKENS if re.search(pat, low)}


def overlaps(new_post: str, recent_texts: list) -> list:
    """Reasons the new post repeats recent ones. Empty list = fresh enough."""
    reasons = []
    new_sigs = _signatures(new_post)
    for old in recent_texts:
        if _opening_overlap(new_post, old) >= OPENING_OVERLAP_LIMIT:
            reasons.append(f"opening too similar to a recent post: \"{old[:50]}...\"")
        shared = new_sigs & _signatures(old)
        if len(shared) >= SIGNATURE_REUSE_LIMIT:
            reasons.append(f"reuses signature details {sorted(shared)} from a recent post")
    # De-dup reasons, cap noise
    return list(dict.fromkeys(reasons))[:4]


def avoid_list(recent_texts: list) -> str:
    """A compact 'avoid repeating these' instruction for the regeneration pass."""
    used_sigs = set()
    openers = []
    for t in recent_texts[-8:]:
        used_sigs |= _signatures(t)
        first = next((ln.strip() for ln in (t or "").split("\n") if ln.strip()), "")
        if first:
            openers.append(first[:60])
    parts = []
    if used_sigs:
        readable = sorted(s.replace("\\", "").replace("?", "") for s in used_sigs)
        parts.append("Do NOT reuse these details (use a DIFFERENT true moment): " + ", ".join(readable))
    if openers:
        parts.append("Do NOT open like any of these recent posts: " + " | ".join(openers[-5:]))
    return "\n".join(parts)
