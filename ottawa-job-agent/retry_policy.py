"""Decide whether a previously-seen job deserves another automated attempt.

`seen_jobs.json` is permanent by design: a job id recorded there is filtered out
of every later run (job_agent.py's `new_jobs` line). That is correct for jobs
that were genuinely finished — applied, expired, skipped, or handed to a human
on purpose — but it also means a job that failed because of a *bug* stays failed
forever, even after the bug is fixed. That is exactly what happened to the 17
GoodLife Workday postings that hit the Sep 8 combobox-timeout bug on 2026-09-05:
the fix shipped, and not one of them was ever re-attempted.

This module is the narrow exception. It re-opens a job only when the recorded
reason says the automation broke *before submitting anything*, and never when
the run may have already put an application in front of an employer.

Two kinds of re-open, deliberately scored differently:

- **Precondition failures** (no saved ATS session, expired session). The wizard
  never started, so nothing was tried and nothing was learned. These do not burn
  an attempt — otherwise a week of expired-session runs would permanently retire
  a job that only ever needed a fresh sign-in.
- **Transient failures** (the wizard stopped moving, the form driver failed).
  Something really was attempted and it broke. Worth a bounded number of further
  tries in case a fix lands, then it stays with the human for good.

Everything else defaults to *no retry*: a captcha, a form we could not verify, a
job-board bot-check, and above all `submit_unconfirmed` — a Submit was clicked
there and the confirmation was merely unreadable, so retrying risks a second
real application under his name. An unknown or missing reason is also a no.
"""

from datetime import datetime, timedelta
from typing import Optional

# A transient failure gets this many automated attempts in total (the original
# plus MAX_TRANSIENT_ATTEMPTS - 1 retries) before it belongs to the human.
MAX_TRANSIENT_ATTEMPTS = 3

# The agent wakes every ~4 hours. Without a cooldown a broken posting would be
# re-driven six times a day and exhaust its budget before any fix could ship.
RETRY_COOLDOWN_DAYS = 1

# Ceiling on how many re-opened jobs a single run will take on. The backlog
# holds roughly a hundred retryable records; admitting them all at once would
# turn a routine run into a Playwright marathon and blow through the watchdog
# that exists to keep the daily cadence alive. Oldest first, so the queue drains
# steadily over successive runs instead of in one lump.
MAX_RETRIES_PER_RUN = 10

# Only these statuses are ever reconsidered. `submit_unconfirmed` is absent on
# purpose and must stay absent — see the module docstring.
RETRYABLE_STATUSES = frozenset({
    "prefilled_pending_review",
    "web_apply_failed",
    "failed",
})

# Matched case-insensitively as substrings of the recorded no_apply_reason.
# These describe a run that never reached a Submit control.
# Job Bank's "requires your Job Bank sign-in" is deliberately absent: it is
# recorded under the manual_only status, which is not retryable, so re-opening
# those would only put the same posting back in the digest day after day without
# any prospect of the automation finishing it.
_PRECONDITION_REASONS = (
    "looks expired",
    "no saved workday session",
)

_TRANSIENT_REASONS = (
    "the wizard stopped before reaching a submit step",
    "page or form automation failed",
    "couldn't find/click",
)


def _reason_of(entry: dict) -> str:
    return str(entry.get("no_apply_reason") or "").strip().lower()


def _matches(reason: str, patterns: tuple) -> bool:
    return any(p in reason for p in patterns)


def classify(entry: dict) -> Optional[str]:
    """"precondition", "transient", or None when the job must not be retried."""
    if not isinstance(entry, dict):
        return None
    if entry.get("status") not in RETRYABLE_STATUSES:
        return None
    reason = _reason_of(entry)
    if not reason:
        return None
    if _matches(reason, _PRECONDITION_REASONS):
        return "precondition"
    if _matches(reason, _TRANSIENT_REASONS):
        return "transient"
    return None


def _cooled_down(entry: dict, today: datetime) -> bool:
    """True when enough time has passed since the last attempt. A missing or
    unparseable date is treated as cooled down: the entry predates attempt
    tracking, so its one retry is exactly what this module exists to give."""
    raw = entry.get("last_attempt") or entry.get("date")
    if not raw:
        return True
    try:
        last = datetime.strptime(str(raw)[:10], "%Y-%m-%d")
    except ValueError:
        return True
    return today - last >= timedelta(days=RETRY_COOLDOWN_DAYS)


def should_retry(entry: dict, today: Optional[datetime] = None) -> bool:
    """Whether job_agent should let this previously-seen job through again."""
    kind = classify(entry)
    if kind is None:
        return False

    today = today or datetime.now()
    if not _cooled_down(entry, today):
        return False

    if kind == "precondition":
        return True

    try:
        attempts = int(entry.get("attempts") or 1)
    except (TypeError, ValueError):
        attempts = 1
    return attempts < MAX_TRANSIENT_ATTEMPTS


def select_retries(seen: dict, today: Optional[datetime] = None) -> list:
    """The job ids in `seen` to re-admit on this run, most recent attempt first
    and capped at MAX_RETRIES_PER_RUN.

    Newest first, not oldest: a retry only pays off on a posting that is still
    open, and the backlog's oldest failures are months-dead listings. It also
    puts the budget where the evidence is — a bug fixed today broke the jobs that
    ran most recently. An entry with no recorded date sorts last, being the
    stalest thing in the file.
    """
    eligible = []
    for job_id, entry in (seen or {}).items():
        if not should_retry(entry, today):
            continue
        when = str(entry.get("last_attempt") or entry.get("date") or "")
        eligible.append((when, str(job_id)))
    eligible.sort(reverse=True)
    return [job_id for _, job_id in eligible[:MAX_RETRIES_PER_RUN]]


def next_attempt_count(previous: Optional[dict], reason: str) -> int:
    """The `attempts` value to store on a fresh failure. Precondition failures
    never got a real try, so they leave the counter where it was."""
    try:
        prior = int((previous or {}).get("attempts") or 0)
    except (TypeError, ValueError):
        prior = 0
    if _matches(str(reason or "").lower(), _PRECONDITION_REASONS):
        return prior
    return prior + 1
