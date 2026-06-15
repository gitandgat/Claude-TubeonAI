"""
Scheduler — scheduler.py
────────────────────────
Runs minervini_bot.py every weekday at 9:00 AM Eastern Time.
Uses Minervini Trend Template for entry and -7%/+20% exits.
After the bot finishes, puts the Mac to sleep (SLEEP_AFTER_RUN = True).

Managed by launchd — starts at login, restarts on crash.
Logs: scheduler.log (this file) and bot.log (trade activity).
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pytz
import schedule

ET = pytz.timezone("America/New_York")

# ── Paths ──────────────────────────────────────────────────────────────────────
BOT_DIR = Path(__file__).parent
BOT_SCRIPT = BOT_DIR / "minervini_bot.py"
SCHEDULER_LOG = BOT_DIR / "scheduler.log"

# ── Config ────────────────────────────────────────────────────────────────────
# Set False if you want the Mac to stay awake after the bot finishes.
SLEEP_AFTER_RUN = True

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(SCHEDULER_LOG),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def is_market_weekday() -> bool:
    """True Monday–Friday in ET (does not account for US market holidays)."""
    return datetime.now(ET).weekday() < 5  # 0=Mon … 4=Fri


def wait_for_network(timeout: int = 120) -> bool:
    """
    Wait until we can reach api.polygon.io, checking every 5 s.
    Returns True when online, False if timeout exceeded.
    Mac often takes 15-30 s to get internet after waking from sleep.
    """
    import socket
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            socket.setdefaulttimeout(5)
            socket.getaddrinfo("api.polygon.io", 443)
            return True
        except OSError:
            log.info("Waiting for network … (%ds remaining)", int(deadline - time.time()))
            time.sleep(5)
    return False


def sleep_mac() -> None:
    """Put the Mac to sleep via osascript (no sudo required)."""
    log.info("Putting Mac to sleep …")
    subprocess.run(
        ["osascript", "-e", 'tell application "System Events" to sleep'],
        check=False,
    )


def wait_for_network_indefinite() -> None:
    """
    Wait indefinitely for network to become available.
    Retries every 30 seconds with persistent logging.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            import socket
            socket.setdefaulttimeout(5)
            socket.getaddrinfo("api.polygon.io", 443)
            log.info("Network is available (attempt %d). Proceeding with bot run.", attempt)
            return
        except OSError:
            log.info("Network unavailable (attempt %d). Retrying in 30 seconds…", attempt)
            time.sleep(30)


def trigger_bot() -> None:
    """
    Called by schedule at 09:45 ET every day (after the 9:30 market open).
    Skips weekends, runs bot.py, then sleeps the Mac if configured.
    Waits indefinitely for network before proceeding.
    """
    if not is_market_weekday():
        log.info("Weekend in ET — skipping bot run.")
        return

    log.info("Checking network connectivity …")
    wait_for_network_indefinite()

    log.info("Network ready. Triggering minervini_bot.py …")
    result = subprocess.run([sys.executable, str(BOT_SCRIPT)])

    if result.returncode == 0:
        log.info("Bot run finished successfully.")
    else:
        log.error("Bot exited with code %d — check bot.log for details.", result.returncode)

    # Tier-2 forward paper-trade log (screen vs Kavout vs SPY, zero-lookahead)
    forward_script = BOT_DIR / "forward_test.py"
    if forward_script.exists():
        log.info("Logging forward paper-trade snapshot …")
        subprocess.run([sys.executable, str(forward_script)])

    # Go-live readiness gate — fires a one-time alert when all criteria pass
    readiness_script = BOT_DIR / "readiness_check.py"
    if readiness_script.exists():
        subprocess.run([sys.executable, str(readiness_script)])

    _write_heartbeat(result.returncode)
    _log_next_run()

    if SLEEP_AFTER_RUN:
        time.sleep(5)   # brief pause so the final log line flushes before sleep
        sleep_mac()


def _write_heartbeat(returncode: int) -> None:
    """Record the last bot run so DAILY_CHECK.sh can verify execution health."""
    heartbeat = {
        "last_run": datetime.now(ET).isoformat(),
        "returncode": returncode,
        "status": "ok" if returncode == 0 else "failed",
    }
    try:
        (BOT_DIR / "last_run.json").write_text(json.dumps(heartbeat, indent=2))
    except OSError as exc:
        log.warning("Could not write heartbeat file: %s", exc)


def _log_next_run() -> None:
    job = next(
        (j for j in schedule.get_jobs() if j.job_func.func is trigger_bot),
        None,
    )
    if job:
        log.info("Next scheduled run: %s", job.next_run)


# ── Schedule ──────────────────────────────────────────────────────────────────
# TZ=America/New_York is set in the launchd plist, so "09:45" fires at 9:45 AM ET.
# Runs 15 min AFTER the 9:30 open (not before it): the intraday momentum filter
# needs the market open with 5/15-min bars formed. At the old 9:00 slot the market
# was still closed, so the intraday check rejected 100% of entries every day.
# (3-bot variant trigger removed — variants archived to trading-bot/archive/, Jun 2026)
schedule.every().day.at("09:45").do(trigger_bot)

log.info("Scheduler started — minervini_bot fires weekdays at 09:45 ET (after market open).")
log.info("Sleep after run: %s", SLEEP_AFTER_RUN)
_log_next_run()

while True:
    schedule.run_pending()
    time.sleep(30)
