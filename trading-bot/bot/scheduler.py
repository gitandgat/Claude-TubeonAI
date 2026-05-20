"""
Scheduler — scheduler.py
────────────────────────
Runs minervini_bot.py every weekday at 9:00 AM Eastern Time.
Uses Minervini Trend Template for entry and -7%/+20% exits.
After the bot finishes, puts the Mac to sleep (SLEEP_AFTER_RUN = True).

Managed by launchd — starts at login, restarts on crash.
Logs: scheduler.log (this file) and bot.log (trade activity).
"""

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


def trigger_bot() -> None:
    """
    Called by schedule at 09:00 ET every day.
    Skips weekends, runs bot.py, then sleeps the Mac if configured.
    """
    if not is_market_weekday():
        log.info("Weekend in ET — skipping bot run.")
        return

    log.info("Checking network connectivity …")
    if not wait_for_network():
        log.error("Network not available after 120 s — skipping bot run today.")
        _log_next_run()
        return

    log.info("Network ready. Triggering minervini_bot.py …")
    result = subprocess.run([sys.executable, str(BOT_SCRIPT)])

    if result.returncode == 0:
        log.info("Bot run finished successfully.")
    else:
        log.error("Bot exited with code %d — check bot.log for details.", result.returncode)

    _log_next_run()

    if SLEEP_AFTER_RUN:
        time.sleep(5)   # brief pause so the final log line flushes before sleep
        sleep_mac()


def _log_next_run() -> None:
    job = next(
        (j for j in schedule.get_jobs() if j.job_func.func is trigger_bot),
        None,
    )
    if job:
        log.info("Next scheduled run: %s", job.next_run)


def trigger_all_variants() -> None:
    """
    Called by schedule at 09:05 ET every weekday.
    Runs all 3 bot variants (A, B, C) in sequence with delays between them.
    """
    if not is_market_weekday():
        log.info("Weekend in ET — skipping 3-bot run.")
        return

    log.info("Checking network connectivity for 3-bot run …")
    if not wait_for_network():
        log.error("Network not available after 120 s — skipping 3-bot run today.")
        _log_next_run()
        return

    log.info("Network ready. Triggering all 3 bot variants …")

    variants = ["bot_a.py", "bot_b.py", "bot_c.py"]
    for variant_script in variants:
        variant_path = BOT_DIR / variant_script
        if not variant_path.exists():
            log.error("Bot script not found: %s", variant_path)
            continue

        log.info(f"Running {variant_script}…")
        result = subprocess.run([sys.executable, str(variant_path)])

        if result.returncode == 0:
            log.info(f"{variant_script} finished successfully.")
        else:
            log.error(f"{variant_script} exited with code {result.returncode}")

        time.sleep(30)  # Delay between variants to avoid Polygon rate limits

    log.info("All 3-bot variants completed. Running comparison…")
    compare_script = BOT_DIR / "compare_performance.py"
    if compare_script.exists():
        subprocess.run([sys.executable, str(compare_script), "--last-7"])

    _log_next_run()


# ── Schedule ──────────────────────────────────────────────────────────────────
# TZ=America/New_York is set in the launchd plist, so "09:00" fires at 9:00 AM ET.
schedule.every().day.at("09:00").do(trigger_bot)
schedule.every().day.at("09:05").do(trigger_all_variants)

log.info("Scheduler started — minervini_bot fires weekdays at 09:00 ET, 3-bot variants at 09:05 ET.")
log.info("Sleep after run: %s", SLEEP_AFTER_RUN)
_log_next_run()

while True:
    schedule.run_pending()
    time.sleep(30)
