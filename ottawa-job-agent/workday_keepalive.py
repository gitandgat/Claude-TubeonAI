"""Keep a saved Workday candidate session from idling out between agent runs.

The problem this exists for, measured on goodlifefitness.wd3: Workday drops a
candidate session on a server-side *idle* timer of roughly 85 minutes, not on
cookie expiry — a session captured at 17:45 on Sep 10 was already anonymous by
19:10 with 16 of its 19 cookies still unexpired. Every authenticated request
resets that clock, which is why several diagnostic runs in a row all found the
session live. launchd runs job_agent.py every four hours, so between two
scheduled runs the session sits untouched for far longer than the idle window
and is reliably dead by the next one. On Sep 13 the session was refreshed at
20:19 and was gone by the following morning's walk.

So this touches each tenant's Careers page on a shorter interval than the idle
window and writes the rolling cookies back, exactly as an agent run does. It is
the same refresh_session call the applier already makes; the only new thing is
that it happens on a cadence Workday's timer cannot outlive.

Deliberately narrow:

* It visits the Careers page, never a posting's /apply URL. Landing on /apply
  as a signed-in candidate drops straight into the wizard and would create a
  draft application on a posting every time this ran. Nothing here starts,
  fills, or submits an application.
* It writes the session back only while still signed in. Overwriting a good
  saved session with a logged-out one costs him a manual sign-in and buys
  nothing, so an expired session is reported and left alone.
* It never signs in. His password is not in this repository and this module is
  not the place it starts being. An expired session needs
  `python3 workday_session.py <tenant>`, which opens a real browser for him.

Not yet proven: whether touching the Careers page is enough to hold the
*apply-flow* session open, or whether Workday scopes that separately. The only
evidence that will settle it is a session that survives a gap longer than 85
minutes with nothing but this job running against it.

Usage:
    python3 workday_keepalive.py            # every tenant with a saved session
    python3 workday_keepalive.py goodlifefitness
"""

import sys
from datetime import datetime

from playwright.sync_api import sync_playwright

import workday_session

NAV_TIMEOUT_MS = 40000


def _stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _log(msg: str) -> None:
    print("[{}] {}".format(_stamp(), msg), flush=True)


def tenants_with_sessions() -> list:
    """Tenants that have something to keep alive.

    A tenant with no saved session is not a failure here — he simply has not
    signed into it — so it is skipped silently rather than reported every
    45 minutes for the life of the launchd job.
    """
    found = []
    for entry in workday_session.load_known_workday().get("tenants", []):
        tenant = (entry.get("tenant") or "").strip()
        if tenant and workday_session.session_exists(tenant):
            found.append(tenant)
    return found


def touch(tenant: str) -> bool:
    """One authenticated page load, then save the rolling cookies back.

    Returns True only when the session was live and was written back.
    """
    url = workday_session._careers_url(tenant)
    if not url:
        _log("{}: not in known_workday.json, skipping".format(tenant))
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = workday_session.new_context_with_session(browser, tenant)
            page = context.new_page()
            try:
                page.goto(url, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")
            except Exception as e:
                _log("{}: couldn't reach {} ({})".format(tenant, url, e))
                return False

            # _looks_signed_in polls until the page has painted before trusting
            # the absence of a Sign In control. Asking any sooner asks an empty
            # document, which is how two probes this month reported a perfectly
            # good session as expired.
            if not workday_session._looks_signed_in(page, tenant):
                _log("{}: session is no longer signed in — run "
                     "`python3 workday_session.py {}` to refresh it. Leaving the "
                     "saved file untouched.".format(tenant, tenant))
                return False

            if workday_session.refresh_session(context, tenant):
                _log("{}: still signed in, session refreshed".format(tenant))
                return True
            _log("{}: still signed in but the session file could not be "
                 "written".format(tenant))
            return False
        finally:
            browser.close()


def main(argv: list) -> int:
    targets = [argv[1]] if len(argv) > 1 else tenants_with_sessions()
    if not targets:
        _log("no saved Workday sessions to keep alive")
        return 0

    alive = 0
    for tenant in targets:
        try:
            if touch(tenant):
                alive += 1
        except Exception as e:
            # One tenant's bad day must not stop the others from being touched.
            _log("{}: keep-alive failed ({})".format(tenant, e))
    _log("{}/{} session(s) still alive".format(alive, len(targets)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
