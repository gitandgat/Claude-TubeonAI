"""Three Ottawa health boards (Njoyn, SuccessFactors, Jobvite) → pipeline jobs.

All fixtures are trimmed copies of the real markup captured 2026-09-07. Every
test is offline: the fetchers take a session object, so a fake one stands in
for requests, and the Njoyn fetcher is exercised through its parsers only
(the browser step is a thin wrapper around them).
"""

import pytest

import health_boards_source as hb

CIHI = {"kind": "njoyn", "company_name": "CIHI", "cl": "cl3", "clid": "53103", "category": "health"}
CITY = {"kind": "successfactors", "company_name": "City of Ottawa",
        "base_url": "https://jobs-emplois.ottawa.ca/city-jobs", "queries": ["health"], "category": "municipal"}
ROYAL = {"kind": "jobvite", "company_name": "The Royal", "slug": "theroyal",
         "referer": "https://www.theroyal.ca/jobs/", "category": "health"}


# --- SuccessFactors ---

SF_PAGE = """
<tr class="data-row"><td class="colTitle">
  <span class="jobTitle hidden-phone">
    <a href="/city-jobs/job/Ottawa%2C-ON-Systems-Analyst-ON/1291524947/" class="jobTitle-link">Systems Analyst, Transit Technology</a>
  </span>
  <div class="jobdetail-phone visible-phone"><span class="jobTitle visible-phone">
    <a class="jobTitle-link" href="/city-jobs/job/Ottawa%2C-ON-Systems-Analyst-ON/1291524947/">Systems Analyst, Transit Technology</a>
  </span></div>
</td></tr>
<tr class="data-row"><td class="colTitle">
  <a href="/city-jobs/job/Ottawa%2C-ON-Health-Information-Analyst-ON/1291500000/" class="jobTitle-link">Health Information Management Analyst</a>
  <a class="jobTitle-link" href="/city-jobs/job/Ottawa%2C-ON-Health-Information-Analyst-ON/1291500000/">Health Information Management Analyst</a>
</td></tr>
"""

SF_DETAIL = """
<span class="jobdescription"><p><b>Requisition ID:</b> 23513<br/><b>Department:</b> Ottawa Public Health<br/>
<b>Application Close:</b> 30/09/2026</p><p>Maintains the electronic medical record.</p></span>
<div class="job-apply bottom"><a href="/talentcommunity/apply/1291500000/?locale=en_GB">Apply now</a></div>
"""


def test_sf_rows_dedupe_the_desktop_and_phone_anchors():
    rows = hb.parse_sf_rows(SF_PAGE)
    assert [r["title"] for r in rows] == ["Systems Analyst, Transit Technology",
                                          "Health Information Management Analyst"]
    assert rows[0]["path"] == "/city-jobs/job/Ottawa%2C-ON-Systems-Analyst-ON/1291524947/"


def test_sf_detail_reads_description_and_close_date():
    parsed = hb.parse_sf_detail(SF_DETAIL)
    assert "electronic medical record" in parsed["description"]
    assert "Apply now" not in parsed["description"]
    assert parsed["deadline"] == "2026-09-30"


class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text, self.status_code = text, status_code


class FakeSession:
    """Serves the SF search page once, then an empty page, and the detail page
    for any posting URL. Records every URL so the tests can count requests."""

    def __init__(self, search_pages, detail_html):
        self.search_pages, self.detail_html, self.calls = list(search_pages), detail_html, []

    def get(self, url, headers=None, params=None, timeout=None):
        self.calls.append((url, dict(params or {})))
        if url.endswith("/search/"):
            return FakeResponse(self.search_pages.pop(0) if self.search_pages else "")
        return FakeResponse(self.detail_html)


def test_sf_fetch_builds_jobs_and_skips_seen_without_a_detail_request(monkeypatch):
    monkeypatch.setattr(hb.time, "sleep", lambda *_: None)
    seen_id = hb.make_id("Systems Analyst, Transit Technology", "City of Ottawa",
                         "/city-jobs/job/Ottawa%2C-ON-Systems-Analyst-ON/1291524947/")
    session = FakeSession([SF_PAGE], SF_DETAIL)

    jobs = hb.fetch_successfactors(CITY, {seen_id}, session)

    assert [j["title"] for j in jobs] == ["Health Information Management Analyst"]
    detail_calls = [u for u, _ in session.calls if "/job/" in u]
    assert detail_calls == ["https://jobs-emplois.ottawa.ca/city-jobs/job/Ottawa%2C-ON-Health-Information-Analyst-ON/1291500000/"]
    job = jobs[0]
    assert job["category"] == "health_informatics"
    assert job["always_notify"] is True
    assert job["apply_target"] == "employer_site"
    assert job["source"] == "City of Ottawa (SuccessFactors)"
    assert job["deadline"] == "2026-09-30"
    assert job["url"].startswith("https://jobs-emplois.ottawa.ca/city-jobs/job/")


def test_sf_search_stops_after_a_short_page(monkeypatch):
    monkeypatch.setattr(hb.time, "sleep", lambda *_: None)
    session = FakeSession([SF_PAGE, SF_PAGE], SF_DETAIL)
    hb.fetch_successfactors(CITY, set(), session)
    search_calls = [p for u, p in session.calls if u.endswith("/search/")]
    assert len(search_calls) == 1  # two rows < page size, so no second page
    assert search_calls[0]["startrow"] == 0 and search_calls[0]["q"] == "health"


def test_a_non_health_city_posting_keeps_the_boards_own_category(monkeypatch):
    monkeypatch.setattr(hb.time, "sleep", lambda *_: None)
    session = FakeSession([SF_PAGE], "<span class=\"jobdescription\">Transit fleet scheduling.</span>")
    jobs = hb.fetch_successfactors(CITY, set(), session)
    transit = next(j for j in jobs if j["title"].startswith("Systems Analyst"))
    assert transit["category"] == "municipal"
    assert transit["always_notify"] is False


# --- Jobvite ---

JV_PAGE = """
<table class="jv-job-list"><tr><th>Title</th></tr>
<tr> <td class="jv-job-list-name"> <a href="/theroyal/job/olSHAfwe">Financial Analyst (TFT 1.0 FTE)</a> </td>
     <td>Finance</td><td>ROM26-170E</td><td class="jv-job-list-location"> Ottawa, Ontario </td> </tr>
<tr> <td class="jv-job-list-name"> <a href="/theroyal/job/oBROCKvl">Registered Nurse</a> </td>
     <td>Forensics</td><td>ROM26-171E</td><td class="jv-job-list-location"> Brockville, Ontario </td> </tr>
<tr> <td class="jv-job-list-name"> <a href="/theroyal/job/oDATAfwe">Clinical Informatics Specialist</a> </td>
     <td>IMHR</td><td>ROM26-172E</td><td class="jv-job-list-location"> Ottawa, Ottawa </td> </tr>
</table>
"""

JV_DETAIL = """
<p class="jv-job-detail-meta"> Finance/Accounting<span class='jv-inline-separator'></span> Ottawa, Ontario </p>
<div class="jv-job-detail-top-actions"><a class="jv-button jv-button-apply" href="/theroyal/job/olSHAfwe/apply">Apply</a></div>
<div class="jv-job-detail-description" ng-non-bindable><p class="blueHeading"><strong>Position Information</strong></p>
<p>Supports the EHR reporting team.</p></div>
<div class="jv-job-detail-bottom-actions"><a href="/theroyal/job/olSHAfwe/apply">Apply</a></div>
"""


def test_jobvite_rows_carry_title_path_and_location():
    rows = hb.parse_jobvite_rows(JV_PAGE)
    assert len(rows) == 3
    assert rows[0] == {"path": "/theroyal/job/olSHAfwe", "title": "Financial Analyst (TFT 1.0 FTE)",
                       "location": "Ottawa, Ontario"}


def test_jobvite_detail_stops_before_the_bottom_apply_button():
    parsed = hb.parse_jobvite_detail(JV_DETAIL)
    assert "EHR reporting team" in parsed["description"]
    assert "Apply" not in parsed["description"]
    assert parsed["meta"] == "Finance/Accounting Ottawa, Ontario"


class JobviteSession(FakeSession):
    def get(self, url, headers=None, params=None, timeout=None):
        self.calls.append((url, dict(params or {}), dict(headers or {})))
        return FakeResponse(self.search_pages[0] if url.endswith("/jobs") else self.detail_html)


def test_jobvite_fetch_drops_other_campuses_and_sends_the_iframe_params(monkeypatch):
    monkeypatch.setattr(hb.time, "sleep", lambda *_: None)
    session = JobviteSession([JV_PAGE], JV_DETAIL)

    jobs = hb.fetch_jobvite(ROYAL, set(), session)

    assert [j["title"] for j in jobs] == ["Financial Analyst (TFT 1.0 FTE)", "Clinical Informatics Specialist"]
    listing_url, params, headers = session.calls[0]
    assert listing_url == "https://jobs.jobvite.com/theroyal/jobs"
    assert params == {"nl": "1", "fr": "false"}
    assert headers["Referer"] == "https://www.theroyal.ca/jobs/"
    by_title = {j["title"]: j for j in jobs}
    assert by_title["Clinical Informatics Specialist"]["category"] == "health_informatics"
    # The shared detail fixture mentions the EHR, but that's the description:
    # a finance title stays health_other and score-gated.
    assert by_title["Financial Analyst (TFT 1.0 FTE)"]["category"] == "health_other"
    assert by_title["Financial Analyst (TFT 1.0 FTE)"]["always_notify"] is False
    assert by_title["Financial Analyst (TFT 1.0 FTE)"]["url"] == "https://jobs.jobvite.com/theroyal/job/olSHAfwe"


# --- Njoyn ---

NJ_PAGE = """
<table><tr><th>Job number</th><th>Job title</th><th>Department</th><th>Category</th><th>Job Type</th><th>City</th></tr>
<tr class=" oddTableDataRow"><td>J0426-0319</td><td><a title="View job details" href="xweb.asp?NTKN=c&amp;clid=53103&amp;Page=JobDetails&amp;Jobid=J0426-0319&amp;BRID=356314&amp;lang=1">Transformation Project Manager</a></td><td>PMO</td><td>Project Management</td><td>Contract</td><td>Toronto, Ottawa</td></tr>
<tr class=" evenTableDataRow"><td>J0826-0663</td><td><a title="View job details" href="xweb.asp?NTKN=c&amp;clid=53103&amp;Page=JobDetails&amp;Jobid=J0826-0663&amp;BRID=361119&amp;lang=1">Co-op Student, Digital Solutions</a></td><td>Digital Solutions</td><td>Co-op</td><td>Co-op Student</td><td>Toronto</td></tr>
</table>
"""

NJ_DETAIL = """
<div id="njnContentContainer"><nav>Careers Help/Register</nav>
Job number: J0426-0319 Job title: Transformation Project Manager Job Type: Contract Vacancy Type: New
Location: Toronto, Ottawa, Ontario, Canada Number of positions: 3 Contract Duration : 1 year
Date posted: September 2, 2026 Closing date: September 30, 2026 Compensation: $92,846.00 - $109,231.00/year
<p>Who we are: passionate about health data and clinical informatics.</p></div>
"""


def test_njoyn_rows_read_every_column_and_unescape_the_link():
    rows = hb.parse_njoyn_rows(NJ_PAGE)
    assert len(rows) == 2
    assert rows[0]["jobid"] == "J0426-0319"
    assert rows[0]["title"] == "Transformation Project Manager"
    assert rows[0]["city"] == "Toronto, Ottawa"
    assert rows[0]["href"] == "xweb.asp?NTKN=c&clid=53103&Page=JobDetails&Jobid=J0426-0319&BRID=356314&lang=1"


def test_njoyn_detail_reads_dates_location_and_drops_the_nav_prefix():
    parsed = hb.parse_njoyn_detail(NJ_DETAIL)
    assert parsed["deadline"] == "2026-09-30"
    assert parsed["posted_date"] == "2026-09-02"
    assert parsed["location"] == "Toronto, Ottawa, Ontario, Canada"
    assert parsed["description"].startswith("Job number:")
    assert "Help/Register" not in parsed["description"]


@pytest.mark.parametrize("city,kept", [("Toronto, Ottawa", True), ("Ottawa", True), ("Toronto", False),
                                       ("Remote - Canada", True), ("Montreal", False)])
def test_njoyn_city_filter_keeps_any_ottawa_listing(city, kept):
    assert hb._is_ottawa_or_remote(city) is kept


def test_njoyn_listing_url_comes_from_the_registry_row():
    assert hb.njoyn_listing_url(CIHI) == "https://clients.njoyn.com/cl3/xweb/xweb.asp?CLID=53103&page=joblisting&lang=1"


def test_njoyn_job_shape_matches_the_other_boards():
    parsed = hb.parse_njoyn_detail(NJ_DETAIL)
    job = hb._to_job(CIHI, title="Transformation Project Manager", url="https://clients.njoyn.com/x",
                     location=parsed["location"], description=parsed["description"], job_key="J0426-0319",
                     deadline=parsed["deadline"], posted_date=parsed["posted_date"])
    assert job["category"] == "health_other"  # informatics only in the description
    assert job["source"] == "CIHI (Njoyn)"
    assert job["ats"] == "njoyn"
    assert job["id"] == hb.make_id("Transformation Project Manager", "CIHI", "J0426-0319")


# --- shared behaviour ---

@pytest.mark.parametrize("title,expected", [
    ("Senior Analyst, Health Workforce Information, Data Development", "health_informatics"),
    ("Health Information Management Analyst", "health_informatics"),
    ("Infrastructure Systems Analyst (Network)", "health_other"),  # IT, not health data
    ("Systems Analyst, Transit Technology", "health_other"),
    ("Epidemiologist", "health_informatics"),
    ("Nurse Practitioner (Bilingual) (RFT 1.0 FTE)", "health_other"),
    ("Clinical and Operations Pharmacy Manager", "health_other"),
    ("Financial Analyst (TFT 1.0 FTE)", "health_other"),
])
def test_category_is_decided_on_the_title_not_an_ehr_mention_in_the_body(title, expected):
    body = "Documents care in the electronic health record (EHR) and the EMR daily."
    assert hb._category_for(CIHI, title, body) == expected

def test_a_health_board_posting_without_data_keywords_is_health_other():
    job = hb._to_job(CIHI, title="Workplace Operations Coordinator", url="u", location="Ottawa",
                     description="Orders supplies for the office.", job_key="J1")
    assert job["category"] == "health_other"
    assert job["always_notify"] is False


@pytest.mark.parametrize("entry,expected", [
    (CIHI, {"health_informatics", "health_other"}),
    (CITY, {"health_informatics", "municipal"}),
])
def test_possible_categories_mirror_category_for(entry, expected):
    assert hb._possible_categories(entry) == expected


def test_fetch_all_scopes_boards_and_survives_one_failing(monkeypatch):
    monkeypatch.setattr(hb, "load_known_boards", lambda: {"boards": [CIHI, CITY, ROYAL]})
    calls = []

    def ok(entry, skip_ids, session):
        calls.append(entry["company_name"])
        return [hb._to_job(entry, title="Health data analyst", url="u", location="Ottawa",
                           description="", job_key=entry["company_name"])]

    def boom(entry, skip_ids, session):
        calls.append(entry["company_name"])
        raise RuntimeError("bot check")

    monkeypatch.setattr(hb, "FETCHERS", {"njoyn": boom, "successfactors": ok, "jobvite": ok})

    jobs = hb.HealthBoardsSource().fetch_all(skip_ids=set())
    assert calls == ["CIHI", "City of Ottawa", "The Royal"]
    assert [j["company"] for j in jobs] == ["City of Ottawa", "The Royal"]

    calls.clear()
    hb.HealthBoardsSource().fetch_all(skip_ids=set(), categories={"municipal"})
    assert calls == ["City of Ottawa"]

    calls.clear()
    hb.HealthBoardsSource().fetch_all(skip_ids=set(), categories={"goodlife"})
    assert calls == []
