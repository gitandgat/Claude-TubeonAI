"""Workday auto-apply's degraded-outcome paths — no Playwright, no browser.

Two of _apply_on_workday's exits happen before `with sync_playwright()` is ever
reached: an unregistered/not-yet-approved tenant, and an approved tenant with no
(or an expired) saved session. Both are pure logic over known_workday.json and
workday_session.session_exists(), so they're covered here without touching a
browser. The scope guard is the whole point of workday_applier.py's design (see
its module docstring) — these tests exist to keep it from silently loosening.
"""

import pytest

import workday_applier as wa
import workday_session as wsess

GOODLIFE_ENTRY = {
    "tenant": "goodlifefitness", "wd_host": "wd3", "site": "Careers",
    "company_name": "GoodLife Fitness", "search_text": "Ottawa",
    "category": "goodlife", "auto_apply": True,
}

CHEO_ENTRY = {
    "tenant": "cheo", "wd_host": "wd10", "site": "External_Site",
    "company_name": "CHEO", "search_text": "Ottawa",
    "category": "health", "auto_apply": False,
}


def job(tenant=None, url="https://goodlifefitness.wd3.myworkdayjobs.com/en-US/Careers/job/Role/apply",
        job_id="job-1"):
    j = {"id": job_id, "title": "Personal Trainer", "company": "GoodLife Fitness", "url": url}
    if tenant is not None:
        j["workday_tenant"] = tenant
    return j


@pytest.fixture
def registry(monkeypatch):
    monkeypatch.setattr(wa, "load_known_workday", lambda: {"tenants": [GOODLIFE_ENTRY, CHEO_ENTRY]})


# --- tenant_for_job ---

def test_tenant_for_job_matches_on_the_recorded_workday_tenant_field(registry):
    assert wa.tenant_for_job(job(tenant="goodlifefitness")) == GOODLIFE_ENTRY


def test_tenant_for_job_match_is_case_insensitive(registry):
    assert wa.tenant_for_job(job(tenant="GoodLifeFitness")) == GOODLIFE_ENTRY


def test_tenant_for_job_falls_back_to_the_url_when_the_field_is_missing(registry):
    """Jobs that arrived through a path other than workday_source (e.g. a stale
    seen_jobs.json entry from before that field existed) still resolve."""
    assert wa.tenant_for_job(job(tenant=None)) == GOODLIFE_ENTRY


def test_tenant_for_job_is_none_for_a_url_with_no_workday_host(registry):
    assert wa.tenant_for_job(job(tenant=None, url="https://example.com/careers/apply")) is None


def test_tenant_for_job_is_none_for_a_tenant_not_in_the_registry(registry):
    """Discovering a new tenant never resolves it to an existing entry — it must
    be added to known_workday.json first, deliberately, before anything treats
    it as known."""
    assert wa.tenant_for_job(job(tenant="somebrandnewtenant")) is None


# --- auto_apply_allowed ---

def test_auto_apply_allowed_true_for_a_tenant_flagged_true(registry):
    assert wa.auto_apply_allowed(job(tenant="goodlifefitness")) is True


def test_auto_apply_allowed_false_for_a_tenant_flagged_false(registry):
    assert wa.auto_apply_allowed(job(tenant="cheo")) is False


def test_auto_apply_allowed_false_for_an_unregistered_tenant(registry):
    """The scope guard this module is built around: an unknown tenant is never
    approved by default, only by an explicit registry entry."""
    assert wa.auto_apply_allowed(job(tenant="somebrandnewtenant")) is False


# --- _apply_on_workday degraded paths (return before Playwright ever opens) ---

def test_unregistered_tenant_returns_prefilled_pending_review_without_a_browser(registry):
    result = wa._apply_on_workday(job(tenant="somebrandnewtenant"), "cover letter", "resume.pdf")

    assert result["status"] == "prefilled_pending_review"
    assert result["ats"] == "workday"
    assert "not approved for unattended Workday submission" in result["reason"]
    assert "this Workday tenant" in result["reason"]


def test_tenant_not_approved_for_auto_apply_returns_prefilled_pending_review(registry):
    result = wa._apply_on_workday(job(tenant="cheo"), "cover letter", "resume.pdf")

    assert result["status"] == "prefilled_pending_review"
    assert "CHEO is not approved for unattended Workday submission yet" == result["reason"]


def test_approved_tenant_with_no_saved_session_degrades_to_prefill(registry, monkeypatch):
    """GoodLife is approved, but a saved session is a separate precondition — his
    password can only ever reach a session file through workday_session.py's
    manual login flow, so a missing file must stop the run just as hard as an
    unapproved tenant does."""
    monkeypatch.setattr(wsess, "session_exists", lambda tenant: False)

    result = wa._apply_on_workday(job(tenant="goodlifefitness"), "cover letter", "resume.pdf")

    assert result["status"] == "prefilled_pending_review"
    assert "no saved Workday session for GoodLife Fitness" in result["reason"]
    assert "python3 workday_session.py goodlifefitness" in result["reason"]


def test_approved_tenant_with_a_saved_session_proceeds_past_the_guard(registry, monkeypatch):
    """Once both preconditions are met the function must actually try to open a
    browser next — proven here by making sync_playwright itself the failure
    point, which only happens if both early-return branches were skipped."""
    monkeypatch.setattr(wsess, "session_exists", lambda tenant: True)

    sentinel = RuntimeError("sync_playwright reached — guard passed")
    monkeypatch.setattr(wa, "sync_playwright", lambda: (_ for _ in ()).throw(sentinel))

    result = wa._apply_on_workday(job(tenant="goodlifefitness"), "cover letter", "resume.pdf")

    assert result["status"] == "failed"
    assert result["reason"] == str(sentinel)


# --- session liveness: absence of Sign In only counts on a page that painted ---
#
# The Sep 11 live run ended on GoodLife's "Create Account/Sign In" step with a
# dead saved session. _is_authenticated got that right *because the page had
# rendered*. On an earlier run against the same tenant it reported
# authenticated:True against a blank page holding nothing but a spinner — the
# Workday SPA needs four to twelve seconds to paint, and an unpainted page has
# no Sign In control either. Absence of the control is only evidence once
# there is a page to be absent from.

class _AuthLocator:
    def __init__(self, page):
        self.page = page

    @property
    def first(self):
        return self

    def count(self):
        if self.page.raises:
            raise RuntimeError("frame detached")
        # Measured live on goodlifefitness.wd3: the Sign In control arrives in
        # the same paint as the first interactive elements (t+3.1s, 12 controls,
        # Sign In among them). Before that the document is empty of both, so a
        # fake that offers Sign In on an unpainted page would be describing a
        # state the real tenant never passes through.
        if not self.page.is_painted():
            return 0
        return 1 if self.page.sign_in_present else 0

    def is_visible(self, timeout=None):
        return self.page.sign_in_visible


class FakeAuthPage:
    """A Workday page that may still be painting.

    `paints_after` is how many polls pass before anything renders; 0 means it
    was already up, and None means it never paints at all.
    """

    def __init__(self, sign_in_present=False, sign_in_visible=False,
                 paints_after=0, raises=False):
        self.sign_in_present = sign_in_present
        self.sign_in_visible = sign_in_visible
        self.paints_after = paints_after
        self.raises = raises
        self.polls = 0
        self.sign_in_reads_before_paint = 0

    def is_painted(self):
        if self.paints_after is None:
            painted = False
        else:
            painted = self.polls > self.paints_after
        if not painted:
            self.sign_in_reads_before_paint += 1
        return painted

    def locator(self, selector):
        return _AuthLocator(self)

    def evaluate(self, script):
        self.polls += 1
        if self.paints_after is None:
            return 0
        return 7 if self.polls > self.paints_after else 0

    def wait_for_timeout(self, ms):
        return None


def test_a_blank_page_is_not_reported_as_signed_in():
    """The defect this pins. A spinner-only page has no Sign In control, and
    the old check read that absence as a live candidate session — so the run
    walked into a wizard it was never inside and reported the wizard broken
    instead of the session expired."""
    page = FakeAuthPage(sign_in_present=False, paints_after=None)
    assert wa._is_authenticated(page) is False


def test_the_sign_in_control_is_not_read_until_the_page_has_painted():
    """Ordering, which a live run caught after the first fix went in. Asking
    for Sign In at t+0 and only then waiting for paint answers the question
    against an empty document every time: the control is absent because nothing
    exists yet, and the wait that follows cannot retract the answer. Measured
    live, this page reported authenticated:True 3.1s into a load whose very
    next frame carried a Sign In button."""
    page = FakeAuthPage(sign_in_present=True, sign_in_visible=True, paints_after=3)
    assert wa._is_authenticated(page) is False
    assert page.sign_in_reads_before_paint == 0


def test_a_page_that_paints_late_with_no_sign_in_control_is_signed_in():
    """The other half: a genuinely signed-in page on a slow tenant must not be
    called anonymous just because it took a few seconds to render."""
    page = FakeAuthPage(sign_in_present=False, paints_after=3)
    assert wa._is_authenticated(page) is True


def test_a_visible_sign_in_control_means_not_signed_in():
    page = FakeAuthPage(sign_in_present=True, sign_in_visible=True)
    assert wa._is_authenticated(page) is False


def test_a_sign_in_control_in_the_markup_but_hidden_does_not_block_a_live_session():
    page = FakeAuthPage(sign_in_present=True, sign_in_visible=False, paints_after=0)
    assert wa._is_authenticated(page) is True


def test_an_unreadable_page_is_not_reported_as_signed_in():
    """The old code's `except Exception: return True`. When the check itself
    fails there is no evidence of a session, and the safe reading is the one
    that degrades to the prefill package rather than the one that starts
    filling a form."""
    page = FakeAuthPage(raises=True)
    assert wa._is_authenticated(page) is False
