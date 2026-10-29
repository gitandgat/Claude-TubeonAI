"""Commute classification from Sahawat's Ottawa address — no geocoding, no API calls.

Home base: 335 Cooper St, Ottawa, ON (Centretown).
Walk is the stated priority; short LRT/bus is acceptable but ranks below it.

This is a pure-logic curated lookup, consistent with the rest of the pipeline's
"never invent facts" rule: a location string either matches a known Ottawa-area
neighbourhood/landmark/FSA, or it doesn't — no distance estimation, no guessing.
"""

import re
from typing import Optional

HOME_ADDRESS = "335 Cooper St, Ottawa, ON"
HOME_NEIGHBOURHOOD = "Centretown"

# Walking distance (roughly under 30 min on foot from Centretown).
_WALK_TERMS = [
    "centretown", "downtown ottawa", "downtown core", "parliament hill",
    "sparks st", "queen st", "bank st", "elgin st", "somerset",
    "golden triangle", "byward market", "lowertown", "sandy hill", "uottawa",
    "university of ottawa", "rideau centre", "the glebe", "glebe", "chinatown",
    "little italy", "lebreton flats", "lebreton", "lansdowne park", "lansdowne",
    # GoodLife names its clubs by intersection, and that name is the whole of
    # what the Workday feed's locationsText carries — no street suffix for
    # "queen st" / "bank st" above to catch. Same reason "rideau centre" and
    # "lansdowne" are in this list.
    "queen and bank",
]
_WALK_FSAS = {"K1P", "K2P", "K1R", "K1N", "K1S"}

# One bus or one O-Train leg, roughly ~30 min door to door.
_TRANSIT_TERMS = [
    "hintonburg", "westboro", "vanier", "new edinburgh", "tunney's pasture",
    "tunneys pasture", "civic hospital", "the ottawa hospital", "general hospital",
    "cheo", "children's hospital of eastern ontario", "st-laurent", "st laurent",
    "hunt club", "merivale", "gatineau", "hull",
]

# Not walkable/short-transit — Ottawa's outer suburbs and beyond.
_FAR_TERMS = [
    "kanata", "orleans", "orléans", "barrhaven", "stittsville", "nepean",
    "bells corners", "riverside south", "manotick", "greely", "rockland",
    "carleton place", "kemptville", "arnprior",
]

_POSTAL_RE = re.compile(r"\bK\d[A-Z]\s?\d[A-Z]\d\b", re.IGNORECASE)
_FSA_RE = re.compile(r"\b(K\d[A-Z])\s?\d[A-Z]\d\b", re.IGNORECASE)

_LABELS = {
    "walk": "🚶 walkable from Centretown",
    "transit": "🚌 ~30 min by bus/O-Train",
    "far": "🚗 far — outer suburb, not walk/short-transit",
    "remote": "💻 remote",
    "unknown": "location unclear — not in posting",
}

_MINUTES = {
    "walk": 20,
    "transit": 30,
    "far": None,
    "remote": 0,
    "unknown": None,
}


def _contains_any(text: str, terms) -> bool:
    return any(term in text for term in terms)


def classify_commute(text: Optional[str]) -> dict:
    """Classify a job's commute from Centretown based on free text (location +
    title + description, whatever's available). Returns {mode, minutes, label}.

    mode is one of: walk, transit, far, remote, unknown.
    "Ottawa" alone with no more specific match is `unknown`, not `walk` — the
    exact address just isn't in the posting, so no adjustment should be applied.
    """
    low = (text or "").lower()

    if "remote" in low or "work from home" in low or "télétravail" in low or "teletravail" in low:
        mode = "remote"
    elif _contains_any(low, _WALK_TERMS):
        mode = "walk"
    elif _contains_any(low, _FAR_TERMS):
        mode = "far"
    elif _contains_any(low, _TRANSIT_TERMS):
        mode = "transit"
    else:
        mode = "unknown"
        fsa_match = _FSA_RE.search(text or "")
        if fsa_match:
            fsa = fsa_match.group(1).upper()
            if fsa in _WALK_FSAS:
                mode = "walk"

    return {"mode": mode, "minutes": _MINUTES[mode], "label": _LABELS[mode]}


def commute_score_adjustment(mode: str) -> int:
    """Score adjustment applied in job_agent.py after score_fit(). Walk is a
    bonus (not a transit penalty) so a strong health-informatics job one bus
    away still clears MIN_SCORE."""
    return {"walk": 1, "transit": 0, "far": -2, "remote": 0, "unknown": 0}.get(mode, 0)


if __name__ == "__main__":
    for sample in [
        "199 Queen St, Ottawa",
        "GoodLife Fitness Ottawa Kanata",
        "CHEO, 401 Smyth Rd, Ottawa",
        "Ottawa, ON",
        "Remote (Canada)",
        "K2P 1A1",
    ]:
        print(f"{sample!r:45} -> {classify_commute(sample)}")
