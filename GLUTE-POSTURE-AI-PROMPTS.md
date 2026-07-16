# Glute Longevity — Posture-Corrective AI Prompt System (Reusable)

Reusable system for generating **glute-focused, posture-correcting** workouts for the ideal client and any variation of them. The meta-prompt outputs a clean exercise list you build in **FitPros** (drag from its HD library; see [GLUTE-FITPROS-BUILD.md](GLUTE-FITPROS-BUILD.md)) — or paste into any platform's AI builder. This is the per-client engine behind the worked 6-week program below.

**Honest framing (use this language with clients):** this is *corrective exercise* — it strengthens the weak muscles and lengthens the tight ones that drive these postures, and trains better habitual alignment. It improves functional posture and reduces strain; it does not "reverse" a fixed structural curve. Anyone with pain, a diagnosed structural condition, or red flags should be cleared by a clinician first.

---

## Ideal client → what's actually happening

| Client finding | Pattern | Tight / overactive (lengthen) | Weak / inhibited (strengthen) |
|---|---|---|---|
| Lumbar lordosis / anterior pelvic tilt | **Lower-crossed** | Hip flexors, lumbar erectors | **Glutes**, deep core (anti-extension) |
| Forward head posture | **Upper-crossed** | Suboccipitals, upper traps, levator | Deep neck flexors |
| Rounded shoulders + thoracic kyphosis | **Upper-crossed** | Pecs, lats | Mid/lower traps, rhomboids, thoracic extensors |

The glute emphasis *is* the lower-crossed fix. We add upper-back + neck correctives for the upper-crossed half.

---

## Corrective menu (the exercise vocabulary the AI pulls from)

**Lengthen / mobilize (tight structures)**
- Hip flexors → `Kneeling Hip Flexor Stretch`, `Couch Stretch`, `90/90 Hip Switch`
- Lumbar erectors → `Child's Pose`, `Cat-Cow`
- Pecs / lats → `Doorway Pec Stretch`, `Lat Stretch`
- Thoracic spine → `Thoracic Extension on Foam Roller`, `Thread the Needle`
- Neck → `Upper Trap Stretch`, `Levator Scapulae Stretch`

**Strengthen / activate (weak structures)**
- Glutes (brand core) → `Glute Bridge`, `Hip Thrust`, `Standing Hip Abduction`, `Clamshell`, `Single Leg Romanian Deadlift`, `Lateral Band Walk`, `Split Squat`, `Step Up`
- Deep core / anti-lordosis → `Dead Bug`, `Plank`, `Hollow Body Hold`, `Pallof Press`, `Posterior Pelvic Tilt`, `Bird Dog`
- Mid/lower trap + rhomboids → `Band Pull-Apart`, `Face Pull`, `Prone Y Raise`, `Prone T Raise`, `Prone W Raise`, `Bent Over Row`, `Scapular Wall Slide`
- Thoracic extensors → `Prone Cobra`, `Wall Slide`
- Deep neck flexors → `Chin Tuck`, `Standing Chin Tuck with Band`

---

## The reusable meta-prompt (give this to your AI per client)

Fill the `{{...}}` slots; your AI returns a clean workout list. Drag those exercises into FitPros (or paste into any AI builder).

```
You are a corrective-exercise coach for the Glute Longevity method. Generate ONE workout for the client below.

CLIENT:
- Level: {{beginner | intermediate}}
- Postural findings: {{e.g. forward head, rounded shoulders, thoracic kyphosis, lumbar lordosis / anterior pelvic tilt}}
- Equipment: {{bodyweight + resistance band; dumbbells optional}}
- Day focus: {{A = glutes + thoracic/scapular | B = hinge/posterior chain + rows + anti-lordosis core | C = single-leg/posture + neck + carry}}
- Week (1-6 progression): {{n}}  // 1-2 activation/low load, 3-4 controlled load, 5 power/tempo, 6 consolidate

RULES (always, in this order):
1. One MOBILITY/RELEASE for a TIGHT structure from the findings.
2. Glute ACTIVATION.
3. One or two GLUTE STRENGTH moves (the priority).
4. One POSTURAL-STRENGTH move for a WEAK muscle from the findings (upper back / scapula / thoracic).
5. One ANTI-LORDOSIS CORE or DEEP-NECK-FLEXOR move.
6. A POSTURE HOLD / finisher.

CONSTRAINTS: joint-friendly; emphasize glutes + correct the listed faults; only use exercises from the Corrective Menu; add an easier regression in parentheses if helpful.
OUTPUT: exercises only, one per line — `Exercise Name SETSxREPS (each side) tempo X-X-X, rest for N seconds`. No prose.
```
(Append the Corrective Menu above so the AI stays on-vocabulary.)

**Session skeleton** (the reusable shape every day follows): `release → glute activation → glute strength → postural strength → anti-lordosis core/neck → posture hold`.

---

## Worked example — full 6-week posture-corrective program

A/B/C split, 3 days/week. Every day follows the skeleton. Paste each block into the AI Builder.

### WEEK 1 — Wake & align
**W1 · Day A — Glutes + thoracic**
```
Thoracic Extension on Foam Roller 2x8, rest for 30 seconds
Glute Bridge 3x12 tempo 2-2-1, rest for 45 seconds
Box Squat 3x10 tempo 3-1-1, rest for 60 seconds
Band Pull-Apart 3x15, rest for 30 seconds
Dead Bug 2x8 (each side), rest for 30 seconds
Prone Cobra 2x20 seconds, rest for 30 seconds
```
**W1 · Day B — Hinge + rows + core**
```
Kneeling Hip Flexor Stretch 2x30 seconds (each side)
Clamshell 3x12 (each side), rest for 30 seconds
Hip Hinge 3x10 tempo 3-1-1, rest for 60 seconds
Face Pull 3x15, rest for 30 seconds
Glute Bridge March 2x8 (each side), rest for 45 seconds
Bird Dog 2x8 (each side), rest for 30 seconds
```
**W1 · Day C — Single-leg + neck + carry**
```
Doorway Pec Stretch 2x30 seconds
Chin Tuck 3x10 tempo 2-2-1, rest for 20 seconds
Lateral Band Walk 3x10 (each side), rest for 30 seconds
Step Up 3x8 (each side), rest for 60 seconds
Scapular Wall Slide 3x10, rest for 30 seconds
Glute Bridge Hold 2x20 seconds, rest for 45 seconds
```

### WEEK 2 — Build the base
**W2 · Day A**
```
Thoracic Extension on Foam Roller 2x10, rest for 30 seconds
Glute Bridge 3x15 tempo 2-2-1, rest for 45 seconds
Box Squat 3x12 tempo 3-1-1, rest for 60 seconds
Band Pull-Apart 3x20, rest for 30 seconds
Dead Bug 3x8 (each side), rest for 30 seconds
Prone Cobra 2x25 seconds, rest for 30 seconds
```
**W2 · Day B**
```
Kneeling Hip Flexor Stretch 2x30 seconds (each side)
Banded Clamshell 3x12 (each side), rest for 30 seconds
Banded Good Morning 3x10 tempo 3-1-1, rest for 60 seconds
Face Pull 3x15, rest for 30 seconds
Glute Bridge March 3x8 (each side), rest for 45 seconds
Bird Dog 3x8 (each side), rest for 30 seconds
```
**W2 · Day C**
```
Doorway Pec Stretch 2x30 seconds
Standing Chin Tuck 3x12, rest for 20 seconds
Lateral Band Walk 3x12 (each side), rest for 30 seconds
Step Up 3x10 (each side), rest for 60 seconds
Prone Y Raise 3x12, rest for 30 seconds
Glute Bridge Hold 3x20 seconds, rest for 45 seconds
```

### WEEK 3 — Load with control
**W3 · Day A**
```
Thoracic Extension on Foam Roller 2x10, rest for 30 seconds
Goblet Squat 3x10 tempo 3-1-1, rest for 75 seconds
Hip Thrust 3x12, rest for 75 seconds
Band Pull-Apart 3x20, rest for 30 seconds
Dead Bug 3x10 (each side), rest for 30 seconds
Prone Cobra 3x25 seconds, rest for 30 seconds
```
**W3 · Day B**
```
Kneeling Hip Flexor Stretch 2x30 seconds (each side)
Single Leg Romanian Deadlift 3x8 (each side), rest for 75 seconds
Hip Thrust 3x12, rest for 75 seconds
Face Pull 3x15, rest for 45 seconds
Banded Clamshell 3x12 (each side), rest for 30 seconds
Plank 3x30 seconds, rest for 30 seconds
```
**W3 · Day C**
```
Doorway Pec Stretch 2x30 seconds
Standing Chin Tuck 3x12, rest for 20 seconds
Goblet Box Squat 3x10, rest for 60 seconds
Step Up 3x10 (each side), rest for 60 seconds
Prone Y Raise 3x12, rest for 30 seconds
Side Plank 2x20 seconds (each side), rest for 30 seconds
```

### WEEK 4 — Posture & carry
**W4 · Day A**
```
Thoracic Extension on Foam Roller 2x10, rest for 30 seconds
Split Squat 3x8 (each side), rest for 75 seconds
Hip Thrust 3x12, rest for 75 seconds
Face Pull 3x15, rest for 45 seconds
Standing Hip Abduction 3x12 (each side), rest for 30 seconds
Prone Cobra 3x30 seconds, rest for 30 seconds
```
**W4 · Day B**
```
Kneeling Hip Flexor Stretch 2x30 seconds (each side)
Single Leg Romanian Deadlift 3x8 (each side), rest for 75 seconds
Suitcase Carry 3x20 meters (each side), rest for 60 seconds
Bent Over Row 3x10, rest for 60 seconds
Banded Clamshell 3x12 (each side), rest for 30 seconds
Dead Bug 2x10 (each side), rest for 30 seconds
```
**W4 · Day C**
```
Doorway Pec Stretch 2x30 seconds
Standing Chin Tuck 3x12, rest for 20 seconds
Goblet Squat 3x10 tempo 3-1-1, rest for 75 seconds
Suitcase Carry 3x20 meters (each side), rest for 60 seconds
Prone T Raise 3x12, rest for 30 seconds
Side Plank 2x25 seconds (each side), rest for 30 seconds
```

### WEEK 5 — Power & resilience
**W5 · Day A**
```
Thoracic Extension on Foam Roller 2x10, rest for 30 seconds
Tempo Goblet Squat 4x8 tempo 4-1-1, rest for 90 seconds
B Stance Hip Thrust 3x10 (each side), rest for 75 seconds
Face Pull 3x15, rest for 45 seconds
Pallof Press 3x10 (each side), rest for 30 seconds
Prone Cobra 3x30 seconds, rest for 30 seconds
```
**W5 · Day B**
```
Kneeling Hip Flexor Stretch 2x30 seconds (each side)
Single Leg Romanian Deadlift 3x10 (each side), rest for 90 seconds
B Stance Hip Thrust 3x10 (each side), rest for 75 seconds
Bent Over Row 3x10, rest for 60 seconds
Banded Clamshell 3x12 (each side), rest for 30 seconds
Hollow Body Hold 3x20 seconds, rest for 30 seconds
```
**W5 · Day C**
```
Doorway Pec Stretch 2x30 seconds
Standing Chin Tuck with Band 3x12, rest for 20 seconds
Tempo Split Squat 3x8 (each side) tempo 4-1-1, rest for 75 seconds
Step Down 3x8 (each side), rest for 60 seconds
Prone W Raise 3x12, rest for 30 seconds
Side Plank 2x30 seconds (each side), rest for 30 seconds
```

### WEEK 6 — Make it last
**W6 · Day A**
```
Thoracic Extension on Foam Roller 2x10, rest for 30 seconds
Goblet Squat 3x10, rest for 75 seconds
Hip Thrust 3x12, rest for 75 seconds
Band Pull-Apart 3x20, rest for 30 seconds
Dead Bug 3x10 (each side), rest for 30 seconds
Prone Cobra 3x30 seconds, rest for 30 seconds
```
**W6 · Day B**
```
Kneeling Hip Flexor Stretch 2x30 seconds (each side)
Single Leg Romanian Deadlift 3x8 (each side), rest for 75 seconds
Reverse Lunge 3x8 (each side), rest for 60 seconds
Face Pull 3x15, rest for 45 seconds
Banded Clamshell 3x12 (each side), rest for 30 seconds
Plank 3x40 seconds, rest for 30 seconds
```
**W6 · Day C**
```
Doorway Pec Stretch 2x30 seconds
Standing Chin Tuck 3x12, rest for 20 seconds
Reverse Lunge 3x8 (each side), rest for 60 seconds
Hip Thrust 3x12, rest for 75 seconds
Prone Y Raise 3x12, rest for 30 seconds
Glute Bridge Hold 2x30 seconds, rest for 45 seconds
```

---

## How to reuse per client
- **Same posture, different equipment/level/days:** change the meta-prompt slots, regenerate.
- **Different posture mix** (e.g. only rounded shoulders, no lordosis): keep glute base, swap the postural-strength + release lines to that fault's row in the menu.
- **Maintenance after Week 6:** 1 squat + 1 hinge + 1 row/face pull + 1 thoracic extension, 2x/week.
