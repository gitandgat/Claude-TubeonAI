"""Session analysis: parse a typed session, resolve lifts, compute the numbers, log it.

    python3 workout.py "bench 3x8 @ 80kg, squat 5,5,5 @ 100"
    python3 workout.py --dry-run "pullups 3x12 bodyweight"
    python3 workout.py --week
    python3 workout.py --pr "barbell bench press"

Deliberately absent: calories burned. Resistance-training energy expenditure
estimates carry error bars wide enough to be useless, and a wrong number here
would feed straight into the nutrition bot's targets. Volume load and the 1RM
trend are the signals that actually move.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

import config
import library
import metrics
import parsing
import profile
import store
import targets

log = logging.getLogger("workout-agent")

WEEK_DAYS = 7


@dataclass
class ExerciseOutcome:
    """One exercise, fully evaluated against history."""

    result: metrics.ExerciseResult
    pr: metrics.PRCheck
    comparison: metrics.Comparison | None


@dataclass
class SessionReport:
    outcomes: list[ExerciseOutcome]
    unmatched: list[str]
    bodyweight_kg: float | None
    workout_id: str | None = None
    logged: bool = False

    @property
    def total_volume_load(self) -> float:
        return round(sum(o.result.total_volume_load for o in self.outcomes), 2)

    @property
    def total_sets(self) -> int:
        return sum(o.result.set_count for o in self.outcomes)


def _load_for(parsed_set: parsing.ParsedSet, bodyweight: float | None) -> float:
    """Resolve a set's actual load in kg.

    Bodyweight lifts use bodyweight as the load, plus anything added. Without a
    stored bodyweight the load is 0 — honest, and the caller warns about it rather
    than inventing a number.
    """
    if not parsed_set.is_bodyweight:
        return metrics.to_kg(parsed_set.weight, parsed_set.unit)

    base = bodyweight or 0.0
    # A weighted bodyweight set may arrive as added_weight, or as weight when the
    # model put the extra load in the obvious field.
    extra = parsed_set.added_weight or parsed_set.weight
    return round(base + metrics.to_kg(extra, parsed_set.unit), 2)


def analyze(text: str, when: date | None = None) -> SessionReport:
    """Parse and evaluate a session WITHOUT writing anything."""
    when = when or date.today()
    parsed = parsing.parse_session(text)

    lib = library.ExerciseLibrary(store.fetch_library())
    resolutions = library.disambiguate([lib.resolve(p.raw_name) for p in parsed])

    user_id = config.user_id()
    records = store.get_records(user_id)
    bodyweight = profile.bodyweight_kg()

    outcomes: list[ExerciseOutcome] = []
    unmatched: list[str] = []

    for parsed_exercise, resolution in zip(parsed, resolutions):
        row = resolution.row
        logged_name = resolution.name
        if row is None:
            unmatched.append(parsed_exercise.raw_name)

        sets = tuple(
            metrics.SetEntry(
                reps=s.reps,
                weight_kg=_load_for(s, bodyweight),
                is_bodyweight=s.is_bodyweight,
            )
            for s in parsed_exercise.sets
        )
        result = metrics.ExerciseResult(
            logged_name=logged_name,
            sets=sets,
            library_name=row["exercise_name"] if row else None,
            muscle_groups=tuple(row.get("muscle_groups") or []) if row else (),
            movement_pattern=(row.get("movement_pattern") if row else None),
            raw_input=parsed_exercise.raw_name,
        )

        pr = metrics.check_pr(result, records.get(logged_name))
        outcomes.append(
            ExerciseOutcome(result=result, pr=pr, comparison=_previous(user_id, result, when))
        )

    return SessionReport(
        outcomes=outcomes, unmatched=unmatched, bodyweight_kg=bodyweight
    )


def _previous(
    user_id: str, result: metrics.ExerciseResult, when: date
) -> metrics.Comparison | None:
    """Compare against the most recent EARLIER session of this lift.

    Sessions on `when` are excluded so logging twice in one day doesn't make the
    morning session the baseline for the evening one.
    """
    history = store.sets_for_exercise(user_id, result.logged_name)
    earlier = [r for r in history if r["workouts"]["date"] < when.isoformat()]
    if not earlier:
        return None
    last_date = earlier[0]["workouts"]["date"]
    same_day = [r for r in earlier if r["workouts"]["date"] == last_date]
    return metrics.compare_to_previous(result, same_day, last_date)


def log_session(report: SessionReport, text: str, when: date | None = None) -> SessionReport:
    """Persist the session and update personal records.

    The sets are written after the workout row, so a failure between the two would
    leave an empty session in history that every later comparison would read as a
    real training day. That half-write is rolled back rather than left behind.
    """
    when = when or date.today()
    user_id = config.user_id()
    store.ensure_profile(user_id)

    workout_id = store.insert_workout(user_id, when, text, report.total_volume_load)
    try:
        rows: list[dict] = []
        for outcome in report.outcomes:
            for index, entry in enumerate(outcome.result.sets, start=1):
                rows.append(
                    {
                        "exercise_name": outcome.result.logged_name,
                        "weight": entry.weight_kg,
                        "reps": entry.reps,
                        "sets": config.SETS_PER_ROW,
                        "volume_load": entry.volume_load,
                        "set_number": index,
                    }
                )
        store.insert_sets(workout_id, rows)
    except Exception:
        log.exception("Set insert failed; rolling back workout %s", workout_id)
        store.delete_workout(workout_id)
        raise

    achieved_at = datetime.now(timezone.utc).isoformat()
    for outcome in report.outcomes:
        if outcome.pr.any_pr:
            store.upsert_record(
                user_id,
                outcome.result.logged_name,
                outcome.pr.new_max_weight,
                outcome.pr.new_max_volume,
                achieved_at,
            )

    report.workout_id = workout_id
    report.logged = True
    return report


# --- formatting -------------------------------------------------------------

def _md(text: str) -> str:
    """Exercise names can come from free text, so neutralise Telegram Markdown."""
    for ch in "_*`[":
        text = text.replace(ch, "\\" + ch)
    return text


def _sets_summary(result: metrics.ExerciseResult) -> str:
    """Compact set notation: 3x8 @ 80kg, or 5/5/3 @ 100kg when reps vary."""
    reps = [s.reps for s in result.sets]
    weights = {s.weight_kg for s in result.sets}
    load = f"{result.top_weight:g}kg" if result.top_weight else "bodyweight"

    if len(set(reps)) == 1 and len(weights) == 1:
        return f"{len(reps)}x{reps[0]} @ {load}"
    if len(weights) == 1:
        return f"{'/'.join(map(str, reps))} @ {load}"
    return ", ".join(f"{s.reps}@{s.weight_kg:g}kg" for s in result.sets)


def format_session(report: SessionReport) -> str:
    # The header must not claim a write that did not happen — a dry run and a
    # logged session are easy to confuse once the output looks identical.
    heading = "Session logged" if report.logged else "Session analysed (not logged)"
    lines = [f"*{heading}* — {report.total_sets} sets, {report.total_volume_load:,.0f} kg total volume"]

    for outcome in report.outcomes:
        result, pr, comp = outcome.result, outcome.pr, outcome.comparison
        name = _md(result.logged_name)
        flag = "" if result.in_library else "  ⚠️ not in library"
        lines += ["", f"*{name}*{flag}", f"{_sets_summary(result)} · {result.total_volume_load:,.0f} kg volume"]

        if result.best_1rm:
            lines.append(f"est. 1RM {result.best_1rm:g} kg")

        if pr.is_first_record:
            lines.append("_first time logged — this is now the baseline_")
        elif pr.any_pr:
            badges = []
            if pr.weight_pr:
                badges.append(f"weight PR ({pr.previous_max_weight:g} → {pr.new_max_weight:g} kg)")
            if pr.volume_pr:
                badges.append(f"volume PR ({pr.previous_max_volume:,.0f} → {pr.new_max_volume:,.0f} kg)")
            lines.append("🏆 " + " · ".join(badges))

        if comp:
            arrow = "▲" if comp.volume_delta > 0 else ("▼" if comp.volume_delta < 0 else "=")
            lines.append(
                f"vs {comp.last_date}: {arrow} {comp.volume_delta:+,.0f} kg "
                f"({comp.volume_pct:+.0f}%) · top weight {comp.top_weight_delta:+g} kg"
            )
        elif not pr.is_first_record:
            lines.append("_no earlier session of this lift to compare_")

    if report.unmatched:
        lines += [
            "",
            f"_Not in the exercise library, logged under the name you used: "
            f"{_md(', '.join(report.unmatched))}_",
        ]

    if any(s.is_bodyweight for o in report.outcomes for s in o.result.sets) and not report.bodyweight_kg:
        lines += ["", "_Bodyweight sets counted at 0 load — set it with /bodyweight 85_"]

    return "\n".join(lines)


def _muscle_volume(rows: list[dict], lib: library.ExerciseLibrary) -> tuple[dict, dict, list[str]]:
    """Set credit and volume load per muscle group, plus glute loading vectors."""
    by_group: dict[str, dict[str, float]] = {}
    vectors: dict[str, float] = {}
    unclassified: list[str] = []

    for row in rows:
        name = row["exercise_name"]
        entry = lib.by_name(name) or lib.resolve(name).row
        set_count = int(row.get("sets") or 1)
        volume = float(row.get("volume_load") or 0)

        if not entry:
            if name not in unclassified:
                unclassified.append(name)
            continue

        for group, credit in targets.credit_for(entry.get("muscle_groups") or []).items():
            bucket = by_group.setdefault(group, {"sets": 0.0, "volume": 0.0})
            bucket["sets"] += credit * set_count
            bucket["volume"] += volume * credit

        vector = targets.glute_vector(entry)
        if vector:
            vectors[vector] = vectors.get(vector, 0.0) + set_count

    return by_group, vectors, unclassified


def format_week(when: date | None = None) -> str:
    when = when or date.today()
    start = when - timedelta(days=WEEK_DAYS - 1)
    user_id = config.user_id()

    rows = store.sets_in_range(user_id, start, when)
    if not rows:
        return f"No sets logged between {start.isoformat()} and {when.isoformat()}."

    lib = library.ExerciseLibrary(store.fetch_library())
    by_group, vectors, unclassified = _muscle_volume(rows, lib)

    previous_rows = store.sets_in_range(
        user_id, start - timedelta(days=WEEK_DAYS), start - timedelta(days=1)
    )
    previous_groups, _, _ = _muscle_volume(previous_rows, lib)

    total_volume = sum(float(r.get("volume_load") or 0) for r in rows)
    days = len({r["workouts"]["date"] for r in rows})

    lines = [
        f"*Last {WEEK_DAYS} days* — {start.isoformat()} to {when.isoformat()}",
        f"{days} training days · {len(rows)} sets · {total_volume:,.0f} kg total volume",
        "",
        "*Sets by muscle group* (primary 1.0, secondary 0.5)",
    ]

    ordered = sorted(by_group.items(), key=lambda kv: kv[1]["sets"], reverse=True)
    for group, stats in ordered:
        target = targets.target_for(group)
        before = previous_groups.get(group, {}).get("sets", 0.0)
        delta = stats["sets"] - before
        trend = f" ({delta:+.1f} vs prior week)" if before else ""
        if target:
            pct = stats["sets"] / target * 100
            mark = "✅" if pct >= 100 else ("🟡" if pct >= 70 else "🔴")
            lines.append(
                f"{mark} {group}: {stats['sets']:.1f} / {target} sets ({pct:.0f}%)"
                f" · {stats['volume']:,.0f} kg{trend}"
            )
        else:
            lines.append(f"• {group}: {stats['sets']:.1f} sets · {stats['volume']:,.0f} kg{trend}")

    if vectors:
        lines += ["", "*Glute loading vectors* (Contreras)"]
        for key, (label, vector_target) in targets.GLUTE_VECTORS.items():
            done = vectors.get(key, 0.0)
            mark = "✅" if done >= vector_target else ("🟡" if done >= vector_target * 0.7 else "🔴")
            lines.append(f"{mark} {label}: {done:.0f} / {vector_target} sets")

    if unclassified:
        lines += ["", f"_Not in the library, uncounted: {_md(', '.join(unclassified))}_"]

    return "\n".join(lines)


def format_today(when: date | None = None) -> str:
    when = when or date.today()
    user_id = config.user_id()
    rows = store.sets_in_range(user_id, when, when)
    if not rows:
        return "Nothing logged yet today."

    by_exercise: dict[str, list[dict]] = {}
    for row in rows:
        by_exercise.setdefault(row["exercise_name"], []).append(row)

    total = sum(float(r.get("volume_load") or 0) for r in rows)
    lines = [
        f"*Today* — {len(by_exercise)} lifts, {len(rows)} sets, {total:,.0f} kg volume",
        "",
    ]
    for name, sets in by_exercise.items():
        result = metrics.ExerciseResult(
            logged_name=name,
            sets=tuple(
                metrics.SetEntry(reps=int(s["reps"]), weight_kg=float(s["weight"])) for s in sets
            ),
        )
        lines.append(
            f"*{_md(name)}* — {_sets_summary(result)} · {result.total_volume_load:,.0f} kg"
            + (f" · est. 1RM {result.best_1rm:g} kg" if result.best_1rm else "")
        )
    return "\n".join(lines)


def format_pr(query: str) -> str:
    user_id = config.user_id()
    lib = library.ExerciseLibrary(store.fetch_library())
    resolution = lib.resolve(query)
    if not resolution.matched and resolution.candidates:
        resolution = library.disambiguate([resolution])[0]
    name = resolution.name

    history = store.sets_for_exercise(user_id, name)
    if not history:
        hint = "" if resolution.matched else " (and it isn't in the exercise library)"
        return f"No history for *{_md(name)}* yet{hint}."

    by_date: dict[str, list[dict]] = {}
    for row in history:
        by_date.setdefault(row["workouts"]["date"], []).append(row)

    record = store.get_records(user_id).get(name)
    lines = [f"*{_md(name)}* — {len(by_date)} sessions"]
    if record:
        lines.append(
            f"PR: {float(record['max_weight']):g} kg top set · "
            f"{float(record['max_volume']):,.0f} kg session volume"
        )
    lines.append("")

    for session_date in sorted(by_date, reverse=True)[:12]:
        sets = by_date[session_date]
        result = metrics.ExerciseResult(
            logged_name=name,
            sets=tuple(
                metrics.SetEntry(reps=int(s["reps"]), weight_kg=float(s["weight"])) for s in sets
            ),
        )
        lines.append(
            f"{session_date}: {_sets_summary(result)} · {result.total_volume_load:,.0f} kg"
            + (f" · 1RM {result.best_1rm:g}" if result.best_1rm else "")
        )
    return "\n".join(lines)


# --- CLI --------------------------------------------------------------------

def _init() -> None:
    """One-time setup: create the user_profiles row the workouts FK needs."""
    user_id = config.user_id()
    row = store.ensure_profile(user_id)
    bodyweight = profile.bodyweight_kg()
    print(f"Profile ready: {row['id']} ({row.get('name')}, {row.get('weight_unit')})")
    print(f"Library: {len(store.fetch_library())} exercises")
    print(f"Bodyweight: {bodyweight or 'NOT SET — run with --bodyweight <kg>'}")


def main() -> None:
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser(description="Log a training session and track progress.")
    parser.add_argument("session", nargs="?", help="e.g. 'bench 3x8 @ 80kg, squat 5,5,5 @ 100'")
    parser.add_argument("--dry-run", action="store_true", help="Analyse without writing")
    parser.add_argument("--today", action="store_true", help="Today's session summary")
    parser.add_argument("--week", action="store_true", help="Volume by muscle group")
    parser.add_argument("--pr", metavar="EXERCISE", help="History for one lift")
    parser.add_argument("--bodyweight", type=float, metavar="KG", help="Store bodyweight in kg")
    parser.add_argument("--init", action="store_true", help="Create the profile row and self-check")
    args = parser.parse_args()

    if args.bodyweight:
        print(f"Bodyweight set to {profile.set_bodyweight_kg(args.bodyweight)} kg")
        return
    if args.init:
        _init()
        return
    if args.today:
        print(format_today())
        return
    if args.week:
        print(format_week())
        return
    if args.pr:
        print(format_pr(args.pr))
        return
    if not args.session:
        parser.error("give a session, or one of --today/--week/--pr/--bodyweight/--init")

    report = analyze(args.session)
    if not args.dry_run:
        report = log_session(report, args.session)
    print(format_session(report))
    if args.dry_run:
        print("\n(dry run — nothing written)", file=sys.stderr)


if __name__ == "__main__":
    main()
