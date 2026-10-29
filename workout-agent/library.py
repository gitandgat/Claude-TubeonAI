"""Resolve what gets typed ("bench", "pullups") against exercise_library.

Deterministic first: normalised exact and compact matching settle most input with
no model call. The model is used only to break a genuine tie between several real
candidates, and it is allowed to answer "none of these" — a lift that is not in the
library gets logged under its raw name rather than quietly mapped onto a different
exercise, which would corrupt both the PR history and the volume comparison.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from anthropic import Anthropic

import config

log = logging.getLogger("workout-agent.library")

# Bare input like "bench" or "squat" means the barbell lift in almost every gym
# log. These decide the tie deterministically instead of spending a model call.
# Audited against the live 85-row library: every target below exists. "curl" and
# "rdl" were deliberately dropped — the library has no barbell curl at all (only
# leg curls), and "RDL" is already an alias of Romanian Deadlift, so inventing a
# preference for either would have pointed at a name that does not exist.
BARE_PREFERENCES = {
    "bench": "Barbell Bench Press",
    "bench press": "Barbell Bench Press",
    "squat": "Barbell Back Squat",
    "deadlift": "Conventional Deadlift",
    "row": "Barbell Row",
    "press": "Overhead Press",
    "ohp": "Overhead Press",
    "hip thrust": "Barbell Hip Thrust",
    "lunge": "Walking Lunge",
}

_NOISE = re.compile(r"[^a-z0-9\s]")


def _normalise(text: str) -> str:
    text = _NOISE.sub(" ", (text or "").lower())
    return " ".join(text.split())


def _tokens(text: str) -> frozenset[str]:
    """Normalised tokens with trailing plurals stripped, so "pullups" and
    "pull up" reduce to the same thing."""
    out = set()
    for token in _normalise(text).split():
        if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
            token = token[:-1]
        out.add(token)
    return frozenset(out)


def _compact(text: str) -> str:
    """Spaces removed and plural stripped: "pullups" -> "pullup", "Pull Up" -> "pullup"."""
    joined = _normalise(text).replace(" ", "")
    if len(joined) > 4 and joined.endswith("s") and not joined.endswith("ss"):
        joined = joined[:-1]
    return joined


@dataclass(frozen=True)
class Resolution:
    """Outcome for one typed exercise phrase."""

    raw: str
    row: dict | None
    candidates: tuple[dict, ...] = ()

    @property
    def matched(self) -> bool:
        return self.row is not None

    @property
    def name(self) -> str:
        return self.row["exercise_name"] if self.row else self.raw


class ExerciseLibrary:
    """In-memory index over exercise_library rows."""

    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows
        self._by_exact: dict[str, dict] = {}
        self._by_compact: dict[str, dict] = {}

        for row in rows:
            names = [row["exercise_name"], *(row.get("alternate_names") or [])]
            for name in names:
                # Canonical names win over alternates on collision, so an alias
                # can never shadow a real exercise.
                self._by_exact.setdefault(_normalise(name), row)
                self._by_compact.setdefault(_compact(name), row)
            self._by_exact[_normalise(row["exercise_name"])] = row
            self._by_compact[_compact(row["exercise_name"])] = row

        self._by_name = {r["exercise_name"]: r for r in rows}

        # A preference naming an exercise that is not in the library would fail
        # open and quietly stop disambiguating. Say so loudly instead.
        missing = sorted(set(BARE_PREFERENCES.values()) - set(self._by_name))
        if missing:
            log.warning(
                "BARE_PREFERENCES names %d exercise(s) absent from exercise_library, "
                "so those shortcuts are inert: %s",
                len(missing), ", ".join(missing),
            )

    def by_name(self, exercise_name: str) -> dict | None:
        """Exact canonical-name lookup, for rows already stored under a library name."""
        return self._by_name.get(exercise_name)

    def _shortlist(self, phrase: str) -> list[dict]:
        """Rows whose name or alias contains every token of the phrase."""
        wanted = _tokens(phrase)
        if not wanted:
            return []
        hits: list[dict] = []
        for row in self.rows:
            names = [row["exercise_name"], *(row.get("alternate_names") or [])]
            if any(wanted <= _tokens(name) for name in names):
                hits.append(row)
        return hits

    def resolve(self, phrase: str) -> Resolution:
        """Deterministic resolution. Leaves ties for the model via `candidates`."""
        key = _normalise(phrase)

        preferred = BARE_PREFERENCES.get(key)
        if preferred and preferred in self._by_name:
            return Resolution(raw=phrase, row=self._by_name[preferred])

        if key in self._by_exact:
            return Resolution(raw=phrase, row=self._by_exact[key])

        compact = _compact(phrase)
        if compact in self._by_compact:
            return Resolution(raw=phrase, row=self._by_compact[compact])

        shortlist = self._shortlist(phrase)
        if len(shortlist) == 1:
            return Resolution(raw=phrase, row=shortlist[0])
        if shortlist:
            return Resolution(raw=phrase, row=None, candidates=tuple(shortlist[:12]))
        return Resolution(raw=phrase, row=None)


def _client() -> Anthropic:
    return Anthropic()


SELECT_TOOL = {
    "name": "select_exercises",
    "description": "Choose the exercise_library entry for each typed phrase",
    "input_schema": {
        "type": "object",
        "properties": {
            "choices": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "phrase_index": {"type": "integer"},
                        "candidate_index": {
                            "type": ["integer", "null"],
                            "description": "Index of the entry that IS this exercise, or null if none is",
                        },
                    },
                    "required": ["phrase_index", "candidate_index"],
                },
            }
        },
        "required": ["choices"],
    },
}

RULES = (
    "For each phrase, pick the library entry that IS that exercise.\n\n"
    "Rules:\n"
    "- It must be the same movement. A Romanian deadlift is not a conventional "
    "deadlift; a leg curl is not a leg extension; an incline press is not a flat press.\n"
    "- Equipment matters when the phrase names it: 'db bench' is the dumbbell entry, "
    "not the barbell one. When the phrase names no equipment, prefer the barbell/"
    "standard version of the lift.\n"
    "- Answer null when no entry is the same movement. Null is the correct answer "
    "for a lift the library does not contain — a wrong match corrupts PR history.\n"
)


def disambiguate(resolutions: list[Resolution]) -> list[Resolution]:
    """Resolve ties in one model call. Resolutions without candidates pass through."""
    pending = [
        (i, r) for i, r in enumerate(resolutions) if not r.matched and r.candidates
    ]
    if not pending:
        return resolutions

    listing = []
    for slot, (_, res) in enumerate(pending):
        lines = [f"Phrase {slot}: {res.raw!r}"]
        lines += [
            f"  {j}. {c['exercise_name']} "
            f"[{c.get('movement_pattern') or '-'}; {', '.join(c.get('muscle_groups') or [])}]"
            for j, c in enumerate(res.candidates)
        ]
        listing.append("\n".join(lines))

    try:
        result = _client().messages.create(
            model=config.MODEL,
            max_tokens=1024,
            tools=[SELECT_TOOL],
            tool_choice={"type": "tool", "name": "select_exercises"},
            messages=[{"role": "user", "content": RULES + "\n" + "\n\n".join(listing)}],
        )
        picks = {
            c["phrase_index"]: c["candidate_index"]
            for block in result.content
            if block.type == "tool_use"
            for c in block.input["choices"]
        }
    except Exception:
        # A failed tie-break must not lose the session. Leave them unmatched so
        # they are logged under the raw name and clearly flagged.
        log.exception("Exercise disambiguation failed; leaving phrases unmatched")
        return resolutions

    resolved = list(resolutions)
    for slot, (original_index, res) in enumerate(pending):
        pick = picks.get(slot)
        if pick is None or not (0 <= pick < len(res.candidates)):
            continue
        resolved[original_index] = Resolution(raw=res.raw, row=res.candidates[pick])
    return resolved
