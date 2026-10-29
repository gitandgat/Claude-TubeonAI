# Workout Agent

Telegram bot: type a training session, get volume load, estimated 1RM, PR flags, and
whether you're actually progressing against the last time you trained that lift.

Sibling to `nutrition-agent/` — same shape (analyzer + CLI, `bot.py`, `run_bot.sh`,
launchd plist), its own bot token, its own venv.

```
bench 3x8 @ 80kg, squat 5,5,5 @ 100, pullups 3x12 bodyweight
```

## Commands

| Command | What it does |
|---|---|
| *(any message)* | Logs the session and replies with volume, 1RM, PRs, and the comparison |
| `/today` | Everything logged today |
| `/week` | Sets and volume by muscle group vs weekly targets, plus glute loading vectors |
| `/pr <exercise>` | Session history and records for one lift |
| `/bodyweight <kg>` | Update the load used for pull-ups, dips, push-ups |

## Setup

### 1-2. Secrets

Two secrets are needed in the repo-root `.env`; both require a human step.

1. **`TELEGRAM_WORKOUT_BOT_TOKEN`** — register a NEW bot with @BotFather.
   Telegram permits exactly one long-poller per token, and `TELEGRAM_BOT_TOKEN`
   (Job Pilot) and `TELEGRAM_NUTRITION_BOT_TOKEN` are both held by running bots;
   reusing either knocks a live service off the air with a 409.
2. **`SUPABASE_URL`** and **`SUPABASE_SERVICE_ROLE_KEY`** — from the
   Longevity-Nutrition project (`afscqhevcuxovbxdyhop`), Settings → API.

```bash
SUPABASE_URL=https://afscqhevcuxovbxdyhop.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role key>
TELEGRAM_WORKOUT_BOT_TOKEN=<BotFather token>
WORKOUT_USER_ID=<uuid, printed by --init>
```

> The repo-root `.env` also has `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY`, which
> point at a **dead** project (`gyymxodipcyl…`, no longer resolves). `config.py` refuses
> any `SUPABASE_URL` that isn't the live ref, so that stale pair can't be picked up by
> accident.

### Why the service-role key

Every RLS policy on `workouts`, `workout_exercises` and `personal_records` is granted
`TO authenticated` and keys on `auth.uid()`. The anon/publishable key gets the `anon`
role, which has no policy at all — so it reads back `[]` rather than erroring, and
writes are silently rejected. A server-side bot with no browser session can't satisfy
`auth.uid()`, so it uses the service-role key and **bypasses RLS**.

The consequence: nothing scopes rows for us. Every query in `store.py` filters on
`user_id` explicitly. Don't remove those filters.

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
```

### 3. An auth user (required, and not obvious)

The foreign-key chain is two levels deep:

```
workouts.user_id -> public.user_profiles(id) -> auth.users(id)   ON DELETE CASCADE
```

`auth.users` starts empty, so **no workout can be written until one Supabase auth
user exists**. Worse, `information_schema` does *not* report that second constraint —
it hides constraints referencing the `auth` schema and reports `user_profiles` as
having no foreign keys at all. `pg_constraint` shows the truth:

```sql
select conname, pg_get_constraintdef(oid) from pg_constraint
 where conrelid = 'public.user_profiles'::regclass and contype = 'f';
-- user_profiles_id_fkey: FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE
```

Email confirmation is enabled on this project, so an ordinary signup sits unconfirmed
and unusable. Create a pre-confirmed user with the Admin API instead — the supported
path for a service-role caller, and no email click. Idempotent, so it is safe to
re-run:

```bash
./.venv/bin/python3 - <<'PY'
import re, requests
from pathlib import Path
import config
EMAIL = "you@example.com"
url, key = config.supabase_url(), config.service_role_key()
H = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
r = requests.get(f"{url}/auth/v1/admin/users", headers=H, timeout=25); r.raise_for_status()
hit = [u for u in (r.json().get("users") or []) if u.get("email") == EMAIL]
if hit:
    user = hit[0]; print("reusing", user["id"])
else:
    c = requests.post(f"{url}/auth/v1/admin/users", headers=H,
                      json={"email": EMAIL, "email_confirm": True}, timeout=25)
    c.raise_for_status(); user = c.json(); print("created", user["id"])
p = Path("../.env"); t = p.read_text()
line = "WORKOUT_USER_ID=" + user["id"]
p.write_text(re.sub(r"(?m)^WORKOUT_USER_ID=.*$", line, t)
             if re.search(r"(?m)^WORKOUT_USER_ID=", t) else t + "\n" + line + "\n")
print("WORKOUT_USER_ID written")
PY
```

No password is set — there is no credential to store, and the web app's password-reset
flow can set one later if you ever want to sign in as that user. Alternatively, sign
up in the Longevity-Nutrition app and use that account's uuid.

### 4. Finish

```bash
./.venv/bin/python3 workout.py --init            # creates the user_profiles row
./.venv/bin/python3 workout.py --bodyweight 85
```

## Run

```bash
./run_bot.sh                                      # foreground
cp com.crosswalk.workout-bot.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.crosswalk.workout-bot.plist
launchctl list | grep workout-bot                 # pid must match the real python process
```

`run_bot.sh` uses `exec` so launchd supervises python directly. Without it launchd
kills the wrapper and orphans python, leaving two pollers fighting over one token.

## CLI

```bash
./.venv/bin/python3 workout.py "bench 3x8 @ 80kg"
./.venv/bin/python3 workout.py --dry-run "squat 5,5,5 @ 100"   # analyse, write nothing
./.venv/bin/python3 workout.py --today
./.venv/bin/python3 workout.py --week
./.venv/bin/python3 workout.py --pr bench
```

## The maths

Fixed by spec in `metrics.py`; not to be "improved".

```
volume_load   = sets x reps x weight
estimated 1RM = weight x (1 + reps / 30)      [Epley]
PR            = beats personal_records.max_weight or .max_volume
```

- Bodyweight lifts use stored bodyweight as the load, plus anything added.
- `max_volume` is the exercise's **session** volume (all sets); `max_weight` is the
  heaviest single set.
- The model only ever *transcribes* notation into sets. Every number is computed in
  Python, so results are reproducible.

**There is deliberately no calories-burned feature.** Resistance-training energy
expenditure estimates are too inaccurate to act on, and a wrong number here would
feed into the nutrition bot's targets.

## Storage

One row per set in `workout_exercises` (`set_number` 1..n, `sets` = 1). A later
migration added `set_number` precisely so sessions log per set, and it's the only way
varying loads inside one exercise (`100x5, 110x3, 120x1`) survive the round trip.

| Table | Written |
|---|---|
| `workouts` | one row per logged message; `total_volume_load` is the session sum |
| `workout_exercises` | one row per set |
| `personal_records` | upserted on `UNIQUE(user_id, exercise_name)` when a PR lands |
| `exercise_library` | read only (85 rows) |

Bodyweight lives in `data/profile.json`, not Supabase: `user_profiles` has
`height_cm`, `age` and `sex` but no bodyweight column, and adding one would mean a
schema change to a live app's database for this bot's benefit. `data/` is gitignored —
personal health data, public repo.

If the sets fail to insert, the `workouts` row is deleted rather than left behind; an
empty session would otherwise read as a real training day and poison every later
volume comparison.

## Exercise resolution

What you type is matched against `exercise_library` (85 rows) using
`alternate_names`, so "bench" finds Barbell Bench Press and "pullups" finds Pull Up.

1. Deterministic: bare-term preferences, then normalised exact, then compact
   (spaces/plurals stripped), then unique token-subset. 15/15 of the common gym
   shorthands resolve here with no model call.
2. Only a genuine tie between several real candidates goes to the model, which may
   answer "none of these".
3. A lift the library doesn't have is flagged `⚠️ not in library` and logged under the
   name you used — **never** remapped onto a different exercise, which would corrupt
   both PR history and the volume comparison.

Every reply shows the resolved library name, so a default you disagree with is visible
rather than silent.

## Weekly targets

`targets.py` holds weekly set targets, biased to glutes and lower body. They are
**population guidelines from the literature, not claims about your body**:

- Schoenfeld, Ogborn & Krieger (2017) dose-response — hypertrophy scales with weekly
  set volume past 10 sets/muscle/week for trained lifters; ~4-6 is maintenance. Lower
  body sits high in that range, upper body at the growth floor.
- Contreras's glute work — the glutes are trained across three **loading vectors**, and
  a programme biased to one leaves the others undertrained:

| Vector | Derived from | Target |
|---|---|---|
| Anteroposterior | `movement_pattern = hinge` (hip thrust, RDL, back extension) | 8 sets |
| Axial | `squat` + `unilateral` (axially loaded, incl. single-leg squats) | 6 sets |
| Lateral / rotary | `hip abductors` muscle group (abduction work) | 4 sets |

The vector split is derived from the live library, not assumed: 40 of 44 glute
exercises classify (the rest are Plank, Bird Dog and sled work, which aren't
vector-specific). Single-leg lunges and step-ups count as **axial**, not lateral —
they're loaded along the spine, and calling them lateral would hide the abduction gap
Contreras actually warns about.

Set counting follows the direct/indirect convention: the first muscle group listed for
an exercise takes full credit, the rest take 0.5. A set of Barbell Back Squat is not a
full set for the hamstrings.

Edit `TARGETS` freely — it's plain data. Set a value to `None` to track a group's
volume with no target line.
