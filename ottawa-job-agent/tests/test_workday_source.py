"""Workday CXS payloads → pipeline jobs, for both seeded tenants.

GoodLife and CHEO are two rows in known_workday.json parsed by one code path,
so the same fixtures are run through both entries: any divergence in category,
notify behaviour, or apply URL has to come from the registry data, never from a
branch in the parser.
"""

import json

import pytest

import workday_source as ws

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


def posting(title, path="/job/Ottawa/Role_JR1", req="JR113503", locations="Ottawa Queen and Bank"):
    return {
        "title": title,
        "externalPath": path,
        "locationsText": locations,
        "postedOn": "Posted 3 Days Ago",
        "bulletFields": [req],
    }


def detail(description, external_url="https://goodlifefitness.wd3.myworkdayjobs.com/en-US/Careers/job/Role_JR1",
           req="JR113503"):
    return {"jobPostingInfo": {
        "jobDescription": "<p>{}</p>".format(description),
        "externalUrl": external_url,
        "jobReqId": req,
    }}


# --- the shape the pipeline expects ---

def test_workday_posting_becomes_a_pipeline_job():
    job = ws._workday_to_job(GOODLIFE_ENTRY,
                             posting("Personal Trainer - Ottawa Queen and Bank"),
                             detail("Deliver training sessions."))

    assert job["title"] == "Personal Trainer - Ottawa Queen and Bank"
    assert job["company"] == "GoodLife Fitness"
    assert job["location"] == "Ottawa Queen and Bank"
    assert job["source"] == "GoodLife Fitness (Workday)"
    assert job["ats"] == "workday"
    assert job["apply_target"] == "employer_site"
    assert job["apply_email"] is None
    assert job["description"] == "Deliver training sessions."


def test_apply_url_is_the_form_not_the_description_page():
    job = ws._workday_to_job(GOODLIFE_ENTRY, posting("Club Attendant"),
                             detail("Front desk."))
    assert job["url"].endswith("/apply")


def test_html_is_stripped_from_the_description():
    job = ws._workday_to_job(
        CHEO_ENTRY, posting("Data Analyst", locations="Ottawa, ON"),
        detail("<b>Support</b> the&nbsp;EMR team", external_url="https://cheo.wd10.myworkdayjobs.com/en-US/External_Site/job/Data_JR9"),
    )
    assert "<b>" not in job["description"]
    assert "Support the EMR team" in job["description"]


def test_posting_without_an_external_url_is_skipped():
    """No externalUrl means no real apply link. Guessing one from the search
    path would put a dead link in the digest under an "Apply here" button."""
    assert ws._workday_to_job(GOODLIFE_ENTRY, posting("Motivator"),
                              {"jobPostingInfo": {"jobDescription": "x"}}) is None


def test_posting_without_a_title_or_path_is_skipped():
    assert ws._workday_to_job(GOODLIFE_ENTRY, {"externalPath": "/job/x"}, detail("x")) is None
    assert ws._workday_to_job(GOODLIFE_ENTRY, {"title": "Role"}, detail("x")) is None


def test_a_missing_detail_fetch_is_skipped_not_half_built():
    assert ws._workday_to_job(GOODLIFE_ENTRY, posting("Motivator"), None) is None


# --- the location filter ---

def test_an_out_of_town_club_is_dropped():
    """searchText="Ottawa" is a full-text match, so GoodLife's Hamilton club on
    Upper Ottawa St comes back from an Ottawa search. GoodLife jobs are
    always_notify, so nothing downstream would filter it — it has to die here."""
    assert ws._workday_to_job(
        GOODLIFE_ENTRY,
        posting("Personal Trainer - Hamilton Stone Church and Upper Ottawa",
                locations="Hamilton, Ontario"),
        detail("Training."),
    ) is None


@pytest.mark.parametrize("location", ["Ottawa, Ontario", "Gloucester, Ontario",
                                      "Ottawa Queen and Bank"])
def test_ottawa_area_locations_survive_the_filter(location):
    job = ws._workday_to_job(GOODLIFE_ENTRY, posting("Club Attendant", locations=location),
                             detail("Front desk."))
    assert job is not None


def test_an_internal_location_label_is_not_treated_as_another_city():
    """CHEO tags some postings with a building name ("Research 2") instead of a
    city. Every CHEO posting is in Ottawa, so an unrecognised label must pass."""
    job = ws._workday_to_job(
        CHEO_ENTRY, posting("Director of Operations", locations="Research 2"),
        detail("Run the clinical research unit.",
               external_url="https://cheo.wd10.myworkdayjobs.com/en-US/External_Site/job/DO_JR7549"),
    )
    assert job is not None
    assert job["location"] == "Research 2"


# --- the target club ---

def test_queen_and_bank_is_flagged_as_the_target_club():
    job = ws._workday_to_job(GOODLIFE_ENTRY,
                             posting("Personal Trainer - Ottawa Queen and Bank"),
                             detail("Training."))
    assert job["target_club"] is True
    assert job["always_notify"] is True


def test_another_ottawa_club_is_not_the_target_club():
    job = ws._workday_to_job(GOODLIFE_ENTRY,
                             posting("Personal Trainer - Ottawa Barrhaven",
                                     locations="Ottawa Barrhaven"),
                             detail("Training."))
    assert "target_club" not in job
    assert job["always_notify"] is True   # every GoodLife role still notifies


def test_target_club_matching_is_case_insensitive():
    job = ws._workday_to_job(GOODLIFE_ENTRY,
                             posting("Group Fitness Trainee - OTTAWA QUEEN AND BANK"),
                             detail("Classes."))
    assert job["target_club"] is True


# --- categories: the health-informatics track has to earn its boost ---

def test_goodlife_roles_stay_in_the_goodlife_category():
    job = ws._workday_to_job(GOODLIFE_ENTRY, posting("Fitness Advisor"), detail("Sales."))
    assert job["category"] == "goodlife"


def test_cheo_health_informatics_role_gets_the_priority_category():
    job = ws._workday_to_job(
        CHEO_ENTRY, posting("Clinical Informatics Specialist", locations="Ottawa, ON"),
        detail("Support the EHR rollout.",
               external_url="https://cheo.wd10.myworkdayjobs.com/en-US/External_Site/job/CI_JR9"),
    )
    assert job["category"] == "health_informatics"
    assert job["always_notify"] is True


def test_cheo_non_informatics_role_does_not_get_the_priority_category():
    """A CHEO recreation-therapy posting is a health job, not a health-data job
    — it must not inherit the +2 that the priority track earns."""
    job = ws._workday_to_job(
        CHEO_ENTRY, posting("Recreation Therapist", locations="Ottawa, ON"),
        detail("Run therapeutic recreation programs for inpatients.",
               external_url="https://cheo.wd10.myworkdayjobs.com/en-US/External_Site/job/RT_JR9"),
    )
    assert job["category"] == "health_other"
    assert job["always_notify"] is False


@pytest.mark.parametrize("text", [
    "Health Information Management", "clinical informatics", "EMR analyst",
    "electronic health record", "health data analyst", "coding and abstracting",
    "digital health", "Requires CHIM or HIM credential",
])
def test_health_informatics_keywords_match(text):
    assert ws.is_health_informatics_text(text)


@pytest.mark.parametrize("text", [
    "Personal trainer — help him reach his goals",   # the pronoun, not the credential
    "Recreation therapist for inpatient programs",
    "",
])
def test_non_health_data_text_does_not_match(text):
    assert not ws.is_health_informatics_text(text)


# --- ids ---

def test_id_is_stable_for_the_same_posting():
    args = ("Personal Trainer", "GoodLife Fitness", "JR113503")
    assert ws.make_id(*args) == ws.make_id(*args)


def test_different_postings_get_different_ids():
    a = ws.make_id("Personal Trainer", "GoodLife Fitness", "JR113503")
    b = ws.make_id("Club Attendant", "GoodLife Fitness", "JR113504")
    assert a != b


def test_the_same_role_at_two_tenants_does_not_collide():
    """Both tenants run through one parser, so ids must separate on company —
    otherwise a CHEO analyst would dedup away a GoodLife one."""
    gl = ws._workday_to_job(GOODLIFE_ENTRY, posting("Data Analyst", req="JR1"),
                            detail("x"))
    cheo = ws._workday_to_job(
        CHEO_ENTRY, posting("Data Analyst", req="JR1", locations="Ottawa, ON"),
        detail("x", external_url="https://cheo.wd10.myworkdayjobs.com/en-US/External_Site/job/DA_JR1",
               req="JR1"),
    )
    assert gl["id"] != cheo["id"]


# --- scoping a run to categories ---
#
# `python3 job_agent.py --category goodlife` is the standard recovery command, and
# the first live one returned zero Workday jobs because the source wasn't wired in
# at all. Which category a posting lands in isn't known until its description has
# been fetched, so a scoped run has to filter on what a tenant *could* produce.

def test_goodlife_tenant_can_only_produce_goodlife():
    assert ws._possible_categories(GOODLIFE_ENTRY) == {"goodlife"}


def test_a_health_tenant_can_produce_either_health_category():
    assert ws._possible_categories(CHEO_ENTRY) == {"health_informatics", "health_other"}


def test_a_discovered_tenant_can_still_reach_the_priority_track():
    """A tenant added by URL discovery has no curated category, but its postings
    are still text-matched — so it must not be scoped out of a health run."""
    assert ws._possible_categories({"category": "workday_direct"}) == {
        "health_informatics", "workday_direct"}


@pytest.mark.parametrize("entry,categories,expected", [
    (GOODLIFE_ENTRY, {"goodlife"}, True),
    (GOODLIFE_ENTRY, {"health_informatics"}, False),
    (CHEO_ENTRY, {"health_informatics"}, True),
    (CHEO_ENTRY, {"goodlife"}, False),
    (GOODLIFE_ENTRY, None, True),   # an unscoped run polls everything
    (CHEO_ENTRY, None, True),
])
def test_scoped_runs_poll_only_the_tenants_that_can_match(entry, categories, expected):
    polled = not (categories and not (ws._possible_categories(entry) & categories))
    assert polled is expected


def test_a_scoped_fetch_skips_the_other_tenant_without_a_request(monkeypatch):
    """The skip has to happen before the network call — polling CHEO and then
    discarding its jobs would spend one detail request per posting for nothing."""
    polled = []
    monkeypatch.setattr(ws, "load_known_workday",
                        lambda: {"tenants": [dict(GOODLIFE_ENTRY), dict(CHEO_ENTRY)]})

    def fake_fetch(tenant, wd_host, site, search_text):
        polled.append(tenant)
        return []

    monkeypatch.setattr(ws, "_fetch_workday_jobs", fake_fetch)
    ws.WorkdaySource().fetch_all(categories={"goodlife"})

    assert polled == ["goodlifefitness"]


# --- tenant registry ---

def test_discovering_a_new_tenant_never_enables_auto_apply(tmp_path, monkeypatch):
    """Auto-apply is scoped to GoodLife until the wizard is proven on one real
    submission. A tenant found in a URL must not be able to opt itself in."""
    registry = tmp_path / "known_workday.json"
    registry.write_text(json.dumps({"tenants": [dict(GOODLIFE_ENTRY)]}))
    monkeypatch.setattr(ws, "KNOWN_WORKDAY_FILE", registry)

    added = ws.discover_workday_tenants_from_jobs(
        [{"url": "https://bruyere.wd3.myworkdayjobs.com/en-US/Careers/job/Analyst"}])

    assert added == 1
    tenants = json.loads(registry.read_text())["tenants"]
    new = [t for t in tenants if t["tenant"] == "bruyere"][0]
    assert new["auto_apply"] is False


def test_an_already_known_tenant_is_not_added_twice(tmp_path, monkeypatch):
    registry = tmp_path / "known_workday.json"
    registry.write_text(json.dumps({"tenants": [dict(GOODLIFE_ENTRY)]}))
    monkeypatch.setattr(ws, "KNOWN_WORKDAY_FILE", registry)

    added = ws.discover_workday_tenants_from_jobs(
        [{"url": "https://goodlifefitness.wd3.myworkdayjobs.com/en-US/Careers/job/Trainer"}])

    assert added == 0


def test_a_non_workday_url_is_ignored(tmp_path, monkeypatch):
    registry = tmp_path / "known_workday.json"
    registry.write_text(json.dumps({"tenants": []}))
    monkeypatch.setattr(ws, "KNOWN_WORKDAY_FILE", registry)

    assert ws.discover_workday_tenants_from_jobs(
        [{"url": "https://boards.greenhouse.io/cityofottawa/jobs/1"}]) == 0


def test_registry_falls_back_to_both_seeded_tenants(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "KNOWN_WORKDAY_FILE", tmp_path / "missing.json")
    tenants = ws.load_known_workday()["tenants"]
    by_name = {t["tenant"]: t for t in tenants}

    assert by_name["goodlifefitness"]["auto_apply"] is True
    assert by_name["cheo"]["auto_apply"] is False


def test_a_corrupt_registry_falls_back_instead_of_crashing_the_run(tmp_path, monkeypatch):
    registry = tmp_path / "known_workday.json"
    registry.write_text("{ not json")
    monkeypatch.setattr(ws, "KNOWN_WORKDAY_FILE", registry)

    assert len(ws.load_known_workday()["tenants"]) == len(ws.DEFAULT_TENANTS)


def test_shipped_registry_matches_the_approved_auto_apply_scope():
    """Guards the live file, not a fixture: GoodLife is the only tenant approved
    for credential-based auto-apply."""
    tenants = json.loads(ws.KNOWN_WORKDAY_FILE.read_text())["tenants"]
    enabled = [t["tenant"] for t in tenants if t.get("auto_apply")]
    assert enabled == ["goodlifefitness"]
