"""Shared configuration for the workout agent.

Secrets come from the repo-root .env via os.environ — never hardcoded, never logged.
This repo is public and has a prior leak incident; a pre-commit gitleaks hook enforces it.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"

load_dotenv(BASE.parent / ".env")

MODEL = "claude-sonnet-5"

# The repo-root .env still carries VITE_SUPABASE_* for a dead project
# (gyymxodipcyl..., no longer resolves). The live Longevity-Nutrition backend is
# afscqhevcuxovbxdyhop, so this agent reads its own SUPABASE_* names and refuses
# to fall back to the stale pair.
LIVE_PROJECT_REF = "afscqhevcuxovbxdyhop"

# One row per set: a later migration added workout_exercises.set_number precisely
# so a session logs each set, which is also the only way varying loads inside one
# exercise ("100x5, 110x3, 120x1") survive the round trip.
SETS_PER_ROW = 1

# Weight in. Everything is stored in kg; display follows this.
DEFAULT_UNIT = "kg"
LB_PER_KG = 2.2046226218

REQUEST_TIMEOUT = 25
ANALYSIS_TIMEOUT = 180


def supabase_url() -> str:
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    if not url:
        raise RuntimeError(
            "SUPABASE_URL is not set in .env. Expected "
            f"https://{LIVE_PROJECT_REF}.supabase.co"
        )
    if LIVE_PROJECT_REF not in url:
        raise RuntimeError(
            f"SUPABASE_URL points at {url.split('//')[-1].split('.')[0]!r}, not the live "
            f"project {LIVE_PROJECT_REF!r}. Refusing to write workouts to the wrong backend."
        )
    return url


def service_role_key() -> str:
    """The service-role key. Required: every RLS policy on these tables targets the
    `authenticated` role and keys on auth.uid(), so the publishable/anon key reads
    back an empty list rather than an error — a silent, dangerous no-op."""
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "SUPABASE_SERVICE_ROLE_KEY is not set in .env.\n"
            "Supabase dashboard → Project Settings → API keys → service_role → copy.\n"
            "The anon/publishable key cannot be used here: RLS grants nothing to the "
            "anon role, so reads return [] and writes are rejected."
        )
    return key


def user_id() -> str:
    """The user_profiles row these workouts belong to (FK target of workouts.user_id)."""
    uid = os.environ.get("WORKOUT_USER_ID", "").strip()
    if not uid:
        raise RuntimeError("WORKOUT_USER_ID is not set in .env — run `python3 workout.py --init`.")
    return uid
