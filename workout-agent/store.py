"""Supabase access for the workout agent, over PostgREST.

Authenticates with the service-role key, which BYPASSES RLS. That is deliberate —
every policy on these tables keys on auth.uid() and this bot is a trusted
single-user server process with no browser session. The direct consequence is that
nothing scopes rows for us, so every query here filters on user_id explicitly.
Dropping that filter would silently expose or overwrite another user's history.

workout_exercises carries no user_id of its own; it is scoped through an inner
embed on workouts, which is why the select strings look the way they do.
"""

from __future__ import annotations

import logging
from datetime import date

import requests

import config

log = logging.getLogger("workout-agent.store")

LIBRARY_FIELDS = (
    "exercise_name,category,muscle_groups,equipment_required,"
    "alternate_names,movement_pattern,rep_ranges,progression_harder"
)
SETS_WITH_DATE = "exercise_name,weight,reps,sets,volume_load,set_number,workouts!inner(date,user_id)"


class StoreError(RuntimeError):
    """A Supabase call failed. Carries the response body, because PostgREST puts
    the actual reason (constraint name, missing column) in there and a bare status
    code sends you hunting."""


def _headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    key = config.service_role_key()
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if extra:
        headers.update(extra)
    return headers


def _request(method: str, path: str, **kwargs) -> list[dict]:
    url = f"{config.supabase_url()}/rest/v1/{path}"
    try:
        res = requests.request(
            method, url, headers=_headers(kwargs.pop("extra_headers", None)),
            timeout=config.REQUEST_TIMEOUT, **kwargs
        )
    except requests.RequestException as exc:
        raise StoreError(f"{method} {path} could not reach Supabase: {exc}") from exc

    if not res.ok:
        # res.text, never the request headers — those hold the service-role key.
        raise StoreError(f"{method} {path} -> {res.status_code}: {res.text[:400]}")
    if not res.content or res.status_code == 204:
        return []
    payload = res.json()
    return payload if isinstance(payload, list) else [payload]


# --- exercise library -------------------------------------------------------

def fetch_library() -> list[dict]:
    """Every exercise_library row. Read once per run and matched against in memory."""
    rows = _request("GET", "exercise_library", params={"select": LIBRARY_FIELDS, "limit": "500"})
    if not rows:
        # The anon key returns [] here rather than 401, so an empty library almost
        # always means the wrong key, not an empty table.
        raise StoreError(
            "exercise_library came back empty. The table has 85 rows, so this is "
            "almost certainly an auth problem — check SUPABASE_SERVICE_ROLE_KEY is "
            "the service_role key and not the anon/publishable one."
        )
    return rows


# --- profile ----------------------------------------------------------------

def ensure_profile(user_id: str, name: str = "Sahawat") -> dict:
    """Return the user_profiles row, creating it if absent.

    Only id, name and weight_unit are set. age, sex, height_cm and primary_goal
    are left NULL on purpose — no facts about his body get invented here.
    """
    existing = _request(
        "GET", "user_profiles", params={"select": "id,name,weight_unit", "id": f"eq.{user_id}"}
    )
    if existing:
        return existing[0]

    created = _request(
        "POST",
        "user_profiles",
        json={"id": user_id, "name": name, "weight_unit": "kg"},
        extra_headers={"Prefer": "return=representation"},
    )
    log.info("Created user_profiles row for %s", user_id)
    return created[0]


# --- workouts ---------------------------------------------------------------

def insert_workout(user_id: str, when: date, notes: str, total_volume_load: float) -> str:
    rows = _request(
        "POST",
        "workouts",
        json={
            "user_id": user_id,
            "date": when.isoformat(),
            "notes": notes[:2000],
            "total_volume_load": total_volume_load,
        },
        extra_headers={"Prefer": "return=representation"},
    )
    return rows[0]["id"]


def insert_sets(workout_id: str, rows: list[dict]) -> None:
    """Bulk-insert one row per set. Each row already carries its own set_number."""
    if not rows:
        return
    _request(
        "POST",
        "workout_exercises",
        json=[{**r, "workout_id": workout_id} for r in rows],
        extra_headers={"Prefer": "return=minimal"},
    )


def delete_workout(workout_id: str) -> None:
    """Remove a session. workout_exercises cascades on workout_id.

    Used to roll back a half-written session: a workout row whose sets failed to
    insert would otherwise sit in history as a real session with no exercises and
    poison every volume comparison after it.
    """
    _request("DELETE", "workouts", params={"id": f"eq.{workout_id}"})


def sets_for_exercise(user_id: str, exercise_name: str) -> list[dict]:
    """Every logged set of one lift, newest first, with its session date."""
    rows = _request(
        "GET",
        "workout_exercises",
        params={
            "select": SETS_WITH_DATE,
            "exercise_name": f"eq.{exercise_name}",
            "workouts.user_id": f"eq.{user_id}",
            "order": "created_at.desc",
            "limit": "2000",
        },
    )
    return sorted(rows, key=lambda r: r["workouts"]["date"], reverse=True)


def sets_in_range(user_id: str, start: date, end: date) -> list[dict]:
    """All sets logged between two dates inclusive.

    Params are a list of pairs, not a dict: a date range needs the same key twice
    (gte and lte), which a dict silently collapses to whichever came last — an
    open-ended range that quietly returns the wrong week.
    """
    return _request(
        "GET",
        "workout_exercises",
        params=[
            ("select", SETS_WITH_DATE),
            ("workouts.user_id", f"eq.{user_id}"),
            ("workouts.date", f"gte.{start.isoformat()}"),
            ("workouts.date", f"lte.{end.isoformat()}"),
            ("limit", "5000"),
        ],
    )


def workouts_in_range(user_id: str, start: date, end: date) -> list[dict]:
    return _request(
        "GET",
        "workouts",
        params=[
            ("select", "id,date,notes,total_volume_load"),
            ("user_id", f"eq.{user_id}"),
            ("date", f"gte.{start.isoformat()}"),
            ("date", f"lte.{end.isoformat()}"),
            ("order", "date.desc"),
        ],
    )


# --- personal records -------------------------------------------------------

def get_records(user_id: str) -> dict[str, dict]:
    rows = _request(
        "GET",
        "personal_records",
        params={
            "select": "exercise_name,max_weight,max_volume,achieved_at",
            "user_id": f"eq.{user_id}",
            "limit": "1000",
        },
    )
    return {r["exercise_name"]: r for r in rows}


def upsert_record(
    user_id: str, exercise_name: str, max_weight: float, max_volume: float, achieved_at: str
) -> None:
    """Write a record, relying on UNIQUE(user_id, exercise_name) to merge."""
    _request(
        "POST",
        "personal_records",
        params={"on_conflict": "user_id,exercise_name"},
        json={
            "user_id": user_id,
            "exercise_name": exercise_name,
            "max_weight": max_weight,
            "max_volume": max_volume,
            "achieved_at": achieved_at,
        },
        extra_headers={"Prefer": "resolution=merge-duplicates,return=minimal"},
    )
