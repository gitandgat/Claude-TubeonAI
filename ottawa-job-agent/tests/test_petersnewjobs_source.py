"""Tests for the Peter's New Jobs digest parser.

The fixture reproduces the structure of a real send as described: one table row
per job with four cells, bold section headers, Mailchimp redirect links in the
HTML and real destinations in the plain-text part. It is NOT a copy of a real
message -- until the parser runs against an actual .eml, these tests prove the
logic is self-consistent, not that it matches Peter's markup.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from petersnewjobs_source import (  # noqa: E402
    _clean_url,
    _is_ottawa_or_remote,
    parse_digest,
    parse_html_rows,
    parse_text_urls,
)


def _row(index, title, employer, location, href):
    return (
        "<tr><td>%s</td>"
        '<td><a href="%s">%s</a></td>'
        "<td>%s</td><td>%s</td></tr>" % (index, href, title, employer, location)
    )


MC = "https://crosswalk.us17.list-manage.com/track/click?u=abc&id=%s&e=f00d"

HTML = """
<table><tr><td colspan="2">Peter's New Jobs</td></tr></table>
<p><strong>Private</strong></p>
<table>
  <tr><td>#</td><td>Position</td><td>Employer</td><td>Location</td></tr>
""" + _row(1, "Data Analyst", "Calian Group", "Ottawa, ON", MC % "l1") \
     + _row(2, "Warehouse Lead", "Giant Tiger", "Toronto, ON", MC % "l2") \
     + """
</table>
<p><strong>Healthcare</strong></p>
<table>
""" + _row(1, "Clinical Informatics Specialist", "CHEO", "Ottawa, ON", MC % "l3") \
     + _row(2, "Bilingual Care Coordinator", "Ottawa CCAC", "Ottawa, ON", MC % "l4") \
     + _row(3, "Bilingual Care Coordinator", "Champlain LHIN", "Ottawa, ON", MC % "l5") \
     + _row(4, "Registered Nurse", "KGH", "Kingston, ON", MC % "l6") \
     + _row(5, "Candidates Interested in Vice Principal Roles", "OCDSB", "Ottawa, ON", MC % "l7") \
     + """
</table>
<p><strong>Agencies</strong></p>
<table>
""" + _row(1, "Health Data Specialist", "Altis Recruitment", "Remote", MC % "l8") \
     + """
</table>
<p>A success story: <a href="%s">read it here</a></p>
""" % (MC % "story")

TEXT = """
Peter's New Jobs

Private

1. Data Analyst - Calian Group - Ottawa, ON
https://calian.com/careers/data-analyst?mc_cid=9f1&mc_eid=UNIQID
2. Warehouse Lead - Giant Tiger - Toronto, ON
https://gianttiger.com/jobs/warehouse-lead?mc_cid=9f1&mc_eid=UNIQID

Healthcare

1. Clinical Informatics Specialist - CHEO - Ottawa, ON
https://cheo.ca/careers/clinical-informatics?mc_cid=9f1&mc_eid=UNIQID
2. Bilingual Care Coordinator - Ottawa CCAC - Ottawa, ON
https://healthcareathome.ca/jobs/care-coordinator?mc_cid=9f1&mc_eid=UNIQID
3. Bilingual Care Coordinator - Champlain LHIN - Ottawa, ON
https://healthcareathome.ca/jobs/care-coordinator?mc_cid=9f1&mc_eid=UNIQID
4. Registered Nurse - KGH - Kingston, ON
https://kgh.on.ca/jobs/rn?mc_cid=9f1&mc_eid=UNIQID
5. Candidates Interested in Vice Principal Roles - OCDSB - Ottawa, ON
https://ocdsb.ca/talent/vice-principal?mc_cid=9f1&mc_eid=UNIQID

Agencies

1. Health Data Specialist - Altis Recruitment - Remote
https://altis.com/jobs/health-data?mc_cid=9f1&mc_eid=UNIQID

Read the success story:
https://crosswalk.us17.list-manage.com/track/click?u=abc&id=story&e=f00d
"""


# --- URL cleaning ---------------------------------------------------------

def test_clean_url_strips_campaign_and_recipient_tracking():
    cleaned = _clean_url(
        "https://cheo.ca/careers/x?mc_cid=9f1&mc_eid=UNIQID&utm_source=mc&id=42")
    assert cleaned == "https://cheo.ca/careers/x?id=42"


def test_clean_url_is_stable_across_sends():
    monday = _clean_url("https://cheo.ca/jobs/1?mc_cid=aaa&mc_eid=111")
    tuesday = _clean_url("https://cheo.ca/jobs/1?mc_cid=bbb&mc_eid=222")
    assert monday == tuesday


# --- Ottawa filter --------------------------------------------------------

def test_ottawa_filter_rejects_the_out_of_area_cities_peter_actually_sends():
    # The permissive job_sources reject-list lets all three of these through;
    # this strict test is why the new source needs its own.
    assert not _is_ottawa_or_remote("Kingston, ON")
    assert not _is_ottawa_or_remote("Renfrew, ON")
    assert not _is_ottawa_or_remote("Montebello, QC")


def test_ottawa_filter_keeps_area_towns_and_remote():
    for location in ("Ottawa, ON", "Kanata", "Gatineau, QC", "Remote",
                     "Télétravail"):
        assert _is_ottawa_or_remote(location), location


def test_ottawa_filter_rejects_a_blank_location():
    assert not _is_ottawa_or_remote("")


# --- HTML extraction ------------------------------------------------------

def test_html_rows_skip_the_header_row_and_layout_tables():
    rows = parse_html_rows(HTML)
    titles = [r["title"] for r in rows]
    assert "Position" not in titles          # header row has no link
    assert "Peter's New Jobs" not in titles  # 2-cell layout table
    assert len(rows) == 8


def test_html_rows_carry_the_section_they_appear_under():
    rows = parse_html_rows(HTML)
    assert rows[0]["section"] == "Private"
    assert rows[2]["section"] == "Healthcare"
    assert rows[-1]["section"] == "Agencies"


def test_html_rows_split_the_four_cells_correctly():
    first = parse_html_rows(HTML)[0]
    assert first["title"] == "Data Analyst"
    assert first["employer"] == "Calian Group"
    assert first["location"] == "Ottawa, ON"
    assert "list-manage.com" in first["href"]


# --- plain-text extraction ------------------------------------------------

def test_text_urls_are_grouped_by_section_and_exclude_redirects():
    urls = parse_text_urls(TEXT)
    assert len(urls["Private"]) == 2
    assert len(urls["Healthcare"]) == 5
    assert len(urls["Agencies"]) == 1
    # The success-story link is a Mailchimp redirect, so it is not a job URL.
    assert all("list-manage.com" not in u
               for section in urls.values() for u in section)


# --- the join and the filters ---------------------------------------------

def test_join_pairs_each_row_with_its_own_destination():
    jobs = parse_digest(HTML, TEXT)["jobs"]
    by_title = {j["title"]: j["url"] for j in jobs}
    assert by_title["Data Analyst"].startswith("https://calian.com")
    assert by_title["Clinical Informatics Specialist"].startswith(
        "https://cheo.ca")


def test_clean_counts_report_no_mismatch():
    assert parse_digest(HTML, TEXT)["mismatched"] == []


def test_out_of_area_and_non_postings_are_dropped():
    result = parse_digest(HTML, TEXT)
    titles = [j["title"] for j in result["jobs"]]
    assert "Warehouse Lead" not in titles   # Toronto
    assert "Registered Nurse" not in titles  # Kingston
    assert not any("Candidates Interested" in t for t in titles)
    assert result["skipped"]["out_of_area"] == 2
    assert result["skipped"]["not_a_posting"] == 1


def test_the_same_posting_under_two_employer_labels_yields_one_job():
    result = parse_digest(HTML, TEXT)
    care = [j for j in result["jobs"] if j["title"] == "Bilingual Care Coordinator"]
    assert len(care) == 1
    assert result["skipped"]["duplicate"] == 1


def test_health_informatics_rows_are_flagged_for_notification():
    jobs = {j["title"]: j for j in parse_digest(HTML, TEXT)["jobs"]}
    informatics = jobs["Clinical Informatics Specialist"]
    assert informatics["category"] == "health_informatics"
    assert informatics["always_notify"] is True
    assert jobs["Data Analyst"]["always_notify"] is False


def test_job_dicts_carry_every_field_the_pipeline_reads():
    required = {"id", "title", "company", "location", "url", "source",
                "category", "apply_email", "description", "deadline",
                "posted_date", "status", "always_notify", "apply_target", "ats"}
    for job in parse_digest(HTML, TEXT)["jobs"]:
        assert required <= set(job), required - set(job)


def test_ids_are_stable_across_two_sends_of_the_same_jobs():
    first = {j["title"]: j["id"] for j in parse_digest(HTML, TEXT)["jobs"]}
    resent = TEXT.replace("mc_cid=9f1", "mc_cid=aa2").replace("UNIQID", "zz9")
    second = {j["title"]: j["id"] for j in parse_digest(HTML, resent)["jobs"]}
    assert first == second


# --- the failure modes that matter ----------------------------------------

def test_a_count_mismatch_keeps_the_redirect_rather_than_mispairing():
    # Drop one Healthcare URL: position no longer identifies a row, so every
    # row in that section must fall back instead of shifting by one.
    broken = TEXT.replace(
        "https://cheo.ca/careers/clinical-informatics?mc_cid=9f1&mc_eid=UNIQID\n", "")
    result = parse_digest(HTML, broken)
    assert result["mismatched"] == [{"section": "Healthcare", "rows": 5,
                                     "urls": 4}]
    informatics = [j for j in result["jobs"]
                   if j["title"] == "Clinical Informatics Specialist"][0]
    assert "list-manage.com" in informatics["url"]
    # Private was intact, so it still gets real destinations.
    analyst = [j for j in result["jobs"] if j["title"] == "Data Analyst"][0]
    assert analyst["url"].startswith("https://calian.com")


def test_the_weekly_events_send_yields_nothing_instead_of_garbage():
    events = """
    <p><strong>This week in Ottawa</strong></p>
    <table><tr><td>Tue</td><td><a href="https://x.test/e">Job fair</a></td>
    <td>City Hall</td><td>Ottawa, ON</td></tr></table>
    """
    result = parse_digest(events, "Job fair\nhttps://x.test/e")
    assert result["jobs"] == []
    assert result["skipped"] == {"not_a_jobs_digest": 1}


def test_html_only_still_produces_jobs_on_redirect_urls():
    result = parse_digest(HTML, "")
    assert len(result["jobs"]) >= 3
    assert all("list-manage.com" in j["url"] for j in result["jobs"])
