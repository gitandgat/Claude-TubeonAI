"""Training maths. Pure functions, no I/O and no model calls — the numbers here
must be reproducible, so nothing in this module is allowed to guess.

Formulas are fixed by spec and must not be "improved":
    volume_load   = sets x reps x weight
    estimated 1RM = weight x (1 + reps / 30)        [Epley]
    PR            = beats personal_records.max_weight or .max_volume
"""

from __future__ import annotations

from dataclasses import dataclass, field

import config


@dataclass(frozen=True)
class SetEntry:
    """One logged set. Frozen: logged sets are facts, not working state."""

    reps: int
    weight_kg: float
    is_bodyweight: bool = False

    @property
    def volume_load(self) -> float:
        # sets x reps x weight, with sets = 1 for a single-set row.
        return round(config.SETS_PER_ROW * self.reps * self.weight_kg, 2)

    @property
    def estimated_1rm(self) -> float:
        """Epley. Undefined for a zero-load set, and at reps=0 it degenerates to
        the weight itself, so guard both rather than emit a confident 0."""
        if self.weight_kg <= 0 or self.reps <= 0:
            return 0.0
        return round(self.weight_kg * (1 + self.reps / 30), 2)


@dataclass(frozen=True)
class ExerciseResult:
    """An exercise as performed in one session, with its derived numbers."""

    logged_name: str
    sets: tuple[SetEntry, ...]
    library_name: str | None = None
    muscle_groups: tuple[str, ...] = ()
    movement_pattern: str | None = None
    raw_input: str = ""

    @property
    def in_library(self) -> bool:
        return self.library_name is not None

    @property
    def total_volume_load(self) -> float:
        return round(sum(s.volume_load for s in self.sets), 2)

    @property
    def total_reps(self) -> int:
        return sum(s.reps for s in self.sets)

    @property
    def top_weight(self) -> float:
        return max((s.weight_kg for s in self.sets), default=0.0)

    @property
    def best_1rm(self) -> float:
        """Best estimated 1RM across the session's sets — a hard triple can beat a
        heavier single, so this is not simply the top weight's estimate."""
        return max((s.estimated_1rm for s in self.sets), default=0.0)

    @property
    def set_count(self) -> int:
        return len(self.sets)


@dataclass(frozen=True)
class PRCheck:
    """Outcome of comparing a session against stored personal records."""

    exercise_name: str
    weight_pr: bool
    volume_pr: bool
    new_max_weight: float
    new_max_volume: float
    previous_max_weight: float
    previous_max_volume: float
    is_first_record: bool = False

    @property
    def any_pr(self) -> bool:
        return self.weight_pr or self.volume_pr


def check_pr(result: ExerciseResult, record: dict | None) -> PRCheck:
    """Compare a session's exercise against its stored record.

    max_volume is the exercise's session volume load (all sets), which is the
    standard volume PR; max_weight is the heaviest single set.
    """
    previous_weight = float(record["max_weight"]) if record else 0.0
    previous_volume = float(record["max_volume"]) if record else 0.0

    weight_pr = result.top_weight > previous_weight
    volume_pr = result.total_volume_load > previous_volume

    return PRCheck(
        exercise_name=result.logged_name,
        weight_pr=weight_pr,
        volume_pr=volume_pr,
        new_max_weight=max(result.top_weight, previous_weight),
        new_max_volume=max(result.total_volume_load, previous_volume),
        previous_max_weight=previous_weight,
        previous_max_volume=previous_volume,
        is_first_record=record is None,
    )


@dataclass(frozen=True)
class Comparison:
    """This session's exercise against the last time the same lift was trained."""

    exercise_name: str
    last_date: str
    volume_delta: float
    volume_pct: float
    top_weight_delta: float
    rm_delta: float
    previous_volume: float
    previous_top_weight: float
    previous_1rm: float

    @property
    def progressing(self) -> bool:
        return self.volume_delta > 0 or self.top_weight_delta > 0


def compare_to_previous(
    result: ExerciseResult, previous_sets: list[dict], last_date: str
) -> Comparison | None:
    """Volume/load/1RM change vs the previous session of this lift.

    previous_sets are workout_exercises rows from that one earlier date.
    """
    if not previous_sets:
        return None

    previous = tuple(
        SetEntry(reps=int(r["reps"]), weight_kg=float(r["weight"])) for r in previous_sets
    )
    before = ExerciseResult(logged_name=result.logged_name, sets=previous)

    previous_volume = before.total_volume_load
    delta = round(result.total_volume_load - previous_volume, 2)

    return Comparison(
        exercise_name=result.logged_name,
        last_date=last_date,
        volume_delta=delta,
        # Guard the divide: a previous session of pure bodyweight-at-zero work
        # would otherwise blow up here.
        volume_pct=round(delta / previous_volume * 100, 1) if previous_volume > 0 else 0.0,
        top_weight_delta=round(result.top_weight - before.top_weight, 2),
        rm_delta=round(result.best_1rm - before.best_1rm, 2),
        previous_volume=previous_volume,
        previous_top_weight=before.top_weight,
        previous_1rm=before.best_1rm,
    )


def to_kg(weight: float, unit: str) -> float:
    """Normalise an input weight to kg. Everything is stored in kg."""
    unit = (unit or config.DEFAULT_UNIT).lower()
    if unit in {"kg", "kgs", "kilo", "kilos", "kilogram", "kilograms"}:
        return round(float(weight), 2)
    if unit in {"lb", "lbs", "pound", "pounds", "#"}:
        return round(float(weight) / config.LB_PER_KG, 2)
    raise ValueError(f"Unknown weight unit {unit!r} — use kg or lb.")
