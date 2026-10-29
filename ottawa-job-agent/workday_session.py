"""Workday session capture — his password never touches this code.

Each Workday tenant (GoodLife, later CHEO) is a separate candidate database, so
signing in means creating/using an account on the employer's own ATS. The
original design read WORKDAY_EMAIL / WORKDAY_PASSWORD from .env and drove
Playwright's own sign-in form, but Sahawat asked not to have his password
stored or typed by this codebase at all. This module replaces that: like
jobbank_session.py does for Job Bank Direct Apply, capture_session() opens a
real, visible browser on the tenant's Careers site, he signs in himself, and
only the resulting Playwright storage_state (cookies + localStorage) is saved
to disk. Automated runs load that file and reuse the session; the email and
password are never read, stored, or transmitted by this code.

Run manually once per tenant (and again whenever a saved session expires):
    python3 workday_session.py goodlifefitness
"""

import sys
import time
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright

from workday_source import WorkdaySource, _possible_categories, load_known_workday

SESSION_DIR = Path(__file__).resolve().parent
NAV_TIMEOUT_MS = 20000
ACTION_TIMEOUT_MS = 1500
PAINT_TIMEOUT_MS = 20000
PAINT_POLL_MS = 1000

# Workday's own "you're not authenticated" signal, and the same check
# workday_applier uses for saved-session liveness — an anonymous visitor sees
# it, a signed-in candidate doesn't. It lives here because both the capture and
# the applier need it, and a capture judging sign-in differently from the run
# that consumes the file is exactly how a logged-out session gets saved as good.
SIGN_IN_LINK = "[data-automation-id='utilityButtonSignIn'], [data-automation-id='signInLink']"


def has_painted(page) -> bool:
    """Whether this page has rendered anything a person could interact with.

    Workday's apply flow is a single-page app whose content area needs four to
    twelve seconds on the live GoodLife tenant; before that the document is a
    shell with a spinner. Counting interactive elements — not form fields, which
    the sign-in step has none of — is the cheapest tenant-neutral way to tell a
    page that is empty from one that is merely slow.
    """
    deadline = time.time() + PAINT_TIMEOUT_MS / 1000.0
    while time.time() < deadline:
        try:
            if page.evaluate(
                    "() => document.querySelectorAll('button, a, input').length") or 0:
                return True
        except Exception:
            return False
        page.wait_for_timeout(PAINT_POLL_MS)
    return False


def is_signed_in(page) -> bool:
    """True once Workday is treating this browser as a signed-in candidate.

    The Sign In control is Workday's own "you're not authenticated" signal
    across tenants, so seeing it is decisive. Not seeing it is not: an unpainted
    page has no Sign In control either, so absence only counts once the page has
    painted. Order matters — measured live on goodlifefitness.wd3, the control
    arrives in the same paint as the page's first twelve interactive elements,
    so asking beforehand always asks an empty document.

    Both failure directions resolve to False on purpose: the cost of a wrong
    False is one more manual sign-in, and the cost of a wrong True is a run that
    walks a wizard it was never inside, or a logged-out capture saved as good.

    The caller is responsible for knowing the page is on the tenant at all —
    see _looks_signed_in, which has to, because a capture window can be left
    anywhere.
    """
    if not has_painted(page):
        return False
    try:
        el = page.locator(SIGN_IN_LINK).first
        return not (el.count() and el.is_visible(timeout=ACTION_TIMEOUT_MS))
    except Exception:
        return False


def _on_tenant_page(page, tenant: str) -> bool:
    """Whether the capture window is actually sitting on this tenant's Workday.

    The applier never needs this — it drives the page itself and knows where it
    is. A capture does: he signs in by hand, and the last click of a Google
    sign-in leaves the window on accounts.google.com, which carries no Workday
    Sign In control and so reads as authenticated to a check that only looks for
    its absence. Another employer's Workday fails this too, and should: each
    tenant is its own candidate database.
    """
    try:
        host = (page.url or "").split("//", 1)[-1].split("/", 1)[0].lower()
    except Exception:
        return False
    return host.startswith(tenant.lower() + ".") and host.endswith("myworkdayjobs.com")


def _looks_signed_in(page, tenant: str) -> bool:
    return _on_tenant_page(page, tenant) and is_signed_in(page)


def _should_save(signed_in: bool, existing: bool) -> bool:
    """Whether to write this capture to disk.

    refresh_session already refuses to overwrite a live session with a
    logged-out one, for the obvious reason that it costs a manual sign-in and
    buys nothing. capture_session had no such guard, so a mistimed Enter could
    throw away a session that was still working. A logged-out capture is still
    worth saving when there is no file yet — the cookies are harmless and the
    next run reports the expiry honestly either way.
    """
    return signed_in or not existing


def session_file(tenant: str) -> Path:
    return SESSION_DIR / ".workday_session_{}.json".format(tenant.lower())


def session_exists(tenant: str) -> bool:
    return session_file(tenant).exists()


def _careers_url(tenant: str) -> Optional[str]:
    for entry in load_known_workday().get("tenants", []):
        if (entry.get("tenant") or "").lower() == tenant.lower():
            return "https://{}.{}.myworkdayjobs.com/{}".format(
                entry["tenant"], entry["wd_host"], entry["site"])
    return None


def _apply_url_for(tenant: str) -> Optional[str]:
    """A real posting's Apply page for this tenant, not the plain Careers
    homepage. Signing in from the Careers homepage never puts him through
    Workday's own apply-flow account gate — a separate "Create Account/Sign
    In" step that only shows up once an application is actually started — so
    a session captured there can look valid yet still fail deep in the
    wizard (confirmed live: 4 fresh-session GoodLife attempts on Sep 6 all
    stalled before Submit). Best-effort only: this is a convenience for the
    one-time interactive capture, never a critical path, so any failure here
    just falls back to the Careers homepage instead of blocking the capture."""
    for entry in load_known_workday().get("tenants", []):
        if (entry.get("tenant") or "").lower() != tenant.lower():
            continue
        try:
            jobs = WorkdaySource().fetch_all(categories=_possible_categories(entry))
        except Exception:
            return None
        for job in jobs:
            if (job.get("workday_tenant") or "").lower() == tenant.lower():
                return job["url"]
        return None
    return None


def capture_session(tenant: str) -> None:
    """Open a real, visible browser so he can log into this tenant's Workday
    candidate account himself. Only the resulting session cookies are saved —
    the password is never seen, read, or stored by this code."""
    careers_url = _careers_url(tenant)
    if not careers_url:
        print("[workday_session] Unknown tenant '{}' — check known_workday.json".format(tenant))
        return

    apply_url = _apply_url_for(tenant)
    url = apply_url or careers_url

    print("[workday_session] Opening {}".format(url))
    if apply_url:
        print("[workday_session] This is a real posting's Apply page, not the plain Careers site — click")
        print("[workday_session] 'Apply Manually' (or similar) so you reach Workday's own account gate for")
        print("[workday_session] the application wizard itself, and sign in / create your account there.")
    else:
        print("[workday_session] Couldn't find a live posting to open its Apply page directly, so this is")
        print("[workday_session] just the Careers homepage instead. Click into any job and hit Apply before")
        print("[workday_session] signing in, so the saved session also covers the wizard's own sign-in gate.")
    print("[workday_session] Nothing is submitted for you.")
    print("[workday_session] LEAVE THE BROWSER OPEN, come back here and press Enter — pressing Enter is what")
    print("[workday_session] saves the session, so closing the window first throws the sign-in away.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
        input()

        # Closing the window before pressing Enter used to raise here, so the
        # sign-in was lost with nothing but a traceback to explain it.
        try:
            signed_in = _looks_signed_in(page, tenant)
        except Exception:
            print("[workday_session] The browser window was already closed, so there's no session to save.")
            print("[workday_session] Re-run this and leave it open until you've pressed Enter here.")
            return
        if not _should_save(signed_in, session_exists(tenant)):
            browser.close()
            print("[workday_session] NOT SAVED. That page is not a signed-in {} page, so this".format(tenant))
            print("[workday_session] capture is logged out — and there is already a saved session on disk,")
            print("[workday_session] which overwriting would cost you for nothing.")
            print("[workday_session] Re-run, and before pressing Enter make sure the Workday window itself")
            print("[workday_session] (not Google's sign-in page) shows you signed in, past the wizard's own")
            print("[workday_session] Create Account/Sign In step.")
            return
        try:
            context.storage_state(path=str(session_file(tenant)))
        except Exception as e:
            print("[workday_session] Couldn't save the session: {}".format(e))
            return
        finally:
            browser.close()

    # Saving used to report success whether or not he'd actually signed in, so
    # a logged-out capture looked identical to a good one on disk and only
    # surfaced later as a wasted wizard run against the Sign In gate.
    if signed_in:
        print("[workday_session] Signed in — saved session to {}".format(session_file(tenant)))
    else:
        print("[workday_session] WARNING: saved {}, but that page is not a signed-in".format(
            session_file(tenant)))
        print("[workday_session] {} page — either Workday still shows its Sign In control,".format(tenant))
        print("[workday_session] or the window was left somewhere else entirely, which is where a Google")
        print("[workday_session] sign-in ends up. This session is probably logged out. Re-run and make sure")
        print("[workday_session] the Workday window itself shows you signed in, past the wizard's own")
        print("[workday_session] Create Account/Sign In step, before pressing Enter.")


def refresh_session(context, tenant: str) -> bool:
    """Write the session back after a run that was still signed in.

    Nothing used to update the saved file after capture_session(), so every
    automated run replayed the same snapshot from the moment he signed in and
    the file only ever got staler — a session captured at 17:45 on Sep 10 was
    already anonymous by 19:10, with 16 of its 19 cookies still unexpired, so
    Workday had dropped it server-side rather than the cookies timing out.
    Saving the rolling cookies back after each authenticated run is what keeps
    a regularly-running agent's session alive between his sign-ins.

    Only ever call this while still authenticated: overwriting a good saved
    session with a logged-out one would cost him a manual sign-in for nothing.
    """
    try:
        context.storage_state(path=str(session_file(tenant)))
        return True
    except Exception as e:
        # A stale-but-real session on disk beats losing it to a write error.
        print("[workday_session] Couldn't refresh saved session for {}: {}".format(tenant, e))
        return False


def new_context_with_session(browser, tenant: str):
    """A Playwright context pre-loaded with the saved session, or a fresh
    context if none has been captured yet. Callers should check
    session_exists() first when a fresh (logged-out) context isn't good
    enough for what they're about to do."""
    path = session_file(tenant)
    if path.exists():
        return browser.new_context(storage_state=str(path))
    return browser.new_context()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        tenants = [t["tenant"] for t in load_known_workday().get("tenants", []) if t.get("auto_apply")]
        print("Usage: python3 workday_session.py <tenant>")
        print("Auto-apply tenants needing a session: {}".format(", ".join(tenants) or "(none yet)"))
    else:
        capture_session(sys.argv[1])
