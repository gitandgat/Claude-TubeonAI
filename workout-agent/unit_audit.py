"""Audit the stored unit of every logged weight. Reads only — writes nothing.

Why this exists
---------------
`workout_exercises.weight` carried no unit until
20261028103000_add_weight_unit_provenance.sql. Two clients wrote it and they did
not agree: this agent has always normalised to kilograms, while the web app
inserted the number as typed and used `user_profiles.weight_unit` (default
'lbs') only as a display label. So some historical rows may be pounds sitting in
a kilogram column, which would mean wrong volume load, wrong Epley 1RM and wrong
PRs for every lift that mixes the two.

This script answers one question: are any stored rows actually pounds?

It never writes. The repair is a separate, explicit step, and it is only worth
building once this report says there is something to repair.

    ./.venv/bin/python3 unit_audit.py            # full report
    ./.venv/bin/python3 unit_audit.py --exercise "Barbell Bench Press"

Reading the output
------------------
  recorded kg / recorded lb   entered_unit is set — unambiguous, nothing to do.
  unrecorded                  entered_unit IS NULL: logged before the column
                              existed. Its unit is not knowable from the row
                              itself, so each one is tested against the lift's
                              own known-kilogram history.
  SUSPECT                     an unrecorded row whose weight sits near 2.2046x
                              the lift's known kg weights — the signature of a
                              pounds number stored unconverted.
"""

from __future__ import annotations

import argparse
import statistics
from collections import defaultdict

import config
import metrics
import store

# How close to the 2.2046 ratio an unrecorded row must sit before it is called
# out. Loads vary legitimately between sessions, so this is deliberately loose
# on the low side and anchored on the ratio rather than on absolute weight.
RATIO_TOLERANCE = 0.25
# Below this many kilograms, the lb/kg ratio stops discriminating: 20 lb and
# 9 kg dumbbells are both plausible, so the test says nothing useful.
MIN_KG_FOR_RATIO = 15.0


def _classify(rows: list[dict]) -> dict[str, list[dict]]:
    by_exercise: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_exercise[row["exercise_name"]].append(row)
    return by_exercise


def _report_exercise(name: str, rows: list[dict]) -> tuple[int, int]:
    """Print one lift's verdict. Returns (unrecorded, suspect) counts."""
    known_kg = [float(r["weight"]) for r in rows if r.get("entered_unit") == "kg"]
    known_lb = [r for r in rows if r.get("entered_unit") == "lb"]
    unrecorded = [r for r in rows if not r.get("entered_unit")]

    reference = statistics.median(known_kg) if known_kg else None
    suspects: list[dict] = []

    for row in unrecorded:
        weight = float(row["weight"])
        if reference is None or reference < MIN_KG_FOR_RATIO or weight <= 0:
            continue
        ratio = weight / reference
        if abs(ratio - config.LB_PER_KG) <= RATIO_TOLERANCE * config.LB_PER_KG:
            suspects.append({**row, "_ratio": ratio})

    print(f"\n{name}")
    print(
        f"  rows {len(rows):>4}   recorded kg {len(known_kg):>4}   "
        f"recorded lb {len(known_lb):>4}   unrecorded {len(unrecorded):>4}"
    )
    if reference is not None:
        print(f"  median known kg load: {reference:g} kg")
    elif unrecorded:
        print("  no kilogram-recorded rows for this lift — ratio test cannot run")

    for row in suspects:
        date = row["workouts"]["date"]
        weight = float(row["weight"])
        print(
            f"  SUSPECT {date}  {weight:g} stored  "
            f"({row['_ratio']:.2f}x median; = {metrics.to_kg(weight, 'lb'):g} kg if pounds)"
        )

    return len(unrecorded), len(suspects)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exercise", help="audit one lift only")
    args = parser.parse_args()

    user_id = config.user_id()
    rows = store.all_sets_with_units(user_id)
    if not rows:
        print("No resistance sets stored for this user — nothing to audit.")
        return

    by_exercise = _classify(rows)
    if args.exercise:
        wanted = args.exercise.lower()
        by_exercise = {k: v for k, v in by_exercise.items() if k.lower() == wanted}
        if not by_exercise:
            print(f"No stored sets named {args.exercise!r}.")
            return

    dates = sorted(r["workouts"]["date"] for r in rows)
    print(f"{len(rows)} resistance sets across {len(by_exercise)} lifts")
    print(f"first logged {dates[0]}, last logged {dates[-1]}")

    total_unrecorded = 0
    total_suspect = 0
    for name in sorted(by_exercise):
        unrecorded, suspect = _report_exercise(name, by_exercise[name])
        total_unrecorded += unrecorded
        total_suspect += suspect

    print("\n" + "=" * 62)
    print(f"unrecorded rows: {total_unrecorded}    flagged as likely pounds: {total_suspect}")
    if total_suspect:
        print(
            "\nThese rows look like pounds stored as kilograms. Nothing has been\n"
            "changed. Repairing them means converting the weight, recomputing\n"
            "volume_load and workouts.total_volume_load, and rebuilding\n"
            "personal_records from the corrected rows — in that order."
        )
    elif total_unrecorded:
        print(
            "\nNo row looks like pounds. The unrecorded rows are consistent with\n"
            "kilograms, so they can be stamped entered_unit='kg' with one update\n"
            "and no weight changes."
        )
    else:
        print("\nEvery row carries an explicit unit. Nothing to do.")


if __name__ == "__main__":
    main()
