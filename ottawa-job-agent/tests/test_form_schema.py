"""Question extraction: Greenhouse's API, and DOM scraping for everything else.

The Greenhouse tests run against a captured API payload rather than the live
board, so they stay offline and stable. The DOM test needs a real browser and
skips cleanly when Playwright's Chromium isn't installed.
"""

import json

import pytest

import form_schema

# Shape captured from boards-api.greenhouse.io/v1/boards/<token>/jobs/<id>?questions=true
GREENHOUSE_PAYLOAD = {
    "id": 4567890,
    "title": "Health Information Analyst",
    "questions": [
        {"label": "First Name", "required": True, "type": "input_text", "name": "first_name"},
        {"label": "Resume", "required": True, "type": "attachment", "name": "resume"},
        {"label": "Why do you want to work here?", "required": False,
         "type": "textarea", "name": "question_1"},
        {"label": "Are you legally authorized to work in Canada?", "required": True,
         "type": "yes_no", "name": "question_2",
         "options": [{"label": "Yes", "value": 1}, {"label": "No", "value": 0}]},
        {"label": "Which shifts are you available for?", "required": False,
         "type": "multi_select", "name": "question_3",
         "options": [{"label": "Days", "value": 1}, {"label": "Evenings", "value": 2},
                     {"label": "Overnight", "value": 3}]},
        {"label": "How did you hear about us?", "required": False,
         "type": "single_select", "name": "question_4",
         "options": [{"label": "Company website", "value": 1},
                     {"label": "Referral", "value": 2}]},
        {"label": "", "required": False, "type": "input_text", "name": "spacer"},
    ],
}


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise form_schema.requests.HTTPError(str(self.status_code))

    def json(self):
        if isinstance(self._payload, str):
            raise ValueError("not json")
        return self._payload


def test_board_token_and_job_id_parsed_from_a_posting_url():
    url = "https://boards.greenhouse.io/cityofottawa/jobs/4567890"
    assert form_schema._greenhouse_board_token(url) == "cityofottawa"
    assert form_schema._greenhouse_job_id(url) == "4567890"


def test_greenhouse_types_map_onto_the_engine_s_kinds():
    kinds = {
        form_schema._greenhouse_field(q)["label"]: form_schema._greenhouse_field(q)["kind"]
        for q in GREENHOUSE_PAYLOAD["questions"] if q["label"]
    }
    assert kinds["First Name"] == "text"
    assert kinds["Resume"] == "file"
    assert kinds["Why do you want to work here?"] == "textarea"
    assert kinds["Are you legally authorized to work in Canada?"] == "select"
    assert kinds["Which shifts are you available for?"] == "checkbox"
    assert kinds["How did you hear about us?"] == "select"


def test_greenhouse_field_keeps_required_flag_and_option_labels():
    q = GREENHOUSE_PAYLOAD["questions"][4]
    parsed = form_schema._greenhouse_field(q)
    assert parsed["required"] is False
    assert parsed["options"] == ["Days", "Evenings", "Overnight"]


def test_extract_greenhouse_fields_drops_unlabelled_questions(monkeypatch):
    monkeypatch.setattr(form_schema.requests, "get",
                        lambda *a, **kw: FakeResponse(GREENHOUSE_PAYLOAD))
    fields = form_schema.extract_greenhouse_fields(
        "https://boards.greenhouse.io/cityofottawa/jobs/4567890")

    assert len(fields) == 6  # the empty-label spacer is dropped
    assert all(f["label"] for f in fields)
    assert {"label", "kind", "required", "options", "name"} == set(fields[0])


def test_extracted_greenhouse_questions_feed_the_answer_engine(monkeypatch):
    """The two modules are only useful joined up: what Greenhouse reports has to
    be answerable by application_prefill without any reshaping in between."""
    import application_prefill as ap

    monkeypatch.setattr(form_schema.requests, "get",
                        lambda *a, **kw: FakeResponse(GREENHOUSE_PAYLOAD))
    fields = form_schema.extract_greenhouse_fields(
        "https://boards.greenhouse.io/cityofottawa/jobs/4567890")

    job = {"title": "Health Information Analyst", "company": "City of Ottawa",
           "location": "Ottawa, ON", "description": ""}
    answers = [ap.answer_field(f, job, resume_pdf="/tmp/r.pdf", generated_budget=0)
               for f in fields]
    by_label = {a["label"]: a for a in answers}

    assert by_label["Are you legally authorized to work in Canada?"]["answer"] == "Yes"
    assert by_label["How did you hear about us?"]["answer"] == "Company website"
    assert by_label["First Name"]["answer"]


@pytest.mark.parametrize("url", [
    "https://boards.greenhouse.io/cityofottawa",      # no job id
    "https://example.com/careers/12345",              # not a greenhouse path shape
])
def test_unparseable_url_returns_none_not_empty(url):
    """None means "lookup failed, fall back to the DOM"; [] would mean "this
    form genuinely has no questions" and would ship an empty package."""
    assert form_schema.extract_greenhouse_fields(url) is None


def test_network_failure_returns_none(monkeypatch):
    def boom(*a, **kw):
        raise form_schema.requests.ConnectionError("offline")

    monkeypatch.setattr(form_schema.requests, "get", boom)
    assert form_schema.extract_greenhouse_fields(
        "https://boards.greenhouse.io/cityofottawa/jobs/4567890") is None


def test_bad_json_returns_none(monkeypatch):
    monkeypatch.setattr(form_schema.requests, "get",
                        lambda *a, **kw: FakeResponse("<html>maintenance</html>"))
    assert form_schema.extract_greenhouse_fields(
        "https://boards.greenhouse.io/cityofottawa/jobs/4567890") is None


# --- DOM extraction (needs a browser) ---

DOM_FIXTURE = """
<form>
  <label for="fn">First name *</label>
  <input id="fn" name="first_name" type="text" required>

  <label for="em">Email</label>
  <input id="em" name="email" type="email">

  <label for="cl">Cover letter</label>
  <textarea id="cl" name="cover_letter"></textarea>

  <label for="auth">Are you legally authorized to work in Canada?</label>
  <select id="auth" name="auth"><option>Yes</option><option>No</option></select>

  <fieldset>
    <legend>Are you available for overnight shifts?</legend>
    <input type="radio" name="overnight" value="yes"> Yes
    <input type="radio" name="overnight" value="no"> No
  </fieldset>

  <input type="hidden" name="csrf" value="x">
  <input type="submit" value="Apply">
</form>
"""


@pytest.fixture
def dom_page():
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                      # browser binary not installed
            pytest.skip("Chromium unavailable: {}".format(e))
        page = browser.new_page()
        page.set_content(DOM_FIXTURE)
        yield page
        browser.close()


def test_dom_extraction_reads_labels_kinds_and_required(dom_page):
    fields = form_schema.extract_dom_fields(dom_page, "generic")
    by_label = {f["label"].rstrip(" *"): f for f in fields}

    assert by_label["First name"]["kind"] == "text"
    assert by_label["First name"]["required"] is True
    assert by_label["Email"]["kind"] == "email"
    assert by_label["Cover letter"]["kind"] == "textarea"
    assert by_label["Are you legally authorized to work in Canada?"]["kind"] == "select"
    assert by_label["Are you legally authorized to work in Canada?"]["options"] == ["Yes", "No"]


def test_dom_extraction_skips_hidden_and_submit_inputs(dom_page):
    names = [f["name"] for f in form_schema.extract_dom_fields(dom_page, "generic")]
    assert "csrf" not in names


def test_dom_extraction_collapses_a_radio_group_into_one_question(dom_page):
    fields = form_schema.extract_dom_fields(dom_page, "generic")
    overnight = [f for f in fields if f["name"] == "overnight"]
    assert len(overnight) == 1, "a Yes/No radio pair must not become two questions"
