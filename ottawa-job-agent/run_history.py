"""Structured automation run-history log — automation_runs.jsonl.

Append-only JSON Lines file, one line per automation invocation. This is the
only structured record of automation runs; job_agent.log is free-text and
not meant to be parsed.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

RUNS_FILE = Path(__file__).resolve().parent / "automation_runs.jsonl"


def record_run(
    automation_name: str,
    target: str,
    status: str,
    message: str,
    duration_ms: Optional[int] = None,
) -> None:
    """Append one JSON line describing an automation run. Never raises —
    a logging failure must not break the pipeline it's observing."""
    try:
        entry = {
            "automation_name": automation_name,
            "target": target,
            "status": status,
            "message": message,
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        with open(RUNS_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def load_runs() -> list:
    """Read all recorded runs, oldest first. Returns [] if the file doesn't exist yet."""
    if not RUNS_FILE.exists():
        return []
    runs = []
    for line in RUNS_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            runs.append(json.loads(line))
        except Exception:
            continue
    return runs
