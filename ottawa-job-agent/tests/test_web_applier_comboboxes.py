"""Greenhouse renders every dropdown as a react-select combobox, so the <select>
and radio passes answered nothing on those forms and every submit died at
validation. These tests cover the two honesty rules of the combobox pass: only an
option the site itself rendered may be chosen, and a location must match the city
*and* the region so no American Ottawa can end up on his application.

They also cover the captcha classifier, which used to call an invisible reCAPTCHA
badge a human gate and told him a blocked form was one click from done.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import web_applier


class FakeOption:
    def __init__(self, text):
        self.text = text
        self.clicked = False

    def click(self, timeout=None):
        self.clicked = True


class FakeBox:
    """Minimal stand-in for a Playwright locator over a react-select input."""

    def __init__(self, attrs=None):
        self.attrs = attrs or {}

    def get_attribute(self, name):
        return self.attrs.get(name)


def options(*labels):
    return [(label, FakeOption(label)) for label in labels]


# --- choosing an option -----------------------------------------------------

def test_exact_match_wins_over_a_prefix_match():
    opts = options("No, I do not", "No")
    assert web_applier._matching_option(opts, "No", False) is opts[1][1]


def test_prefix_match_is_accepted_when_there_is_no_exact_one():
    opts = options("Yes, I am legally authorized to work in Canada")
    assert web_applier._matching_option(opts, "Yes", False) is opts[0][1]


def test_no_match_selects_nothing():
    """A required question left blank stops the submit. Inventing an option the
    employer never offered would put a false answer in their ATS permanently."""
    opts = options("Prefer not to disclose", "Decline to answer")
    assert web_applier._matching_option(opts, "Yes", False) is None


def test_empty_option_list_selects_nothing():
    assert web_applier._matching_option([], "Yes", False) is None


# --- locations, where a near-match is a wrong answer ------------------------

def test_location_requires_the_country_not_just_the_city():
    opts = options("Ottawa, IL, United States", "Ottawa, KS, United States")
    assert web_applier._matching_option(opts, "Ottawa, ON", True) is None


def test_location_picks_the_canadian_ottawa():
    opts = options("Ottawa, IL, United States", "Ottawa, ON, Canada")
    assert web_applier._matching_option(opts, "Ottawa, ON", True) is opts[1][1]


def test_location_accepts_the_province_spelled_out():
    opts = options("Ottawa, Ontario")
    assert web_applier._matching_option(opts, "Ottawa, ON", True) is opts[0][1]


# --- deciding what to answer ------------------------------------------------

def test_country_field_answers_canada():
    assert web_applier._combobox_answer(FakeBox({"id": "country"}), "Country") == "Canada"


def test_location_field_answers_his_real_city():
    answer = web_applier._combobox_answer(FakeBox({"id": "candidate-location"}), "Location")
    assert answer == "Ottawa, ON"


def test_work_authorization_question_answers_yes():
    box = FakeBox({"id": "question_8998746005"})
    label = "Are you legally authorized to work in Canada?"
    assert web_applier._combobox_answer(box, label) == "Yes"


def test_sponsorship_question_answers_no():
    box = FakeBox({"id": "question_8998747005"})
    label = "Will you now or in the future require sponsorship?"
    assert web_applier._combobox_answer(box, label) == "No"


def test_unrecognised_question_is_left_blank():
    """Desired salary and anecdote questions belong to him, not to the agent."""
    box = FakeBox({"id": "question_1"})
    assert web_applier._combobox_answer(box, "What is your desired salary?") == ""


def test_missing_id_does_not_crash():
    assert web_applier._combobox_answer(FakeBox(), "Country") == "Canada"


def test_canadian_eligibility_phrasing_answers_yes():
    """Live Ottawa postings ask "eligible to work for any employer in Canada",
    which matched no pattern — so the one question we can honestly answer on a
    real Greenhouse form was left blank and the submit died at validation."""
    box = FakeBox({"id": "question_8998746005"})
    label = "Are you eligible to work for any employer in Canada?"
    assert web_applier._combobox_answer(box, label) == "Yes"


def test_us_eligibility_phrasing_is_caught_by_the_us_guard():
    """The same phrasing scoped to the US has the opposite honest answer."""
    label = "Are you eligible to work for any employer in the United States?"
    assert web_applier.US_CONTEXT.search(label)


# --- scoping options to the right menu --------------------------------------

def test_listbox_selector_follows_aria_controls():
    """A real form keeps 244 phone dial-code options in the DOM at all times, so
    an unscoped option search matched that list for every single dropdown."""
    box = FakeBox({"aria-controls": "react-select-question_1-listbox"})
    assert web_applier._listbox_selector(box) == (
        "[id='react-select-question_1-listbox'] [role='option']")


def test_listbox_selector_falls_back_to_the_field_id():
    box = FakeBox({"id": "question_1"})
    assert web_applier._listbox_selector(box) == (
        "[id^='react-select-question_1-option']")


def test_listbox_selector_scopes_to_nothing_when_it_cannot_tell():
    """Better to read no options than to read another widget's."""
    assert web_applier._listbox_selector(FakeBox()) == ""


# --- what to type to make the real options appear ---------------------------

def test_location_searches_the_city_alone():
    """Their lookup is server-side and returns nothing for "Ottawa, ON"."""
    assert web_applier._combobox_searches("Ottawa, ON", True) == ("Ottawa",)


def test_other_fields_try_the_open_menu_before_typing():
    assert web_applier._combobox_searches("Yes", False) == ("", "Yes")


# --- captcha classification -------------------------------------------------

class FakeFrame:
    def __init__(self, src="", height=60):
        self.src = src
        self.height = height

    def get_attribute(self, name):
        return self.src if name == "src" else None

    def bounding_box(self):
        return {"x": 0, "y": 0, "width": 256, "height": self.height}


class FakeLocator:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self.items


class FakePage:
    """Returns containers for the div selectors and iframes for the iframe one."""

    def __init__(self, frames=None, containers=None):
        self.frames = frames or []
        self.containers = containers or []

    def locator(self, selector):
        if "iframe" in selector:
            return FakeLocator(self.frames)
        return FakeLocator(self.containers)


def test_invisible_recaptcha_badge_is_not_a_human_gate():
    """Greenhouse puts this badge on every posting. Calling it a captcha hid the
    real blocker on 14 records."""
    page = FakePage(frames=[FakeFrame(
        "https://www.recaptcha.net/recaptcha/enterprise/anchor?size=invisible&k=x")])
    assert not web_applier._has_interactive_captcha(page)


def test_a_real_challenge_frame_is_still_a_human_gate():
    page = FakePage(frames=[FakeFrame(
        "https://newassets.hcaptcha.com/captcha/v1/challenge", height=400)])
    assert web_applier._has_interactive_captcha(page)


def test_an_unmarked_badge_sized_frame_is_not_a_gate():
    page = FakePage(frames=[FakeFrame("https://recaptcha.net/anchor", height=60)])
    assert not web_applier._has_interactive_captcha(page)


def test_a_page_with_no_captcha_at_all():
    assert not web_applier._has_interactive_captcha(FakePage())
