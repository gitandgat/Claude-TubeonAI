"""Small persistent settings the pipeline reads on every run — including
launchd-triggered ones, where no one is present to pass a CLI flag. A JSON file
(not an env var or CLI arg) is the one mechanism that behaves identically whether
job_agent.py was started by a human typing a command or by launchd firing at 4am.
"""

import json
import sys
from datetime import date
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "agent_config.json"

DEFAULTS = {
    # When True, web_applier.py fills every application form completely but stops
    # short of clicking submit — lands on the same "prefilled_pending_review" status
    # the pipeline already uses when it can't find a safe submit path, so the
    # dashboard/digest/tracker need no changes to support this mode.
    "review_only": False,
    # Last date (YYYY-MM-DD) the Serper-credits-exhausted alert was shown in the
    # digest email. The pipeline runs 6x/day, so without this gate the same
    # "add prepaid credits" line repeats 6 times a day for as long as credits
    # stay unpurchased — once the user has seen and decided on it for the day,
    # repeating it adds nothing.
    "serper_alert_last_shown": None,
    # Last date (YYYY-MM-DD) any digest email went out — a real digest (applied/
    # notify/ghosted/alert) or the quiet-day status fallback. Sahawat asked for a
    # daily email regardless of results (Sep18), so a run that finds nothing still
    # sends one short status email per day; this gate stops that from repeating on
    # every one of the day's remaining runs once one has already gone out.
    "last_digest_sent": None,
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return dict(DEFAULTS)
    try:
        data = json.loads(CONFIG_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULTS)
    merged = dict(DEFAULTS)
    merged.update(data)
    return merged


def save_config(config: dict):
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def is_review_only() -> bool:
    return bool(load_config().get("review_only", False))


def set_review_only(value: bool):
    config = load_config()
    config["review_only"] = value
    save_config(config)


def should_alert_serper_exhausted() -> bool:
    """True once per calendar day — call before appending the Serper-credits
    alert to the digest, then call mark_serper_alert_shown() if it fires."""
    return load_config().get("serper_alert_last_shown") != str(date.today())


def mark_serper_alert_shown():
    config = load_config()
    config["serper_alert_last_shown"] = str(date.today())
    save_config(config)


def has_sent_digest_today() -> bool:
    """True once a digest (real or quiet-day status) has already gone out today."""
    return load_config().get("last_digest_sent") == str(date.today())


def mark_digest_sent():
    config = load_config()
    config["last_digest_sent"] = str(date.today())
    save_config(config)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] not in ("on", "off", "status"):
        print("Usage: python3 agent_config.py [on|off|status]")
        print("  on     - review-before-submit: forms get filled, submit is held back")
        print("  off    - normal fully-autonomous auto-submit mode")
        print("  status - show current setting")
        sys.exit(0)

    if args[0] == "status":
        state = "ON (applications held for review)" if is_review_only() else "OFF (auto-submitting)"
        print(f"review_only: {state}")
    elif args[0] == "on":
        set_review_only(True)
        print("review_only set to ON - applications will be filled but not submitted.")
    else:
        set_review_only(False)
        print("review_only set to OFF - pipeline will auto-submit as before.")
