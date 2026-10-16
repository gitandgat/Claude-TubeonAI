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


@dataclass(frozen=True)
class ParsedCardio:
    """Time/distance work. Never carries reps or a load.

    The split from ParsedExercise exists because volume load and Epley both need
    reps and a weight. Coercing "50 minutes" into "50 reps" once produced an entry
    that looked real and was false, so cardio keeps its own fields entirely.
    """

    raw_name: str
    duration_seconds: int | None = None
    distance_m: float | None = None
    avg_heart_rate: int | None = None
    max_heart_rate: int | None = None
    rpe: float | None = None
    incline_pct: float | None = None
    speed_kph: float | None = None
    resistance_level: float | None = None
    interval_work_seconds: int | None = None
    interval_rest_seconds: int | None = None
    interval_rounds: int | None = None


@dataclass(frozen=True)
class ParsedSession:
    """Rep-based work and time/distance work, kept strictly apart."""

    exercises: tuple[ParsedExercise, ...]
    cardio: tuple[ParsedCardio, ...] = ()


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
            },
            "cardio": {
                "type": "array",
                "description": (
                    "Work measured by time or distance rather than reps (running, "
                    "walking, cycling, rowing, intervals, a plank held for time). "
                    "Never give these reps or a weight."
                ),
                "items": {
                    "type": "object",
                    "properties": {
                        "raw_name": {
                            "type": "string",
                            "description": "The activity as written, without the numbers",
                        },
                        "duration_seconds": {
                            "type": ["integer", "null"],
                            "description": "Total WORKING seconds, excluding rest. For intervals this is work x rounds.",
                        },
                        "distance_m": {"type": ["number", "null"], "description": "Distance in metres"},
                        "avg_heart_rate": {"type": ["integer", "null"]},
                        "max_heart_rate": {"type": ["integer", "null"]},
                        "rpe": {"type": ["number", "null"], "description": "Perceived exertion 1-10, only if stated"},
                        "incline_pct": {"type": ["number", "null"]},
                        "speed_kph": {"type": ["number", "null"], "description": "Speed in km/h; convert mph if needed"},
                        "resistance_level": {"type": ["number", "null"]},
                        "interval_work_seconds": {"type": ["integer", "null"]},
                        "interval_rest_seconds": {"type": ["integer", "null"]},
                        "interval_rounds": {"type": ["integer", "null"]},
                    },
                    "required": ["raw_name"],
                },
            },
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
    "If a rep count is genuinely absent for a set, omit that set rather than guessing.\n\n"
    "CRITICAL — time and distance are not reps. Anything measured by duration, "
    "distance, pace or incline rather than repetitions (a 50-minute incline walk, "
    "a 5 km run, 4-minute rowing intervals, a 60-second plank) goes in `cardio`, "
    "never in `exercises`. Never turn minutes, seconds, kilometres or rounds into "
    "a rep count.\n\n"
    "For cardio entries:\n"
    "- Convert minutes to seconds and kilometres to metres.\n"
    "- duration_seconds is WORKING time, excluding rest. '4 min on, 4 min off, "
    "4 rounds' is interval_work_seconds 240, interval_rest_seconds 240, "
    "interval_rounds 4, and duration_seconds 960 (240 x 4).\n"
    "- Put machine settings in incline_pct / speed_kph / resistance_level: "
    "'incline walking 15% 4.8 kph 50 minutes' is incline_pct 15, speed_kph 4.8, "
    "duration_seconds 3000.\n"
    "- raw_name excludes the numbers: 'incline walking', not 'incline walking 15%'.\n"
    "- Leave any field null when it was not stated. Do not estimate heart rate, "
    "distance or effort."
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


def parse_session(text: str) -> ParsedSession:
    """Free text -> rep-based exercises, plus any time/distance work named separately."""
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

    def _num(entry: dict, key: str, cast):
        value = entry.get(key)
        if value is None:
            return None
        try:
            return cast(value)
        except (TypeError, ValueError):
            log.warning("Dropping unreadable %s=%r on cardio entry", key, value)
            return None

    cardio: list[ParsedCardio] = []
    raw_cardio = payload.get("cardio") if isinstance(payload, dict) else None
    for entry in _decoded(raw_cardio) or []:
        entry = _decoded(entry)
        if not isinstance(entry, dict):
            continue
        name = (entry.get("raw_name") or "").strip()
        if not name:
            continue
        cardio.append(
            ParsedCardio(
                raw_name=name,
                duration_seconds=_num(entry, "duration_seconds", int),
                distance_m=_num(entry, "distance_m", float),
                avg_heart_rate=_num(entry, "avg_heart_rate", int),
                max_heart_rate=_num(entry, "max_heart_rate", int),
                rpe=_num(entry, "rpe", float),
                incline_pct=_num(entry, "incline_pct", float),
                speed_kph=_num(entry, "speed_kph", float),
                resistance_level=_num(entry, "resistance_level", float),
                interval_work_seconds=_num(entry, "interval_work_seconds", int),
                interval_rest_seconds=_num(entry, "interval_rest_seconds", int),
                interval_rounds=_num(entry, "interval_rounds", int),
            )
        )

    if not exercises and not cardio:
        raise ParseError(
            "I couldn't find a session in that. Try something like "
            "'bench 3x8 @ 80kg' or 'incline walk 15% at 4.8 kph for 50 minutes'."
        )
    return ParsedSession(exercises=tuple(exercises), cardio=tuple(cardio))
