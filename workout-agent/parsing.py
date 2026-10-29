"""Turn a typed session into structured sets.

"bench 3x8 @ 80kg, squat 5,5,5 @ 100, pullups 3x12 bodyweight"

Notation in the wild is too varied for a regex to own: 3x8, 5,5,5, 100x5/110x3/120x1,
"bodyweight", "+20kg", lb vs kg, "to failure". The model's job is strictly to
TRANSCRIBE that into sets — it is never asked to compute volume, 1RM or anything
else derived. All arithmetic happens in metrics.py so the numbers are reproducible.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from anthropic import Anthropic

import config

log = logging.getLogger("workout-agent.parsing")


class ParseError(RuntimeError):
    """The session text could not be turned into sets."""


@dataclass(frozen=True)
class ParsedSet:
    reps: int
    weight: float
    unit: str
    is_bodyweight: bool = False
    added_weight: float = 0.0


@dataclass(frozen=True)
class ParsedExercise:
    raw_name: str
    sets: tuple[ParsedSet, ...]


PARSE_TOOL = {
    "name": "record_session",
    "description": "Transcribe a training session into exercises and their sets",
    "input_schema": {
        "type": "object",
        "properties": {
            "exercises": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "raw_name": {
                            "type": "string",
                            "description": "The exercise as written, with set/rep/weight notation stripped",
                        },
                        "sets": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "reps": {"type": "integer", "description": "Reps in this one set"},
                                    "weight": {
                                        "type": "number",
                                        "description": "External load for this set. 0 for unloaded bodyweight work.",
                                    },
                                    "unit": {"type": "string", "enum": ["kg", "lb"]},
                                    "is_bodyweight": {
                                        "type": "boolean",
                                        "description": "True when bodyweight is the load (pull up, dip, push up)",
                                    },
                                    "added_weight": {
                                        "type": "number",
                                        "description": "Extra load on a bodyweight lift, e.g. weighted pull up +20kg",
                                    },
                                },
                                "required": ["reps", "weight", "unit", "is_bodyweight"],
                            },
                        },
                    },
                    "required": ["raw_name", "sets"],
                },
            }
        },
        "required": ["exercises"],
    },
}

INSTRUCTIONS = (
    "Transcribe this training session into exercises and individual sets.\n\n"
    "Expand every set out — one entry per set performed:\n"
    "- '3x8 @ 80kg' is three sets of 8 reps at 80 kg.\n"
    "- '5,5,5 @ 100' is three sets of 5 reps at 100.\n"
    "- '100x5, 110x3, 120x1' is three sets at different loads; weight-by-reps order.\n"
    "- '3x12 bodyweight' is three sets of 12 with is_bodyweight true and weight 0.\n"
    "- A weighted bodyweight lift ('pullups 3x5 +20kg') sets is_bodyweight true and "
    "added_weight 20.\n\n"
    "Units: use the unit written. When a number has no unit, use the unit used "
    f"elsewhere in the same message, and {config.DEFAULT_UNIT} if nothing is stated.\n\n"
    "raw_name is the exercise as written, with notation stripped — 'bench 3x8 @ 80kg' "
    "gives raw_name 'bench'. Do NOT expand, correct or canonicalise the name; matching "
    "it against the exercise library happens later.\n\n"
    "Do not compute volume, totals or one-rep maxes. Only transcribe.\n"
    "If a rep count is genuinely absent for a set, omit that set rather than guessing."
)


def _client() -> Anthropic:
    return Anthropic()


def _decoded(value, depth: int = 3):
    """Unwrap a value that arrived JSON-encoded as a string.

    Tool inputs are usually the object the schema asked for, but occasionally
    arrive double-encoded — observed live as {"exercises": "{\"exercises\": [...]}"},
    which iterates as individual characters and blows up far from the cause. It is
    intermittent (one exercise stringified where two did not), so every level is
    normalised instead of trusted.
    """
    for _ in range(depth):
        if not isinstance(value, str):
            break
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return None
    return value


def _exercise_list(payload) -> list | None:
    """Pull the exercises array out of a payload, however deeply it is wrapped."""
    payload = _decoded(payload)
    for _ in range(3):
        if isinstance(payload, dict) and "exercises" in payload:
            payload = _decoded(payload["exercises"])
        else:
            break
    return payload if isinstance(payload, list) else None


def parse_session(text: str) -> list[ParsedExercise]:
    """Free text -> exercises with their sets."""
    if not (text or "").strip():
        raise ParseError("Nothing to parse — send me the session.")

    try:
        result = _client().messages.create(
            model=config.MODEL,
            max_tokens=2048,
            tools=[PARSE_TOOL],
            tool_choice={"type": "tool", "name": "record_session"},
            messages=[{"role": "user", "content": f"{INSTRUCTIONS}\n\nSession:\n{text}"}],
        )
    except Exception as exc:
        raise ParseError(f"Could not reach the model to parse that session: {exc}") from exc

    payload = next(
        (block.input for block in result.content if block.type == "tool_use"), None
    )
    if payload is None:
        raise ParseError("The model returned no structured session.")

    raw_exercises = _exercise_list(payload)
    if raw_exercises is None:
        log.error("Unusable tool payload shape: %r", str(payload)[:300])
        raise ParseError("The model returned a session I couldn't read. Try sending it again.")
    if not isinstance(payload, dict) or not isinstance(payload.get("exercises"), list):
        log.warning("Tool payload arrived encoded as a string; normalised it")

    exercises: list[ParsedExercise] = []
    for item in raw_exercises:
        item = _decoded(item)
        if not isinstance(item, dict):
            log.warning("Skipping unreadable exercise entry: %r", str(item)[:120])
            continue
        name = (item.get("raw_name") or "").strip()
        raw_sets = _decoded(item.get("sets")) or []
        if not isinstance(raw_sets, list):
            log.warning("Skipping %r: unreadable sets", name)
            continue
        sets = tuple(
            ParsedSet(
                reps=int(entry["reps"]),
                weight=float(entry.get("weight") or 0),
                unit=(entry.get("unit") or config.DEFAULT_UNIT).lower(),
                is_bodyweight=bool(entry.get("is_bodyweight")),
                added_weight=float(entry.get("added_weight") or 0),
            )
            for entry in (_decoded(s) for s in raw_sets)
            if isinstance(entry, dict)
            and entry.get("reps") is not None
            and int(entry["reps"]) > 0
        )
        if name and sets:
            exercises.append(ParsedExercise(raw_name=name, sets=sets))

    if not exercises:
        raise ParseError(
            "I couldn't find any sets in that. Try something like "
            "'bench 3x8 @ 80kg, squat 5,5,5 @ 100'."
        )
    return exercises
