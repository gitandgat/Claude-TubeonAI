#!/usr/bin/env python3
"""Liveness monitor for the 5/day vertical posting engine.

Catches the failure that silently killed 5/day for 9 days (Jun 17-26 2026): a hung
run_verticals.py that launchd never re-ran. Runs daily AFTER the verticals job. It:
  1. Reaps any run_verticals.py stuck running far longer than a daily job should
     (so launchd is unblocked to re-run), and
  2. Alerts loudly (macOS notification + log) if fewer than 5 posts are scheduled
     for today — i.e. the engine produced nothing.

Defensive: the one network call has an explicit timeout, so the monitor itself
can't become the next silent hang.
"""
import os
import subprocess
import sys
from datetime import datetime

import requests
from pytz import timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zernio_key import ZERNIO_API_KEY

ET = timezone("America/New_York")
EXPECTED = 5                      # one post per vertical
HUNG_AFTER_SEC = 30 * 60          # a daily job running >30min is hung
LOG = "/tmp/verticals-monitor.log"


def log(msg: str) -> None:
    line = f"[{datetime.now(ET):%Y-%m-%d %H:%M ET}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def notify(title: str, msg: str) -> None:
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{msg}" with title "{title}" sound name "Basso"'],
            timeout=15, check=False)
    except Exception:
        pass


def reap_hung_process() -> None:
    """Kill a run_verticals.py that has been running too long (the 9-day hang)."""
    try:
        pids = subprocess.check_output(["pgrep", "-f", "run_verticals.py"],
                                       text=True).split()
    except subprocess.CalledProcessError:
        return  # not running — fine, it's a short-lived daily job
    for pid in pids:
        try:
            etimes = subprocess.check_output(["ps", "-p", pid, "-o", "etimes="],
                                             text=True).strip()
            if etimes and int(etimes) > HUNG_AFTER_SEC:
                os.kill(int(pid), 9)
                log(f"REAPED hung run_verticals.py pid={pid} (ran {int(etimes)}s)")
                notify("Verticals engine was HUNG",
                       f"Killed stuck pid {pid}; launchd will re-run it.")
        except (subprocess.CalledProcessError, ValueError, ProcessLookupError) as e:
            log(f"reap check failed for pid {pid}: {e}")


def posts_scheduled_today() -> tuple[int, str]:
    today = datetime.now(ET).strftime("%Y-%m-%d")
    r = requests.get("https://zernio.com/api/v1/posts?limit=200",
                     headers={"Authorization": f"Bearer {ZERNIO_API_KEY}"},
                     timeout=30)
    r.raise_for_status()
    payload = r.json()
    posts = payload.get("posts", payload)
    if isinstance(posts, dict):
        posts = posts.get("posts", [])
    return sum(1 for p in posts if (p.get("scheduledFor") or "")[:10] == today), today


def main() -> None:
    reap_hung_process()
    try:
        n, today = posts_scheduled_today()
    except Exception as e:
        log(f"Zernio check FAILED: {e}")
        notify("Verticals monitor error", f"Could not reach Zernio: {e}")
        return
    if n >= EXPECTED:
        log(f"OK — {n} posts scheduled for {today} (>= {EXPECTED}).")
    else:
        log(f"ALERT — only {n} posts scheduled for {today} (expected {EXPECTED}). "
            "Verticals engine may be down.")
        notify("5/day posting may be DOWN",
               f"Only {n} posts scheduled today (want {EXPECTED}). Check run_verticals.py.")


if __name__ == "__main__":
    main()
