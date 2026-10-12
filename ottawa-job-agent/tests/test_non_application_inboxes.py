"""Regression tests for the esc-cse@ottawa.ca incident (2026-09-07): an
accommodation contact printed on a City of Ottawa posting was used as the
application inbox, and the duplicate-recipient guard then held back every later
City of Ottawa job. See non_application_inboxes.py."""

import web_applier
from non_application_inboxes import first_application_email, is_non_application_inbox

CITY_OF_OTTAWA_FOOTER = (
    "Police Record Check: The successful candidate will be required to complete a "
    "Vulnerable Sector Check (Level 3). The City of Ottawa provides accommodation to "
    "applicants during all parts of the hiring process, upon request. Please contact the "
    "Employee Service Centre at 613-580-2424 extension 12211 or via email at "
    "esc-cse@ottawa.ca"
)


def test_city_of_ottawa_accommodation_contact_is_rejected():
    assert is_non_application_inbox("esc-cse@ottawa.ca", CITY_OF_OTTAWA_FOOTER)
    assert first_application_email(CITY_OF_OTTAWA_FOOTER) is None


def test_known_inbox_rejected_without_any_text():
    assert is_non_application_inbox("ESC-CSE@ottawa.ca")
    assert is_non_application_inbox(" esc-cse@ottawa.ca. ")


def test_real_apply_address_kept_next_to_an_accommodation_contact():
    text = (
        "Please send your resume and cover letter to careers@acme.ca by Friday. "
        "We provide accommodation on request; contact hr-access@acme.ca."
    )
    assert not is_non_application_inbox("careers@acme.ca", text)
    assert is_non_application_inbox("hr-access@acme.ca", text)
    assert first_application_email(text) == "careers@acme.ca"


def test_first_application_email_looks_past_a_leading_accommodation_contact():
    text = (
        "Accommodation is available on request: accessibility@acme.ca. "
        "To apply, email your CV to jobs@acme.ca."
    )
    assert first_application_email(text) == "jobs@acme.ca"


def test_sentence_asking_for_a_resume_wins_over_accommodation_wording():
    text = "Applicants requiring accommodation can still send their resume to hiring@acme.ca."
    assert not is_non_application_inbox("hiring@acme.ca", text)


def test_address_not_in_text_is_judged_by_known_list_only():
    assert not is_non_application_inbox("talent@acme.ca", CITY_OF_OTTAWA_FOOTER)
    assert not is_non_application_inbox("", CITY_OF_OTTAWA_FOOTER)


def test_web_applier_picker_never_returns_the_accommodation_inbox():
    assert web_applier._pick_apply_email(["esc-cse@ottawa.ca"], "jobs-emplois.ottawa.ca") == ""
    assert (
        web_applier._pick_apply_email(["esc-cse@ottawa.ca", "careers@ottawa.ca"], "jobs-emplois.ottawa.ca")
        == "careers@ottawa.ca"
    )


class _FakePage:
    url = "https://jobs-emplois.ottawa.ca/city-jobs/job/Ottawa-ON-Personal-Fitness-Trainer/1291381847/"

    def __init__(self, body, mailtos=()):
        self._body, self._mailtos = body, list(mailtos)

    def eval_on_selector_all(self, selector, script):
        return self._mailtos

    def locator(self, selector):
        page = self

        class _Loc:
            def inner_text(self, timeout=None):
                return page._body

        return _Loc()


def test_harvest_skips_accommodation_contact_on_city_posting():
    page = _FakePage(CITY_OF_OTTAWA_FOOTER, mailtos=["mailto:esc-cse@ottawa.ca"])
    assert web_applier._harvest_apply_email(page) == ""


def test_harvest_still_finds_a_real_apply_inbox():
    body = "Send your resume to recruitment@ottawa.ca. " + CITY_OF_OTTAWA_FOOTER
    assert web_applier._harvest_apply_email(_FakePage(body)) == "recruitment@ottawa.ca"
