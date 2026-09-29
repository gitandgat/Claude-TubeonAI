"""The liveness gate in apply_interested.py.

Every case here came from a real run: four swiped jobs were packaged, three of
them had already closed, and not one of the three returned an HTTP error. Workday
serves 200 with a JavaScript shell and renders its own 404 client-side; Jobvite
silently falls back to the careers landing page; and Njoyn answers scripted GETs
with a Radware CAPTCHA that has no job content on it either. So the gate is tested
against the three shapes that actually occur, plus the failure modes where it must
fail OPEN — a wrong "closed" throws away a real application.
"""

import pytest

import apply_interested as ai


class _Resp:
    def __init__(self, text="", status_code=200, payload=None):
        self.text = text
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise ai.requests.HTTPError(str(self.status_code))

    def json(self):
        return self._payload


@pytest.fixture(autouse=True)
def _clear_cache():
    ai._workday_list_cache.clear()
    yield
    ai._workday_list_cache.clear()


# --- title probe ----------------------------------------------------------

def test_probe_drops_the_bracketed_tail():
    # The employer edits "(TFT 1.0 FTE)" and the posting is still the same job.
    assert ai._title_probe("Manager, Patient Care Services (TFT 1.0 FTE)") == \
        "manager patient care services"


def test_probe_caps_at_four_words_and_drops_short_ones():
    assert ai._title_probe(
        "Data Analyst, Information Services, Business Intelligence (ITC)") == \
        "data analyst information services"


def test_probe_is_empty_for_a_titleless_job():
    assert ai._title_probe("") == ""


# --- page text -----------------------------------------------------------

def test_visible_text_joins_a_title_split_across_tags():
    # CIHI renders the comma inside its own element; the phrase exists only once
    # the markup is gone.
    html = "<h1>Program Specialist,<span> Digital Solutions</span></h1>"
    assert "program specialist digital solutions" in ai._visible_text(html)


def test_visible_text_ignores_script_and_style_bodies():
    html = "<style>.closed{}</style><script>var x='no longer'</script><p>Nurse</p>"
    assert ai._visible_text(html) == "nurse"


def test_bot_wall_is_recognised():
    assert ai._BOT_WALL_PATTERN.search("Radware Captcha Page")
    assert not ai._BOT_WALL_PATTERN.search("program specialist digital solutions")


# --- Workday -------------------------------------------------------------

CHEO_URL = ("https://cheo.wd10.myworkdayjobs.com/en-US/External_Site/job/"
            "Research-2/Data-Analyst_JR7982/apply")


def test_workday_url_parses_tenant_site_and_req():
    m = ai._WORKDAY_URL.search(CHEO_URL)
    assert (m.group("tenant"), m.group("host"), m.group("site"), m.group("req")) == \
        ("cheo", "wd10", "External_Site", "JR7982")


def _stub_workday(monkeypatch, paths, total=None):
    def fake_post(url, **kwargs):
        offset = kwargs["json"]["offset"]
        batch = [{"externalPath": p} for p in paths[offset:offset + 20]]
        return _Resp(payload={"jobPostings": batch,
                              "total": total if total is not None else len(paths)})
    monkeypatch.setattr(ai.requests, "post", fake_post)


def test_workday_posting_still_listed_is_live(monkeypatch):
    _stub_workday(monkeypatch, ["/job/Research/Data-Analyst_JR7982"])
    assert ai._posting_is_live({"title": "Data Analyst"}, CHEO_URL) == (True, "")


def test_workday_posting_absent_from_the_list_is_closed(monkeypatch):
    _stub_workday(monkeypatch, ["/job/Somewhere/Behaviour-Therapist_JR8100"])
    live, why = ai._posting_is_live({"title": "Data Analyst"}, CHEO_URL)
    assert not live
    assert "JR7982" in why and "cheo" in why


def test_workday_pages_past_the_first_twenty(monkeypatch):
    # The req that matters is on page 2 — reading only page 1 would close a live job.
    paths = ["/job/x/Filler_JR%04d" % n for n in range(25)]
    paths[24] = "/job/x/Data-Analyst_JR7982"
    _stub_workday(monkeypatch, paths)
    assert ai._posting_is_live({"title": "Data Analyst"}, CHEO_URL)[0]


def test_workday_list_is_fetched_once_per_tenant(monkeypatch):
    calls = []

    def fake_post(url, **kwargs):
        calls.append(url)
        return _Resp(payload={"jobPostings": [{"externalPath": "/job/x/A_JR7982"}],
                              "total": 1})
    monkeypatch.setattr(ai.requests, "post", fake_post)
    ai._posting_is_live({"title": "A"}, CHEO_URL)
    ai._posting_is_live({"title": "B"}, CHEO_URL.replace("JR7982", "JR8043"))
    assert len(calls) == 1


def test_workday_fetch_failure_fails_open(monkeypatch):
    def boom(url, **kwargs):
        raise ai.requests.ConnectionError("dns")
    monkeypatch.setattr(ai.requests, "post", boom)
    assert ai._posting_is_live({"title": "Data Analyst"}, CHEO_URL) == (True, "")


# --- generic pages -------------------------------------------------------

JOBVITE_URL = "https://jobs.jobvite.com/theroyal/job/abc123"


def _stub_get(monkeypatch, resp):
    monkeypatch.setattr(ai.requests, "get", lambda url, **kwargs: resp)


def test_title_still_on_the_page_is_live(monkeypatch):
    _stub_get(monkeypatch, _Resp("<h1>Manager, Patient Care Services</h1>"))
    job = {"title": "Manager, Patient Care Services (TFT 1.0 FTE)"}
    assert ai._posting_is_live(job, JOBVITE_URL) == (True, "")


def test_landing_page_fallback_is_closed(monkeypatch):
    # What The Royal actually served: the careers board, HTTP 200, no job on it.
    _stub_get(monkeypatch, _Resp("<title>Job Opportunities | The Royal</title>"))
    job = {"title": "Manager, Patient Care Services (TFT 1.0 FTE)"}
    live, why = ai._posting_is_live(job, JOBVITE_URL)
    assert not live
    assert "manager patient care services" in why


def test_http_error_is_closed(monkeypatch):
    _stub_get(monkeypatch, _Resp("gone", status_code=404))
    live, why = ai._posting_is_live({"title": "Nurse Practitioner"}, JOBVITE_URL)
    assert not live
    assert "404" in why


def test_network_error_fails_open(monkeypatch):
    def boom(url, **kwargs):
        raise ai.requests.Timeout("slow")
    monkeypatch.setattr(ai.requests, "get", boom)
    assert ai._posting_is_live({"title": "Nurse"}, JOBVITE_URL) == (True, "")


def test_a_job_with_no_title_is_never_closed_by_this_check(monkeypatch):
    def boom(url, **kwargs):
        raise AssertionError("should not fetch without a probe")
    monkeypatch.setattr(ai.requests, "get", boom)
    assert ai._posting_is_live({"title": ""}, JOBVITE_URL) == (True, "")


# --- bot wall that a real browser can see past ---------------------------

NJOYN_URL = "https://clients.njoyn.com/cl3/xweb/xweb.asp?Jobid=J0926-0055"


def test_closed_wording_is_taken_as_proof(monkeypatch):
    # What CIHI actually served the morning after its closing date, wrapped in the
    # employer's full site chrome — so absence-of-title is not the only signal.
    _stub_get(monkeypatch, _Resp("<p>Sorry, this job is no longer available.</p>"))
    live, why = ai._posting_is_live(
        {"title": "Program Specialist, Digital Solutions"}, NJOYN_URL)
    assert not live
    assert "no longer available" in why


def test_bot_wall_falls_back_to_a_rendered_page(monkeypatch):
    _stub_get(monkeypatch, _Resp("<h1>Radware Captcha Page</h1> request unblock"))
    monkeypatch.setattr(ai, "_render_visible_text",
                        lambda url: "careers cihi sorry this job is no longer available")
    live, why = ai._posting_is_live(
        {"title": "Program Specialist, Digital Solutions"}, NJOYN_URL)
    assert not live
    assert "no longer available" in why


def test_rendered_page_showing_the_job_is_live(monkeypatch):
    _stub_get(monkeypatch, _Resp("<h1>Radware Captcha Page</h1>"))
    monkeypatch.setattr(ai, "_render_visible_text",
                        lambda url: "program specialist digital solutions job number j0926")
    assert ai._posting_is_live(
        {"title": "Program Specialist, Digital Solutions"}, NJOYN_URL) == (True, "")


def test_wall_behind_the_wall_still_fails_open(monkeypatch):
    _stub_get(monkeypatch, _Resp("<h1>Radware Captcha Page</h1>"))
    monkeypatch.setattr(ai, "_render_visible_text", lambda url: "radware captcha page")
    assert ai._posting_is_live({"title": "Program Specialist"}, NJOYN_URL) == (True, "")


def test_browser_unavailable_fails_open(monkeypatch):
    _stub_get(monkeypatch, _Resp("<h1>Radware Captcha Page</h1>"))
    monkeypatch.setattr(ai, "_render_visible_text", lambda url: None)
    assert ai._posting_is_live({"title": "Program Specialist"}, NJOYN_URL) == (True, "")


def test_a_healthy_page_never_launches_a_browser(monkeypatch):
    # The expensive path must stay reserved for bot walls.
    _stub_get(monkeypatch, _Resp("<h1>Program Specialist, Digital Solutions</h1>"))

    def boom(url):
        raise AssertionError("should not render a page that fetched fine")
    monkeypatch.setattr(ai, "_render_visible_text", boom)
    assert ai._posting_is_live(
        {"title": "Program Specialist, Digital Solutions"}, NJOYN_URL) == (True, "")
