"""The safety-critical half of these tests is the refusal list: a job that may
already have reached an employer must never be re-driven."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import retry_policy

TODAY = datetime(2026, 9, 9)
OLD = "2026-09-05"


def entry(status="prefilled_pending_review", reason="", attempts=1, date=OLD):
    return {"status": status, "no_apply_reason": reason,
            "attempts": attempts, "date": date}


# --- must retry -------------------------------------------------------------

def test_wizard_stopped_is_retried():
    e = entry(reason="the wizard stopped before reaching a Submit step")
    assert retry_policy.should_retry(e, TODAY)


def test_form_automation_failure_is_retried():
    assert retry_policy.should_retry(entry(reason="page or form automation failed"), TODAY)


def test_expired_session_is_retried():
    e = entry(reason="saved Workday session for GoodLife Fitness looks expired — "
                     "run `python3 workday_session.py goodlifefitness` again")
    assert retry_policy.should_retry(e, TODAY)


def test_expired_session_never_exhausts_attempts():
    """A week of expired-session runs must not permanently retire a job that
    only ever needed a fresh sign-in."""
    e = entry(reason="looks expired", attempts=99)
    assert retry_policy.should_retry(e, TODAY)


def test_precondition_failure_does_not_consume_an_attempt():
    assert retry_policy.next_attempt_count({"attempts": 2}, "looks expired") == 2


def test_transient_failure_consumes_an_attempt():
    assert retry_policy.next_attempt_count({"attempts": 2},
                                           "page or form automation failed") == 3


# --- must NOT retry ---------------------------------------------------------

def test_submit_unconfirmed_is_never_retried():
    """A Submit was clicked; only the confirmation was unreadable. Retrying
    risks a second real application under his name."""
    e = entry(status="submit_unconfirmed",
              reason="Submit clicked but Workday showed no confirmation text")
    assert not retry_policy.should_retry(e, TODAY)


def test_captcha_is_never_retried():
    e = entry(reason="everything is filled in — the site demands a captcha, "
                     "which only a human may answer")
    assert not retry_policy.should_retry(e, TODAY)


def test_unverifiable_form_is_never_retried():
    e = entry(reason="non-standard form without a resume-upload field — "
                     "auto-submitting couldn't be verified as a real application")
    assert not retry_policy.should_retry(e, TODAY)


def test_job_board_botcheck_is_never_retried():
    e = entry(reason="job-board bot-check page (Glassdoor/ZipRecruiter/Indeed) — "
                     "no real application form reachable by automation")
    assert not retry_policy.should_retry(e, TODAY)


def test_applied_is_never_retried():
    assert not retry_policy.should_retry(
        entry(status="applied_web", reason="page or form automation failed"), TODAY)


def test_missing_reason_defaults_to_no_retry():
    assert not retry_policy.should_retry({"status": "prefilled_pending_review"}, TODAY)


def test_non_dict_entry_is_safe():
    assert not retry_policy.should_retry("notified", TODAY)


# --- budget and cooldown ----------------------------------------------------

def test_transient_stops_after_max_attempts():
    e = entry(reason="the wizard stopped before reaching a Submit step",
              attempts=retry_policy.MAX_TRANSIENT_ATTEMPTS)
    assert not retry_policy.should_retry(e, TODAY)


def test_same_day_failure_waits_for_cooldown():
    e = entry(reason="page or form automation failed", date="2026-09-09")
    assert not retry_policy.should_retry(e, TODAY)


def test_entry_predating_attempt_tracking_gets_its_retry():
    assert retry_policy.should_retry(
        {"status": "prefilled_pending_review",
         "no_apply_reason": "the wizard stopped before reaching a Submit step"}, TODAY)


def test_web_apply_failed_status_is_retryable():
    """job_agent records the generic automation failure under this status."""
    assert retry_policy.should_retry(
        entry(status="web_apply_failed", reason="page or form automation failed"), TODAY)


def test_jobbank_signin_is_not_retried():
    """manual_only is not a retryable status — re-opening these would redeliver
    the same posting daily with no prospect of automation finishing it."""
    assert not retry_policy.should_retry(
        entry(status="manual_only",
              reason="Job Bank Direct Apply — requires your Job Bank sign-in"), TODAY)


# --- run selection ----------------------------------------------------------

def test_select_retries_skips_non_retryable():
    seen = {
        "a": entry(reason="the wizard stopped before reaching a Submit step"),
        "b": entry(status="submit_unconfirmed", reason="Submit clicked, no confirmation"),
        "c": {"status": "applied_web", "date": OLD},
    }
    assert retry_policy.select_retries(seen, TODAY) == ["a"]


def test_select_retries_is_capped_per_run():
    seen = {"job%02d" % i: entry(reason="page or form automation failed")
            for i in range(retry_policy.MAX_RETRIES_PER_RUN + 15)}
    assert len(retry_policy.select_retries(seen, TODAY)) == retry_policy.MAX_RETRIES_PER_RUN


def test_select_retries_takes_the_newest_first():
    """Budget goes to postings most likely to still be open."""
    seen = {
        "newer": entry(reason="page or form automation failed", date="2026-09-07"),
        "older": entry(reason="page or form automation failed", date="2026-09-01"),
    }
    assert retry_policy.select_retries(seen, TODAY)[0] == "newer"


def test_select_retries_sorts_undated_entries_last():
    seen = {
        "dated": entry(reason="page or form automation failed", date="2026-09-01"),
        "undated": {"status": "web_apply_failed",
                    "no_apply_reason": "page or form automation failed"},
    }
    assert retry_policy.select_retries(seen, TODAY) == ["dated", "undated"]


def test_select_retries_handles_empty_and_none():
    assert retry_policy.select_retries({}, TODAY) == []
    assert retry_policy.select_retries(None, TODAY) == []
