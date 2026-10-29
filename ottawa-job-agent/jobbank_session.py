"""Job Bank session capture + liveness check for Direct Apply auto-apply.

Job Bank's own "Direct Apply" postings require the applicant's personal Job
Bank sign-in — there is no honest way to submit those without it. This module
never touches Sahawat's password: capture_session() opens a real, visible
browser so he can log in himself, then persists only the resulting session
cookies (Playwright's storage_state) to SESSION_FILE. Automated runs load
that file to reuse the authenticated session; his credentials are never
read, stored, or transmitted by this code.

Run manually once (and again whenever the saved session expires):
    python3 jobbank_session.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

SESSION_FILE = Path(__file__).resolve().parent / ".jobbank_session.json"
LOGIN_URL = "https://www.jobbank.gc.ca/login"
NAV_TIMEOUT_MS = 20000

# Confirmed live (server-rendered) on a logged-out Direct Apply posting's detail
# page — see jobbank_source.py's _classify_apply override. Its continued
# presence on a real Direct Apply posting, loaded with the saved session, is
# the only reliable signal available (without guessing at markup for an
# authenticated page this code has never observed) that the session expired.
SIGN_IN_MARKER = "sign in to apply directly"


def session_exists() -> bool:
    return SESSION_FILE.exists()


def capture_session() -> None:
    """Open a real, visible browser for Sahawat to log into Job Bank himself.
    Only the resulting session cookies are saved — never the password."""
    print(f"[jobbank_session] Opening {LOGIN_URL} — log in with your Job Bank account,")
    print("[jobbank_session] then come back here and press Enter (nothing is submitted for you).")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
        input("Press Enter once you're signed in to Job Bank... ")
        context.storage_state(path=str(SESSION_FILE))
        browser.close()
    print(f"[jobbank_session] Session saved to {SESSION_FILE}")


def has_live_session(job_url: str) -> bool:
    """Cheaply check whether the saved session is still authenticated, using a
    real Direct Apply posting's page as ground truth. Returns False without
    launching a browser when no session has ever been captured, so the
    existing FYI-only path costs nothing extra until Sahawat opts in."""
    if not session_exists():
        return False
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(storage_state=str(SESSION_FILE))
            page = context.new_page()
            page.goto(job_url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
            page.wait_for_timeout(1000)
            body_text = ""
            try:
                body_text = page.locator("body").inner_text(timeout=1500) or ""
            except Exception:
                pass
            browser.close()
            return SIGN_IN_MARKER not in body_text.lower()
    except Exception:
        return False


if __name__ == "__main__":
    capture_session()
