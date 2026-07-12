"""Auto-apply on Job Bank's own "Direct Apply" postings — the sign-in-gated
subset of jobbank_source.py's manual_only jobs (job["jobbank_direct_apply"]).

Direct Apply is NOT a fillable form. Confirmed live: clicking the "Direct
Apply" control is itself the final, instant, irreversible submission — there
is no intermediate review step, no resume-upload field to fill, nothing to
"prefill". It reuses whatever resume/cover letter are already stored on the
signed-in account's "My documents" (see resume_builder.py's "universal"
category and cover_letter_builder.py — the account-level files kept there for
exactly this reason). The per-job cover_letter/resume_pdf this function
receives can't be attached to a Direct Apply click at all; they're accepted
only to keep the same call signature as apply_on_website.

Given that, this module's only real job is honesty: find the Direct Apply
control, click it, then verify the genuine post-click confirmation text
("You have successfully applied for this job through Job Bank!", confirmed
live) before ever reporting "submitted". A click that can't be confirmed is
reported as "submit_unconfirmed", never silently upgraded to "submitted" —
and never downgraded to some other status that would misrepresent a real
submission as still-pending.

If no session has been captured, or the saved one has expired, this bails out
before touching the page (no click attempted against an unauthenticated
form), so the caller can fall back to job_agent.py's existing FYI-only path.
"""

import re
import time

from playwright.sync_api import sync_playwright

from jobbank_session import NAV_TIMEOUT_MS, SESSION_FILE, has_live_session, session_exists
from run_history import record_run
from web_applier import ACTION_TIMEOUT_MS, BOT_BLOCK_PATTERN, SCREENSHOT_DIR

_RUN_HISTORY_STATUS = {
    "submitted": "Success",
    "submit_unconfirmed": "Failed",
    "failed": "Failed",
    "blocked": "Skipped",
    "no_session": "Skipped",
}

# Job Bank's exact post-click confirmation, verified live. Nothing else counts
# as proof the application actually went through.
CONFIRMATION_PATTERN = re.compile(
    r"successfully applied for this job through job bank", re.I
)

# Anchored to the whole button/link text so nothing else on the page (e.g. a
# "How to apply" info link) is mistaken for the real submit control.
DIRECT_APPLY_BUTTON_PATTERN = re.compile(r"^\s*direct\s*apply\s*$", re.I)


def apply_jobbank_direct(job: dict, cover_letter: str, resume_pdf: str) -> dict:
    """Thin logging wrapper around _apply_jobbank_direct — records the run to
    automation_runs.jsonl without altering its behavior."""
    start = time.time()
    result = _apply_jobbank_direct(job, cover_letter, resume_pdf)
    record_run(
        "Job Bank Direct Apply",
        f"{job.get('title', '?')} @ {job.get('company', '?')}",
        _RUN_HISTORY_STATUS.get(result.get("status"), "Skipped"),
        str(result.get("status")),
        duration_ms=int((time.time() - start) * 1000),
    )
    return result


def _find_direct_apply_button(page):
    """Return the first visible 'Direct Apply' control on the page, or None."""
    try:
        candidates = page.locator("a, button").all()
    except Exception:
        return None
    for el in candidates:
        try:
            if not el.is_visible(timeout=300):
                continue
            text = (el.inner_text(timeout=300) or "").strip()
            if DIRECT_APPLY_BUTTON_PATTERN.match(text):
                return el
        except Exception:
            continue
    return None


def _apply_jobbank_direct(job: dict, cover_letter: str, resume_pdf: str) -> dict:
    """Fire Job Bank's own Direct Apply using the saved session.

    Returns "submitted" only when the real post-click confirmation text is
    found, "submit_unconfirmed" when the button was clicked but confirmation
    couldn't be verified (a real click happened — this must never be
    misreported as merely "pending"), "failed" when the button couldn't be
    located at all, "blocked" for a bot-check interstitial, and "no_session"
    when there's no live session to use yet.
    """
    job_url = job["url"]

    if not session_exists() or not has_live_session(job_url):
        return {"status": "no_session", "ats": "jobbank", "screenshot": None}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(storage_state=str(SESSION_FILE))
            page = context.new_page()
            page.set_default_timeout(NAV_TIMEOUT_MS)
            page.goto(job_url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
            page.wait_for_timeout(1500)

            body_text = ""
            try:
                body_text = page.locator("body").inner_text(timeout=ACTION_TIMEOUT_MS) or ""
            except Exception:
                pass
            if BOT_BLOCK_PATTERN.search(body_text):
                browser.close()
                return {"status": "blocked", "ats": "jobbank", "screenshot": None}

            button = _find_direct_apply_button(page)
            if button is None:
                browser.close()
                return {"status": "failed", "ats": "jobbank", "screenshot": None}

            # This click is the real, final submission — not a step toward
            # revealing a form. See module docstring.
            button.click(timeout=ACTION_TIMEOUT_MS)
            page.wait_for_timeout(2500)

            confirm_text = ""
            try:
                confirm_text = page.locator("body").inner_text(timeout=ACTION_TIMEOUT_MS) or ""
            except Exception:
                pass

            screenshot = None
            try:
                screenshot = str(SCREENSHOT_DIR / f"{job['id']}.png")
                page.screenshot(path=screenshot, full_page=True)
            except Exception:
                screenshot = None

            browser.close()

            if CONFIRMATION_PATTERN.search(confirm_text):
                return {"status": "submitted", "ats": "jobbank", "screenshot": screenshot}
            return {"status": "submit_unconfirmed", "ats": "jobbank", "screenshot": screenshot}

    except Exception as e:
        print(f"[jobbank_apply] Failed on {job_url}: {e}")
        return {"status": "failed", "ats": "jobbank", "screenshot": None}
