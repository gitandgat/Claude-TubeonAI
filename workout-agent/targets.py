"""Weekly set targets per muscle group, weighted toward glutes and lower body.

These are POPULATION guidelines from the training literature, not claims about
Sahawat's body or any assessment of him:

* Schoenfeld, Ogborn & Krieger (2017) dose-response meta-analysis — hypertrophy
  scales with weekly set volume, with gains continuing past 10 sets/muscle/week
  for trained lifters. 10 is the floor for growth; ~4-6 is maintenance.
* Contreras's glute work — the glutes are trained across three LOADING VECTORS,
  and a programme biased to only one leaves the others undertrained:
    - axial / vertical  (spinal loading)      -> squat pattern
    - anteroposterior   (horizontal resistance) -> hinge pattern (hip thrust, RDL,
      back extension); the vector he argues is most commonly missing
    - lateral / rotary  (abduction, rotation) -> unilateral + abductor work
  He also argues for high glute frequency (2-4x/week) and a spread of rep ranges,
  because the glutes tolerate and respond to heavy, moderate and metabolic work.

Edit TARGETS freely — it is plain data, and nothing else reads meaning into the
numbers. Set a value to None to track a group's volume without a target line.
"""

from __future__ import annotations

# The library uses 27 distinct muscle_groups labels; these fold the synonyms and
# the near-duplicates into groups worth reporting on. Keys are the raw labels as
# they appear in exercise_library.muscle_groups, so nothing here is invented.
MUSCLE_ALIASES = {
    "upper chest": "chest",
    "anterior deltoids": "shoulders",
    "rear deltoids": "shoulders",
    "rotator cuff": "shoulders",
    "obliques": "core",
    "hip flexors": "core",
    "lats": "back",
    "rhomboids": "back",
    "upper back": "back",
    "traps": "back",
    "back": "back",
    "arms": "arms",
}

# Weekly set targets. Lower body is the priority, so it sits in the upper half of
# the dose-response range; upper body sits at the growth floor to be maintained
# rather than maximised.
TARGETS: dict[str, int | None] = {
    # Priority — glutes and lower body
    "glutes": 20,
    "hamstrings": 16,
    "quadriceps": 16,
    "adductors": 8,
    # 4, not 8: no exercise in the library lists "hip abductors" first (both
    # abduction machines put glutes primary), so this group can only ever earn
    # half credit — a target of 8 would silently demand 16 real sets a week.
    "hip abductors": 4,
    "calves": 10,
    "lower back": 10,
    # Maintained, not maximised
    "back": 12,
    "chest": 10,
    "shoulders": 10,
    "biceps": 8,
    "triceps": 8,
    "core": 10,
    # Tracked without a target — too vague or incidental to program against
    "grip": None,
    "legs": None,
    "arms": None,
    "cardio": None,
}

# Contreras's three glute loading vectors, derived from the live library rather
# than assumed. Weekly set targets, and the order they are reported in.
#
# Classification is NOT a straight movement_pattern lookup. The library marks all
# 13 single-leg exercises "unilateral", but a lunge, step-up or pistol squat is
# axially loaded — calling those "lateral" would overstate that vector and hide
# the gap Contreras actually warns about. True lateral/rotary work is abduction,
# which the library identifies by a "hip abductors" muscle group (Hip Abduction
# Machine and Cable Hip Abduction, both of which it happens to tag "unilateral").
GLUTE_VECTORS = {
    "anteroposterior": ("Anteroposterior", 8),
    "axial": ("Axial", 6),
    "lateral": ("Lateral / rotary", 4),
}

# Bulgarian Split Squat is pattern "squat" in the library, so single-leg squats
# already land in axial; the unilateral pattern is folded there too for the same
# reason (loaded along the spine, not across the hip).
AXIAL_PATTERNS = {"squat", "unilateral"}
ANTEROPOSTERIOR_PATTERNS = {"hinge"}


def glute_vector(entry: dict) -> str | None:
    """Which loading vector one glute exercise trains, or None if it isn't glute work."""
    muscles = entry.get("muscle_groups") or []
    if "glutes" not in muscles:
        return None
    # Abduction first: it is the vector most often missing, and its exercises are
    # tagged with a pattern that would otherwise swallow them into axial.
    if "hip abductors" in muscles:
        return "lateral"
    pattern = entry.get("movement_pattern")
    if pattern in ANTEROPOSTERIOR_PATTERNS:
        return "anteroposterior"
    if pattern in AXIAL_PATTERNS:
        return "axial"
    return None

# A set of Barbell Back Squat is not a full set for the hamstrings. muscle_groups
# is ordered primary-first in the library, so the first label takes full credit
# and the rest take half — the direct/indirect convention used in the volume
# literature, rather than counting every incidental muscle as a full set.
PRIMARY_CREDIT = 1.0
SECONDARY_CREDIT = 0.5


def canonical(muscle: str) -> str:
    """Fold a raw library label into its reporting group."""
    return MUSCLE_ALIASES.get(muscle, muscle)


def credit_for(muscle_groups: list[str]) -> dict[str, float]:
    """Set credit per reporting group for one set of an exercise.

    Folding can collide (chest + upper chest both map to chest); keep the larger
    credit so a primary never gets demoted to indirect by an alias.
    """
    credits: dict[str, float] = {}
    for index, raw in enumerate(muscle_groups):
        group = canonical(raw)
        credit = PRIMARY_CREDIT if index == 0 else SECONDARY_CREDIT
        credits[group] = max(credits.get(group, 0.0), credit)
    return credits


def target_for(group: str) -> int | None:
    return TARGETS.get(group)
