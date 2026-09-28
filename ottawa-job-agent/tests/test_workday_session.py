"""Session-file bookkeeping for workday_session.py — no browser, no network.

His password is never in scope here: these tests only check that the right
file name is used per tenant and that a missing file is reported honestly.
"""

import workday_session as wsess


def test_session_file_is_scoped_per_tenant():
    assert wsess.session_file("goodlifefitness").name == ".workday_session_goodlifefitness.json"
    assert wsess.session_file("cheo").name == ".workday_session_cheo.json"


def test_session_file_name_is_case_insensitive():
    assert wsess.session_file("GoodLifeFitness").name == wsess.session_file("goodlifefitness").name


def test_session_exists_is_false_when_no_file_was_ever_captured(tmp_path, monkeypatch):
    monkeypatch.setattr(wsess, "SESSION_DIR", tmp_path)
    assert wsess.session_exists("goodlifefitness") is False


def test_session_exists_is_true_once_a_session_file_is_present(tmp_path, monkeypatch):
    monkeypatch.setattr(wsess, "SESSION_DIR", tmp_path)
    wsess.session_file("goodlifefitness").write_text("{}")
    assert wsess.session_exists("goodlifefitness") is True


def test_careers_url_is_built_from_the_registry(monkeypatch):
    monkeypatch.setattr(wsess, "load_known_workday", lambda: {"tenants": [
        {"tenant": "goodlifefitness", "wd_host": "wd3", "site": "Careers"},
    ]})
    assert wsess._careers_url("goodlifefitness") == (
        "https://goodlifefitness.wd3.myworkdayjobs.com/Careers")


def test_careers_url_is_none_for_an_unknown_tenant(monkeypatch):
    monkeypatch.setattr(wsess, "load_known_workday", lambda: {"tenants": []})
    assert wsess._careers_url("nonesuch") is None


def test_new_context_with_session_loads_the_saved_file(tmp_path, monkeypatch):
    monkeypatch.setattr(wsess, "SESSION_DIR", tmp_path)
    wsess.session_file("goodlifefitness").write_text("{}")

    calls = []

    class FakeBrowser:
        def new_context(self, **kwargs):
            calls.append(kwargs)
            return "context"

    result = wsess.new_context_with_session(FakeBrowser(), "goodlifefitness")

    assert result == "context"
    assert calls == [{"storage_state": str(wsess.session_file("goodlifefitness"))}]


def test_new_context_with_session_falls_back_to_a_fresh_context_when_unsaved(tmp_path, monkeypatch):
    monkeypatch.setattr(wsess, "SESSION_DIR", tmp_path)

    calls = []

    class FakeBrowser:
        def new_context(self, **kwargs):
            calls.append(kwargs)
            return "fresh-context"

    result = wsess.new_context_with_session(FakeBrowser(), "goodlifefitness")

    assert result == "fresh-context"
    assert calls == [{}]


def test_refresh_session_writes_the_rolling_cookies_back(tmp_path, monkeypatch):
    """Nothing updated the saved file after capture, so every run replayed an
    ever-staler snapshot until Workday dropped it server-side."""
    monkeypatch.setattr(wsess, "SESSION_DIR", tmp_path)
    saved = []

    class FakeContext:
        def storage_state(self, path=None):
            saved.append(path)

    assert wsess.refresh_session(FakeContext(), "goodlifefitness") is True
    assert saved == [str(wsess.session_file("goodlifefitness"))]


def test_refresh_session_keeps_the_old_file_when_the_write_fails(tmp_path, monkeypatch):
    """A stale-but-real session on disk beats losing it and costing him a
    manual sign-in."""
    monkeypatch.setattr(wsess, "SESSION_DIR", tmp_path)
    wsess.session_file("goodlifefitness").write_text('{"cookies": []}')

    class FakeContext:
        def storage_state(self, path=None):
            raise RuntimeError("target closed")

    assert wsess.refresh_session(FakeContext(), "goodlifefitness") is False
    assert wsess.session_file("goodlifefitness").read_text() == '{"cookies": []}'


class _FakeSignInLocator:
    def __init__(self, count, visible=True):
        self._count = count
        self._visible = visible

    @property
    def first(self):
        return self

    def count(self):
        return self._count

    def is_visible(self, timeout=None):
        return self._visible


class _FakePage:
    """A capture window that may still be painting, and may not even be on
    Workday.

    `paints_after` is how many polls pass before anything renders; 0 means it
    was already up, None means it never paints. `url` matters because the
    sign-in control he is judged by only exists on the tenant's own pages.
    """

    TENANT_URL = "https://goodlifefitness.wd3.myworkdayjobs.com/Careers"

    def __init__(self, locator, url=TENANT_URL, paints_after=0, raises=False):
        self._locator = locator
        self.url = url
        self.paints_after = paints_after
        self.raises = raises
        self.polls = 0

    def locator(self, selector):
        assert selector == wsess.SIGN_IN_LINK
        if self.raises:
            raise RuntimeError("frame detached")
        return self._locator

    def evaluate(self, script):
        self.polls += 1
        if self.paints_after is None:
            return 0
        return 7 if self.polls > self.paints_after else 0

    def wait_for_timeout(self, ms):
        return None


def _page(count, visible=True, **kw):
    return _FakePage(_FakeSignInLocator(count, visible=visible), **kw)


def test_a_visible_sign_in_control_means_not_signed_in():
    """Saving used to report success either way, so a logged-out capture looked
    identical on disk and only surfaced as a wasted wizard run later."""
    assert wsess._looks_signed_in(_page(1, visible=True), "goodlifefitness") is False


def test_no_sign_in_control_means_signed_in():
    assert wsess._looks_signed_in(_page(0), "goodlifefitness") is True


def test_a_present_but_hidden_sign_in_control_still_counts_as_signed_in():
    assert wsess._looks_signed_in(_page(1, visible=False), "goodlifefitness") is True


# --- the Sep 12 defect: "Signed in" reported from a page that was not Workday ---
#
# He ran the capture, was told "Signed in — saved session", and told me the
# same. The file held eight anonymous cookies and no localStorage, and the
# Careers home and candidate home both still showed Sign In. The check had the
# pre-fix shape: no Workday Sign In control anywhere on the page was read as a
# live session, and Google's OAuth page — where the last click of a Google
# sign-in leaves you — has no Workday controls at all. So the capture tool told
# him the opposite of the truth, and he passed it on in good faith.

def test_a_capture_left_on_googles_oauth_page_is_not_reported_as_signed_in():
    """The likely live path. Nothing on accounts.google.com carries Workday's
    Sign In control, so judging by its absence there answers a question about
    a page that cannot answer it."""
    page = _page(0, url="https://accounts.google.com/o/oauth2/v2/auth?client_id=x")
    assert wsess._looks_signed_in(page, "goodlifefitness") is False


def test_a_capture_on_another_workday_tenant_is_not_reported_as_signed_in():
    """Being signed into some other employer's Workday is not being signed into
    this one — each tenant is its own candidate database."""
    page = _page(0, url="https://cheo.wd10.myworkdayjobs.com/External_Site")
    assert wsess._looks_signed_in(page, "goodlifefitness") is False


def test_an_unpainted_tenant_page_is_not_reported_as_signed_in():
    """Same ordering trap the applier hit: the Workday SPA needs seconds to
    paint, and a page with nothing on it has no Sign In control either."""
    assert wsess._looks_signed_in(_page(0, paints_after=None), "goodlifefitness") is False


def test_a_tenant_page_that_paints_late_is_still_judged_honestly():
    assert wsess._looks_signed_in(_page(0, paints_after=3), "goodlifefitness") is True


def test_an_unreadable_page_is_not_reported_as_signed_in():
    """When the check itself fails there is no evidence of a session, and the
    safe reading is the one that sends him back to sign in again."""
    assert wsess._looks_signed_in(_page(0, raises=True), "goodlifefitness") is False


# --- a logged-out capture must not destroy a working one ---
#
# refresh_session already refuses to overwrite a good session with a logged-out
# one. capture_session had no such guard, so a mistimed Enter could cost a
# session that was still working.

def test_a_signed_in_capture_is_always_saved():
    assert wsess._should_save(signed_in=True, existing=False) is True
    assert wsess._should_save(signed_in=True, existing=True) is True


def test_a_logged_out_capture_is_saved_only_when_there_is_nothing_to_lose():
    assert wsess._should_save(signed_in=False, existing=False) is True
    assert wsess._should_save(signed_in=False, existing=True) is False


def test_the_applier_judges_sign_in_by_the_same_logic_as_the_capture():
    """A capture judging "signed in" differently from the run that consumes the
    file is how a logged-out session gets saved as a good one — which is exactly
    what happened on Sep 12, in the opposite direction."""
    import workday_applier

    assert workday_applier._SIGN_IN_LINK == wsess.SIGN_IN_LINK
    assert workday_applier._is_authenticated(_page(1, visible=True)) is False
    assert workday_applier._is_authenticated(_page(0)) is True
