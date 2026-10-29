"""Workday's "Select One" fields broke the GoodLife wizard three separate ways,
all of them silent. These tests pin the fixes.

1. Workday leaves a closed listbox in the DOM, so reading `ul[role='listbox']`
   globally returned the *previous* field's options — live, Country was offered
   the "how did you hear" list, Province or Territory got 250 country names, and
   Phone Device Type got the 13 provinces. Nothing could match, so no dropdown
   was ever filled and the run stalled with no error.
2. The aria-label carries the field's current value, not a fixed placeholder, so
   an already-correct field ("Phone Device Type Mobile Required") came back with
   the value baked into its question text, matched no rule, and was reported as
   needing his input — a false blocker one step into a five-step wizard.
3. match_option's containment fallback could return a real but wrong option for
   a short answer, which is the one failure mode that would put a false answer
   in an employer's ATS under his name.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import application_prefill
import form_schema


class FakeButton:
    """Stand-in for a Playwright locator over a Workday combobox button.

    Mirrors the real widget: aria-controls is published only once the button is
    expanded, and it names that button's own listbox.
    """

    def __init__(self, aria_label="", shown="Select One", listbox_id=None,
                 expands=True):
        self.aria_label = aria_label
        self.shown = shown
        self.listbox_id = listbox_id
        self.expands = expands
        self.expanded = False

    def click(self, timeout=None):
        self.expanded = self.expands

    def text_content(self, timeout=None):
        return self.shown

    def get_attribute(self, name, timeout=None):
        if name == "aria-label":
            return self.aria_label
        if name == "aria-expanded":
            return "true" if self.expanded else "false"
        if name == "aria-controls":
            return self.listbox_id if self.expanded else None
        return None


class FakeLocator:
    def __init__(self, page, selector):
        self.page = page
        self.selector = selector

    @property
    def first(self):
        return self

    def wait_for(self, state=None, timeout=None):
        return None

    def locator(self, selector):
        return FakeLocator(self.page, "{} {}".format(self.selector, selector))


class FakePage:
    """Resolves `[id='x']` against a dict of listbox id -> option labels, and
    records every id that was asked for."""

    def __init__(self, listboxes):
        self.listboxes = listboxes
        self.requested = []

    def locator(self, selector):
        self.requested.append(selector)
        return FakeLocator(self, selector)

    def wait_for_timeout(self, ms):
        return None

    def keyboard_press(self, key):
        return None

    @property
    def keyboard(self):
        return self

    def press(self, key):
        return None


# --- 1. options come from the button's own listbox ---------------------------

def test_listbox_is_resolved_through_the_buttons_own_aria_controls():
    page = FakePage({"ysgw2": ["Alberta", "Ontario"]})
    button = FakeButton(listbox_id="ysgw2")
    button.click()

    form_schema.open_combobox_listbox(page, button)

    assert page.requested == ["[id='ysgw2']"]


def test_a_button_that_never_opens_yields_no_listbox():
    """No binding means no way to tell which options belong to this field. A
    blank question he answers himself beats a wrong one submitted for him."""
    page = FakePage({})
    button = FakeButton(listbox_id="ysgw2", expands=False)
    button.click()

    assert form_schema.open_combobox_listbox(page, button) is None


def test_each_button_resolves_to_its_own_listbox_not_the_first_in_the_dom():
    """The live failure: four buttons, four listboxes, options shifted by one."""
    page = FakePage({"ysgw3": ["Email"], "ysgw0": ["Canada"], "ysgw2": ["Ontario"]})
    for listbox_id in ("ysgw3", "ysgw0", "ysgw2"):
        button = FakeButton(listbox_id=listbox_id)
        button.click()
        form_schema.open_combobox_listbox(page, button)

    assert page.requested == ["[id='ysgw3']", "[id='ysgw0']", "[id='ysgw2']"]


# --- 2. the label is the question, never the current value -------------------

def test_placeholder_label_loses_its_boilerplate():
    label, required = form_schema._combobox_label_from_aria(
        "How Did You Hear About Us? Select One Required", "Select One")
    assert (label, required) == ("How Did You Hear About Us?", True)


def test_a_filled_field_does_not_bake_its_value_into_the_question():
    label, required = form_schema._combobox_label_from_aria(
        "Phone Device Type Mobile Required", "Mobile")
    assert (label, required) == ("Phone Device Type", True)


def test_a_multi_word_value_is_stripped_too():
    label, _ = form_schema._combobox_label_from_aria(
        "Country Phone Code Canada (+1) Required", "Canada (+1)")
    assert label == "Country Phone Code"


def test_an_optional_combobox_is_not_marked_required():
    label, required = form_schema._combobox_label_from_aria(
        "Preferred Contact Method Select One", "Select One")
    assert (label, required) == ("Preferred Contact Method", False)


def test_a_value_already_on_the_form_answers_the_question():
    """Workday pre-fills from his own candidate profile, so "Mobile" is his
    data. Treating it as unanswered stopped the run on a correct field."""
    field = {"label": "Phone Device Type", "kind": "workday_select",
             "required": True, "options": ["Landline", "Mobile"], "value": "Mobile"}
    answer = application_prefill.answer_field(field, {"company": "GoodLife"})

    assert answer["needs_input"] is False
    assert answer["answer"] == "Mobile"
    assert answer["source"] == "already_on_form"


def test_an_empty_combobox_with_no_rule_still_needs_his_input():
    field = {"label": "T-shirt size", "kind": "workday_select",
             "required": True, "options": ["S", "M", "L"], "value": ""}
    assert application_prefill.answer_field(field, {"company": "GoodLife"})["needs_input"]


# --- 3. option matching stays honest ----------------------------------------

def test_province_abbreviation_expands_to_the_real_option():
    provinces = ["Alberta", "Nova Scotia", "Ontario", "Quebec"]
    assert application_prefill.match_option("ON", provinces) == "Ontario"


def test_a_short_answer_cannot_land_on_an_unrelated_option():
    """"ON" used to select "None of the above" purely because the letters were
    in there — a real option, the wrong answer, permanent in their ATS."""
    assert application_prefill.match_option("ON", ["None of the above"]) is None


def test_option_matching_does_not_depend_on_option_order():
    both = ["Select One", "Ontario"]
    assert application_prefill.match_option("ON", both) == "Ontario"
    assert application_prefill.match_option("ON", list(reversed(both))) == "Ontario"


def test_a_substantial_containment_match_still_works():
    assert application_prefill.match_option("Canada", ["Canada (+1)"]) == "Canada (+1)"


def test_no_match_still_returns_nothing():
    assert application_prefill.match_option("Yes", ["Prefer not to say"]) is None
