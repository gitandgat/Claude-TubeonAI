"""Local profile: bodyweight, used as the load for bodyweight lifts.

Kept in workout-agent/data/ rather than Supabase on purpose — user_profiles has
height_cm, age and sex but no bodyweight column, and adding one would mean a
schema change to a live app's database for this bot's benefit. The file is
gitignored: this is personal health data in a public repo.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import config

log = logging.getLogger("workout-agent.profile")

PROFILE_PATH = config.DATA_DIR / "profile.json"


def load() -> dict:
    if not PROFILE_PATH.exists():
        return {}
    try:
        return json.loads(PROFILE_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        # A corrupt profile must not read as "bodyweight 0", which would silently
        # zero out every pull-up and dip in the log.
        log.exception("profile.json is unreadable; treating bodyweight as unset")
        return {}


def save(**fields) -> dict:
    data = {**load(), **fields}
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.write_text(json.dumps(data, indent=2) + "\n")
    return data


def bodyweight_kg() -> float | None:
    value = load().get("bodyweight_kg")
    return float(value) if value else None


def set_bodyweight_kg(value: float) -> float:
    if not 30 <= value <= 300:
        raise ValueError(f"{value} kg is not a plausible bodyweight.")
    save(bodyweight_kg=round(float(value), 1))
    return round(float(value), 1)
