"""Job Bank search parsing, the Ottawa-area filter, and apply-route classification.

The two bugs this source was rebuilt around were both silent: a search that
returned other cities, and a filter that then threw away the real Ottawa results.
Neither raised anything — the run just reported 0 jobs. So these tests assert on
what comes back, not on the absence of an exception.

Everything runs against captured HTML through a fake session; no request reaches
jobbank.gc.ca.
"""

import pytest
import requests

import jobbank_source as jb


def article(pid, title, company="Acme Corp", location="Ottawa (ON)", salary="$20.00 hourly"):
    return (
        '<article>'
        '<a href="/jobsearch/jobposting/{pid}?source=searchresults">'
        '<span class="noctitle">{title}</span></a>'
        '<ul class="list-unstyled">'
        '<li class="business">{company}</li>'
        '<li class="location">Location{location}</li>'
        '<li class="salary">Salary: {salary}</li>'
        '</ul>'
        '</article>'
    ).format(pid=pid, title=title, company=company, location=location, salary=salary)


def results_page(*articles):
    return "<html><body><section>" + "".join(articles) + "</section></body></html>"


class FakeResponse:
    def __init__(self, text, status=200):
        self.text = text
        self.status_code = status


class FakeSession:
    """Serves one canned page per request, in order, and records the params it
    was called with so the city filter can be asserted on."""

    def __init__(self, pages, raise_on=None):
        self.pages = list(pages)
        self.raise_on = raise_on          # 1-based request number that blows up
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append(params or {})
        if self.raise_on is not None and len(self.calls) == self.raise_on:
            raise requests.RequestException("connection reset")
        if not self.pages:
            return FakeResponse(results_page())
        return FakeResponse(self.pages.pop(0))


@pytest.fixture(autouse=True)
def no_politeness_delay(monkeypatch):
    """SLEEP_BETWEEN is 0.4s per page — real in production, pure waiting here."""
    monkeypatch.setattr(jb.time, "sleep", lambda *_: None)


# --- card parsing ---

def test_parse_cards_reads_every_field():
    cards = jb._parse_cards(results_page(article(
        "44001234", "Health Information Clerk", company="CHEO",
        location="Ottawa (ON)", salary="$28.00 hourly")))

    assert len(cards) == 1
    card = cards[0]
    assert card["pid"] == "44001234"
    assert card["title"] == "Health Information Clerk"
    assert card["company"] == "CHEO"
    assert card["location"] == "Ottawa (ON)"
    assert "28.00" in card["salary"]


def test_parse_cards_unescapes_and_strips_markup():
    html = results_page(article(
        "44001235", "Nurse &amp; <abbr>HIM</abbr> Assistant", company="Bruy&egrave;re"))
    card = jb._parse_cards(html)[0]

    assert "&amp;" not in card["title"]
    assert "<abbr>" not in card["title"]
    assert card["company"] == "Bruyère"


def test_parse_cards_fills_defaults_for_missing_optional_fields():
    bare = ('<article><a href="/jobsearch/jobposting/44001236">'
            '<span class="noctitle">General Labourer</span></a></article>')
    card = jb._parse_cards(results_page(bare))[0]

    assert card["company"] == "Unknown"
    assert card["location"] == "Ottawa, ON"
    assert card["salary"] == ""


def test_parse_cards_skips_articles_that_are_not_postings():
    """Job Bank wraps promo panels and alert boxes in <article> too. One without
    a posting id or a title is furniture, not a job."""
    promo = '<article><h2>Create a Job Bank account</h2></article>'
    assert jb._parse_cards(results_page(promo)) == []


def test_parse_cards_on_an_empty_page_returns_nothing():
    assert jb._parse_cards(results_page()) == []


# --- the Ottawa-area filter (bug B) ---

@pytest.mark.parametrize("location", [
    "Ottawa (ON)", "Nepean (ON)", "Kanata (ON)", "Orleans South (ON)",
    "Gloucester (ON)", "Barrhaven (ON)", "Vanier (ON)", "Gatineau (QC)",
])
def test_ottawa_area_municipalities_are_kept(location):
    """Job Bank labels postings by municipality, not by "Ottawa". Matching only
    the literal "ottawa" is what dropped every one of these."""
    assert jb._is_ottawa_or_remote(location)


def test_remote_postings_are_kept_in_both_languages():
    assert jb._is_ottawa_or_remote("Remote")
    assert jb._is_ottawa_or_remote("Télétravail")


@pytest.mark.parametrize("location", [
    "Toronto (ON)", "Kingston (ON)", "Burlington (ON)", "Vancouver (BC)",
])
def test_other_cities_are_dropped(location):
    assert not jb._is_ottawa_or_remote(location)


# --- pagination ---

def test_search_sends_the_captured_city_filter():
    """`locationparam` is the real server-side filter; without it the search
    comes back nationwide. Pin it so a refactor can't drop it back to the
    human-readable `locationstring` alone."""
    session = FakeSession([results_page(article("1", "Clerk"))])
    jb._search_ottawa_cards(session, "administrative assistant", 1)

    assert session.calls[0]["locationparam"] == jb.OTTAWA_LOCATION_PARAM
    assert session.calls[0]["searchstring"] == "administrative assistant"


def test_search_pages_until_it_has_enough_cards():
    pages = [results_page(*[article(str(i), "Clerk {}".format(i)) for i in range(3)]),
             results_page(*[article(str(i), "Clerk {}".format(i)) for i in range(3, 6)])]
    session = FakeSession(pages)

    cards = jb._search_ottawa_cards(session, "clerk", 6)

    assert len(cards) == 6
    assert [c["page"] for c in session.calls] == [1, 2]


def test_search_stops_at_the_cap_and_trims_the_overshoot():
    """The cap bounds the expensive per-posting resolve loop downstream, so a
    page that overshoots it must be trimmed, not passed through."""
    session = FakeSession([results_page(*[article(str(i), "Clerk") for i in range(10)])])

    cards = jb._search_ottawa_cards(session, "clerk", 4)

    assert len(cards) == 4
    assert len(session.calls) == 1, "no second page once the cap is met"


def test_search_stops_on_the_first_empty_page():
    """Job Bank returns zero cards past the end instead of an error, so a narrow
    query must cost one wasted request, not four."""
    session = FakeSession([results_page(article("1", "Clerk")), results_page()])

    cards = jb._search_ottawa_cards(session, "crossing guard", 30)

    assert len(cards) == 1
    assert len(session.calls) == 2


def test_search_never_exceeds_the_page_ceiling():
    full = results_page(*[article(str(i), "Clerk") for i in range(3)])
    session = FakeSession([full] * 20)

    jb._search_ottawa_cards(session, "clerk", 999)

    assert len(session.calls) == jb.MAX_SEARCH_PAGES


def test_a_network_error_keeps_the_pages_already_collected():
    """A flaky page 2 shouldn't cost the category the Ottawa jobs page 1 found."""
    session = FakeSession([results_page(article("1", "Clerk"))], raise_on=2)

    cards = jb._search_ottawa_cards(session, "clerk", 30)

    assert len(cards) == 1


def test_a_non_200_stops_the_loop_without_raising():
    class ErrorSession(FakeSession):
        def get(self, url, params=None, headers=None, timeout=None):
            self.calls.append(params or {})
            return FakeResponse("<html>503</html>", status=503)

    session = ErrorSession([])
    assert jb._search_ottawa_cards(session, "clerk", 10) == []
    assert len(session.calls) == 1


def test_out_of_town_results_are_filtered_before_the_cap_applies():
    """The filter runs per page, so a page of Toronto results must not count
    toward `want` and end the search early."""
    page1 = results_page(article("1", "Clerk", location="Toronto (ON)"),
                         article("2", "Clerk", location="Kingston (ON)"))
    page2 = results_page(article("3", "Clerk", location="Ottawa (ON)"))
    session = FakeSession([page1, page2])

    cards = jb._search_ottawa_cards(session, "clerk", 1)

    assert [c["location"] for c in cards] == ["Ottawa (ON)"]


# --- the always_notify confirmation gate ---
#
# Every case below is a real false match from the first live run after the search
# was fixed. always_notify skips MIN_SCORE, so an unconfirmed bucket label puts
# these straight into his digest — the exact "more discovery, worse completion"
# failure the rebuild was supposed to avoid.

@pytest.mark.parametrize("category,title,company,description", [
    ("thai_embassy", "personal support worker – nursing care",
     "Embassy West Senior Living", "Provide personal care to residents."),
    ("health_informatics", "pathologists' assistant",
     "A Growing bakery in Ottawa", "Assist with daily production."),
    ("health_informatics", "community animator",
     "Banque alimentaire de la Lievre", "Animate community food programs."),
    ("hospitality_hotel", "manager, hotel front office",
     "Chipotle Mexican Grill", "Lead the restaurant crew and serve guests."),
    ("goodlife", "cleaning service manager", "Clean Inc", "Manage cleaning staff."),
])
def test_an_unconfirmed_bucket_label_loses_always_notify(category, title, company, description):
    job = {"title": title, "company": company, "description": description}
    assert not jb._confirms_always_notify(category, job)


@pytest.mark.parametrize("category,title,company,description", [
    ("thai_embassy", "administrative assistant", "Royal Thai Embassy",
     "Support the consular section."),
    ("health_informatics", "Data Analyst, Information Services", "CHEO",
     "Support EMR data quality and coding and abstracting workflows."),
    ("hospitality_hotel", "manager, hotel front office", "Lord Elgin Hotel",
     "Run the front desk and guest services team."),
    ("goodlife", "fitness instructor", "Orangetheory", "Lead group fitness classes."),
])
def test_a_confirmed_posting_keeps_always_notify(category, title, company, description):
    job = {"title": title, "company": company, "description": description}
    assert jb._confirms_always_notify(category, job)


def test_a_hotel_is_judged_on_the_employer_not_the_noc_title():
    """Job Bank files postings under NOC titles, so "manager, hotel front office"
    is exactly where the false match comes from — it must not confirm itself."""
    assert not jb._confirms_always_notify("hospitality_hotel", {
        "title": "manager, hotel front office",
        "company": "Chipotle Mexican Grill",
        "description": "Fast casual restaurant service.",
    })


def test_a_score_gated_category_is_left_alone():
    """Only the four always_notify buckets are guarded; everything else already
    has to clear MIN_SCORE, so the gate must not start dropping those."""
    assert jb._confirms_always_notify("customer_service", {
        "title": "customer service agent", "company": "Working Solutions",
        "description": "Answer inbound calls.",
    })


# --- apply routing: the decision that turns into a real email ---

def test_a_mailto_reveal_routes_to_the_email_path():
    route = jb._classify_apply(
        '<p>How to apply: <a href="mailto:hr@cheo.on.ca">hr@cheo.on.ca</a></p>')
    assert route == {"mode": "email", "email": "hr@cheo.on.ca"}


def test_a_bare_email_needs_the_by_email_phrasing():
    """A stray address in the posting body isn't an instruction to write to it —
    only Job Bank's own "apply by email" wording is."""
    assert jb._classify_apply("<p>Apply by email: careers@example.org</p>")["mode"] == "email"
    assert jb._classify_apply("<p>Questions? info@example.org</p>")["mode"] == "manual"


def test_an_employer_link_routes_to_the_web_apply_path():
    route = jb._classify_apply(
        '<p>Apply online: <a href="https://careers.cheo.on.ca/job/123">here</a></p>')
    assert route["mode"] == "external"
    assert route["url"].startswith("https://careers.cheo.on.ca")


@pytest.mark.parametrize("host", ["indeed.com", "ziprecruiter.com", "linkedin.com",
                                  "www.jobbank.gc.ca"])
def test_aggregator_links_are_never_offered_as_an_apply_target(host):
    route = jb._classify_apply(
        '<a href="https://{}/viewjob?jk=abc">Apply</a>'.format(host))
    assert route["mode"] == "manual"


def test_direct_apply_is_flagged_for_his_own_sign_in():
    route = jb._classify_apply("<p>You must sign in to apply directly.</p>")
    assert route["mode"] == "manual"
    assert route["direct_apply"] is True


@pytest.mark.parametrize("phrase,fragment", [
    ("Apply in person between 9 and 5", "in person"),
    ("Send your resume by mail to the address below", "by mail"),
    ("Applications accepted by fax only", "by fax"),
])
def test_offline_apply_methods_are_reported_honestly(phrase, fragment):
    route = jb._classify_apply("<p>{}</p>".format(phrase))
    assert route["mode"] == "manual"
    assert fragment in route["reason"]


def test_an_unrecognised_reveal_falls_back_to_manual_not_to_a_guess():
    route = jb._classify_apply("<div></div>")
    assert route["mode"] == "manual"
    assert route["reason"]


# --- ids ---

def test_id_is_stable_and_distinct_per_posting():
    a = jb.make_id("Clerk", "CHEO", "https://www.jobbank.gc.ca/jobsearch/jobposting/1")
    again = jb.make_id("Clerk", "CHEO", "https://www.jobbank.gc.ca/jobsearch/jobposting/1")
    b = jb.make_id("Clerk", "CHEO", "https://www.jobbank.gc.ca/jobsearch/jobposting/2")

    assert a == again
    assert a != b
