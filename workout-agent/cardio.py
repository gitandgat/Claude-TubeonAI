"""Cardio entries: derived metrics and display.

Kept apart from metrics.py because none of the resistance maths applies — there is
no volume load and no Epley estimate for a walk. The comparable signals here are
duration, distance, pace and the machine settings the work was done at.
"""

from __future__ import annotations

from dataclasses import dataclass

import parsing


@dataclass(frozen=True)
class CardioResult:
    """One cardio activity as performed, with its library resolution."""

    logged_name: str
    parsed: parsing.ParsedCardio
    library_name: str | None = None
    raw_input: str = ""

    @property
    def in_library(self) -> bool:
        return self.library_name is not None

    @property
    def duration_seconds(self) -> int:
        return self.parsed.duration_seconds or 0

    @property
    def distance_m(self) -> float:
        return self.parsed.distance_m or 0.0

    @property
    def pace_sec_per_km(self) -> float | None:
        """Seconds per kilometre. None unless both distance and duration are known."""
        if self.distance_m <= 0 or self.duration_seconds <= 0:
            return None
        return round(self.duration_seconds / (self.distance_m / 1000), 1)


def fmt_duration(seconds: int) -> str:
    """1500 -> '25 min'; 3900 -> '1h 05m'; 45 -> '45s'."""
    if seconds <= 0:
        return "—"
    hours, rest = divmod(int(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes} min" + (f" {secs}s" if secs else "")
    return f"{secs}s"


def fmt_distance(metres: float) -> str:
    if metres <= 0:
        return "—"
    return f"{metres / 1000:.2f} km" if metres >= 1000 else f"{metres:.0f} m"


def fmt_pace(sec_per_km: float | None) -> str | None:
    if not sec_per_km:
        return None
    minutes, seconds = divmod(int(round(sec_per_km)), 60)
    return f"{minutes}:{seconds:02d} /km"


def describe(result: CardioResult) -> str:
    """One line of what was actually done, omitting anything not recorded."""
    p = result.parsed
    bits: list[str] = []

    if p.interval_rounds and p.interval_work_seconds:
        work = fmt_duration(p.interval_work_seconds)
        rest = fmt_duration(p.interval_rest_seconds) if p.interval_rest_seconds else None
        bits.append(
            f"{p.interval_rounds} x {work}" + (f" on / {rest} off" if rest else "")
        )

    if result.duration_seconds:
        label = "work" if p.interval_rounds else None
        bits.append(fmt_duration(result.duration_seconds) + (f" {label}" if label else ""))
    if result.distance_m:
        bits.append(fmt_distance(result.distance_m))

    pace = fmt_pace(result.pace_sec_per_km)
    if pace:
        bits.append(pace)

    settings = []
    if p.incline_pct is not None:
        settings.append(f"{p.incline_pct:g}% incline")
    if p.speed_kph is not None:
        settings.append(f"{p.speed_kph:g} kph")
    if p.resistance_level is not None:
        settings.append(f"resistance {p.resistance_level:g}")
    if settings:
        bits.append(" @ ".join(settings))

    effort = []
    if p.avg_heart_rate:
        effort.append(f"avg HR {p.avg_heart_rate}")
    if p.max_heart_rate:
        effort.append(f"max HR {p.max_heart_rate}")
    if p.rpe:
        effort.append(f"RPE {p.rpe:g}")
    if effort:
        bits.append(", ".join(effort))

    return " · ".join(bits) if bits else "logged, no numbers given"


def to_row(result: CardioResult) -> dict:
    """A workout_exercises row for cardio.

    weight/reps/sets/volume_load stay at 0: sets x reps x weight has no meaning
    here, and leaving volume_load at 0 keeps cardio out of resistance totals.
    """
    p = result.parsed
    return {
        "exercise_name": result.logged_name,
        "kind": "cardio",
        "source": "manual",
        "weight": 0,
        "reps": 0,
        "sets": 0,
        "volume_load": 0,
        "set_number": 1,
        "duration_seconds": p.duration_seconds,
        "distance_m": p.distance_m,
        "avg_heart_rate": p.avg_heart_rate,
        "max_heart_rate": p.max_heart_rate,
        "rpe": p.rpe,
        "incline_pct": p.incline_pct,
        "speed_kph": p.speed_kph,
        "resistance_level": p.resistance_level,
        "interval_work_seconds": p.interval_work_seconds,
        "interval_rest_seconds": p.interval_rest_seconds,
        "interval_rounds": p.interval_rounds,
    }


def from_row(row: dict) -> CardioResult:
    """Rebuild a CardioResult from a stored row, for history and weekly reports."""
    return CardioResult(
        logged_name=row["exercise_name"],
        parsed=parsing.ParsedCardio(
            raw_name=row["exercise_name"],
            duration_seconds=row.get("duration_seconds"),
            distance_m=float(row["distance_m"]) if row.get("distance_m") is not None else None,
            avg_heart_rate=row.get("avg_heart_rate"),
            max_heart_rate=row.get("max_heart_rate"),
            rpe=float(row["rpe"]) if row.get("rpe") is not None else None,
            incline_pct=float(row["incline_pct"]) if row.get("incline_pct") is not None else None,
            speed_kph=float(row["speed_kph"]) if row.get("speed_kph") is not None else None,
            resistance_level=(
                float(row["resistance_level"]) if row.get("resistance_level") is not None else None
            ),
            interval_work_seconds=row.get("interval_work_seconds"),
            interval_rest_seconds=row.get("interval_rest_seconds"),
            interval_rounds=row.get("interval_rounds"),
        ),
    )


@dataclass(frozen=True)
class CardioComparison:
    last_date: str
    duration_delta: int
    distance_delta: float
    pace_delta: float | None


def compare(result: CardioResult, previous_rows: list[dict], last_date: str) -> CardioComparison | None:
    """Change vs the previous session of the same activity.

    Pace improving means seconds-per-km going DOWN, so the sign is inverted when
    reported — a negative pace_delta is faster.
    """
    if not previous_rows:
        return None
    before = from_row(previous_rows[0])
    pace_now, pace_then = result.pace_sec_per_km, before.pace_sec_per_km
    return CardioComparison(
        last_date=last_date,
        duration_delta=result.duration_seconds - before.duration_seconds,
        distance_delta=round(result.distance_m - before.distance_m, 1),
        pace_delta=round(pace_now - pace_then, 1) if pace_now and pace_then else None,
    )
