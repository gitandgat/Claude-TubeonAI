"""The GoodLife wizard reached Application Questions, left six required fields
blank, tripped Workday's own "Errors Found" panel, and still reported 15 fields
answered and zero blockers. Three separate silences produced that, and these
tests pin all three.

1. A combobox whose aria-label is only boilerplate ("Select One Required")
   yields an empty label, and _combobox_field_from_button then returned None —
   the required question vanished from the schema with no error. Whatever the
   aria-label says, the question text is still on the page next to the widget,
   and a control that cannot be identified at all must become a blocker rather
   than disappear.
2. _advance() returned True on a successful *click*, not on a successful step
   *change*, so a validation wall read as forward progress and the loop spun on
   one step until MAX_WIZARD_STEPS ran out.
3. When the wizard stopped moving, the run reported the generic "stopped before
   reaching a Submit step" while Workday was displaying the exact list of what
   was wrong. Those messages are evidence and belong in the outcome.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import form_schema
import workday_applier


# --- fakes ------------------------------------------------------------------

class FakeElement:
    """A Workday combobox button, plus the container text a real page would
    render around it."""

    def __init__(self, aria_label="", shown="Select One", container_text="",
                 labelledby=None, labelledby_text=None, el_id=None,
                 legend_text="", tag="BUTTON", required=None):
        self.aria_label = aria_label
        self.shown = shown
        self.container_text = container_text
        # Workday's real Application Questions put the question here and leave
        # the wrapping divs holding only the placeholder. Defaulting it empty
        # keeps the older tests below exercising the container fallback.
        self.legend_text = legend_text
        self.tag = tag
        self.required = required
        self.labelledby = labelledby
        self.labelledby_text = labelledby_text
        self.el_id = el_id
        self.expanded = False

    def evaluate(self, script):
        return self.tag

    def click(self, timeout=None):
        self.expanded = False  # never opens, so no options are invented

    def text_content(self, timeout=None):
        return self.shown

    def inner_text(self, timeout=None):
        return self.container_text

    def count(self):
        return 1

    def get_attribute(self, name, timeout=None):
        return {
            "aria-label": self.aria_label,
            "aria-labelledby": self.labelledby,
            "aria-expanded": "true" if self.expanded else "false",
            "aria-controls": None,
            "id": self.el_id,
            "name": None,
            "required": self.required,
        }.get(name)

    def locator(self, selector):
        # The xpath ancestor lookups used to recover the question text. The
        # fieldset's <legend> and the nearest wrapping container are different
        # places holding different text, so the fake must tell them apart —
        # answering both with the container is what let a helper that flattened
        # the legend's line breaks pass while corrupting the real question.
        if "legend" in selector:
            return _Found(self.legend_text)
        return _Found(self.container_text) if "ancestor" in selector else _Found("")


class _Found:
    def __init__(self, text):
        self.text = text

    @property
    def first(self):
        return self

    def count(self):
        return 1 if self.text else 0

    def inner_text(self, timeout=None):
        return self.text

    def is_enabled(self, timeout=None):
        return True


class FakeFrame:
    def __init__(self, by_id=None):
        self.by_id = by_id or {}

    def locator(self, selector):
        for key, text in self.by_id.items():
            if "'{}'".format(key) in selector:
                return _Found(text)
        return _Found("")

    def wait_for_timeout(self, ms):
        return None

    @property
    def keyboard(self):
        return self

    def press(self, key):
        return None


class FakeWizardPage:
    """Enough page for _advance(): a clickable next control and a set of form
    controls that changes only when the wizard actually moves on."""

    def __init__(self, controls, controls_after=None, errors=(),
                 active_step="", active_step_after=None, forward_enabled=True,
                 error_panel=()):
        self.controls = list(controls)
        # Workday's "Errors Found" panel, which carries no automation id and no
        # role=alert — only its text. _step_errors reaches it through a second
        # page.evaluate, so the fake has to tell the two scripts apart; a fake
        # that answered every evaluate with the control list handed _step_errors
        # every widget on the step as a validation message.
        self.error_panel = list(error_panel)
        self.controls_after = (list(controls_after)
                               if controls_after is not None else list(controls))
        self.errors = list(errors)
        self.clicks = 0
        # "" means a tenant with no progress bar, which is what the older tests
        # below describe — they pin the control-comparison fallback.
        self.active_step = active_step
        self.active_step_after = (active_step_after
                                  if active_step_after is not None else active_step)
        self.forward_enabled = forward_enabled

    # _click / _click_either
    def locator(self, selector):
        if "progressBarActiveStep" in selector:
            return _Found(self.active_step if not self.clicks
                          else self.active_step_after)
        return _NextButton(self)

    def get_by_role(self, role, name=None):
        return _NextButton(self)

    def evaluate(self, script):
        if "Error" in script:
            return list(self.error_panel)
        return list(self.controls)

    def wait_for_timeout(self, ms):
        return None


class _NextButton:
    def __init__(self, page):
        self.page = page

    @property
    def first(self):
        return self

    def count(self):
        return 1

    def is_visible(self, timeout=None):
        return True

    def is_enabled(self, timeout=None):
        # Workday disables Save and Continue while the next step loads; a fake
        # that never does is a page whose steps are always finished painting.
        return getattr(self.page, "forward_enabled", True)

    def click(self, timeout=None):
        self.page.clicks += 1
        self.page.controls = list(self.page.controls_after)

    def inner_text(self, timeout=None):
        return "Save and Continue"

    def all(self):
        return [_Found(e) for e in self.page.errors]


# --- 1. a required question must never vanish -------------------------------

def test_boilerplate_only_aria_label_yields_no_label():
    """The trigger condition, stated plainly: Workday's Application Questions
    put the question in the markup, not in the aria-label, so the aria path
    strips itself down to nothing."""
    label, required = form_schema._combobox_label_from_aria("Select One Required", "")
    assert label == ""
    assert required is True


def test_the_question_text_is_recovered_from_the_widgets_container():
    el = FakeElement(
        aria_label="Select One Required",
        container_text="Are you legally entitled to work in Canada?*\nSelect One",
    )
    field = form_schema._combobox_field_from_button(
        FakeFrame(), el, frame=FakeFrame())
    assert field is not None
    assert field["label"] == "Are you legally entitled to work in Canada?*"
    assert field["required"] is True


def test_the_question_text_is_recovered_from_aria_labelledby():
    el = FakeElement(aria_label="Select One", labelledby="q7")
    frame = FakeFrame({"q7": "How long can you commit to this availability?*"})
    field = form_schema._combobox_field_from_button(frame, el, frame=frame)
    assert field is not None
    assert field["label"] == "How long can you commit to this availability?*"


def test_an_unidentifiable_dropdown_blocks_instead_of_disappearing():
    """This is the safety bias. A control we cannot name might be optional, and
    flagging it stops a run that could have finished — but the alternative is
    what actually happened: six required questions left blank while the run
    reported no blockers at all.

    The widget here points at a label element that renders nothing, so it is
    announcing itself as a labelled form control while giving us no name — the
    one shape that is unmistakably a question and still unreadable. (A widget
    with no aria-label *and* no aria-labelledby is page chrome; see below.)"""
    el = FakeElement(aria_label="", container_text="", labelledby="q_missing")
    field = form_schema._combobox_field_from_button(
        FakeFrame(), el, frame=FakeFrame())
    assert field is not None
    assert field["required"] is True
    assert field["kind"] == "workday_select"
    assert field["label"]  # something a human can act on, never empty


# --- 2. advancing means moving, not clicking --------------------------------

def test_advance_is_false_when_the_step_did_not_change():
    """The validation wall: Save and Continue is clicked, Workday refuses, the
    same step re-renders. Reporting that as progress is what let the loop spin
    to MAX_WIZARD_STEPS and then blame a missing Submit step."""
    page = FakeWizardPage(controls=["q1", "q2", "q3"])
    assert workday_applier._advance(page) is False
    assert page.clicks == 1


def test_advance_is_true_when_the_next_step_renders():
    page = FakeWizardPage(controls=["name", "email"],
                          controls_after=["workAuth", "availability"])
    assert workday_applier._advance(page) is True


def test_advance_is_false_when_there_is_no_forward_control():
    class NoButton(FakeWizardPage):
        def locator(self, selector):
            return _Found("")

        def get_by_role(self, role, name=None):
            return _Found("")

    assert workday_applier._advance(NoButton(controls=["a"])) is False


# --- 3. Workday's own error text is the reason ------------------------------

def test_validation_messages_are_read_off_the_page():
    page = FakeWizardPage(
        controls=["q1"],
        errors=["Error: Select One is required",
                "Please list the days and hours you are available to work."],
    )
    found = workday_applier._step_errors(page)
    assert "Error: Select One is required" in found
    assert len(found) == 2


def test_no_error_panel_reads_as_no_errors():
    assert workday_applier._step_errors(FakeWizardPage(controls=["q1"])) == []


# --- 4. "are you currently one of our employees?" is a fact, not a guess -----

import application_prefill

_YES_NO = ["Yes", "No"]
_GOODLIFE = {"title": "Personal Trainer", "company": "GoodLife Fitness"}


def _select(label, options=None):
    return {"label": label, "kind": "workday_select", "required": True,
            "options": options if options is not None else _YES_NO,
            "name": "q", "value": ""}


def test_current_associate_at_the_hiring_company_answers_no():
    """GoodLife's own wording, verbatim off the form. He is applying from
    outside, so "are you on our payroll right now" has one honest answer."""
    answer = application_prefill.answer_field(_select(
        "Are you a current Associate (paid employee) at any of the following "
        "brands/organizations: GoodLife Fitness, Fit4Less, GYMVMT, GoodLife "
        "Kids Foundation or canfitpro?*"), _GOODLIFE)
    assert answer["needs_input"] is False
    assert answer["answer"] == "No"


def test_currently_employed_by_this_company_answers_no():
    answer = application_prefill.answer_field(
        _select("Are you currently employed by this organization?"), _GOODLIFE)
    assert answer["needs_input"] is False
    assert answer["answer"] == "No"


def test_a_current_employment_question_about_someone_else_is_not_answered():
    """The guard that keeps the No where it belongs. "Are you currently
    employed?" on its own is about his job situation, not about theirs."""
    answer = application_prefill.answer_field(
        _select("Are you currently employed?"), _GOODLIFE)
    assert answer["needs_input"] is True


def test_a_past_employer_asking_about_current_status_is_flagged_not_guessed():
    """Sault Area Hospital is on his real history. Whether that employment is
    current is his to say — inferring No from a past-employer list would be a
    guess about his present."""
    answer = application_prefill.answer_field(
        _select("Are you a current employee of Sault Area Hospital?"),
        {"title": "Analyst", "company": "Sault Area Hospital"})
    assert answer["needs_input"] is True


# --- 5. page chrome is not a form field -------------------------------------

def test_the_settings_menu_button_is_not_treated_as_a_question():
    """Workday's own Settings menu is a button[aria-haspopup='listbox'] sitting
    in the page chrome on every step. Live output caught it being reported as an
    unidentified required dropdown — a blocker on every step of every wizard.
    It has no aria-label, no aria-labelledby, and no question text around it;
    that combination is what distinguishes chrome from a labelled-badly field."""
    el = FakeElement(aria_label=None, shown="Settings", container_text="Settings")
    assert form_schema._combobox_field_from_button(
        FakeFrame(), el, frame=FakeFrame()) is None


def test_a_form_widget_whose_label_is_only_boilerplate_still_blocks():
    """The other side of the same line. This one *does* carry an aria-label —
    Workday just put nothing useful in it — so it is a real question and must
    not be dropped."""
    el = FakeElement(aria_label="Select One Required", shown="Select One",
                     container_text="Select One")
    field = form_schema._combobox_field_from_button(
        FakeFrame(), el, frame=FakeFrame())
    assert field is not None
    assert field["required"] is True


# --- 6. the phone rule was answering two fields it had no business in --------

def _text(label, required=False, value=""):
    return {"label": label, "kind": "text", "required": required,
            "options": [], "name": "q", "value": value}


def test_phone_extension_is_left_blank_not_filled_with_the_phone_number():
    """Live output caught this one: "Phone Extension" matched the generic
    phone|mobile|telephone rule and was answered '416-616-9589'. That is a false
    value — he has no extension — and unlike a missed question it would have
    been submitted and sat in the employer's ATS under his name."""
    answer = application_prefill.answer_field(_text("Phone Extension"), _GOODLIFE)
    assert answer["answer"] == ""
    assert answer["needs_input"] is False


def test_a_required_extension_field_is_flagged_rather_than_blanked():
    """Blank is the honest answer only while blank is allowed. If a form insists
    on an extension, that is something he has to resolve, not us."""
    answer = application_prefill.answer_field(
        _text("Phone Extension", required=True), _GOODLIFE)
    assert answer["needs_input"] is True


def test_country_phone_code_answers_the_dial_code_not_the_country():
    """Same live run: "Country Phone Code*" was answered 'Canada' by the
    \\bcountry\\b rule. The field wants +1."""
    answer = application_prefill.answer_field(
        _text("Country Phone Code*", required=True), _GOODLIFE)
    assert answer["answer"] == "+1"


def test_country_phone_code_picks_the_matching_option_when_there_is_a_list():
    field = _text("Country Phone Code*", required=True)
    field["kind"] = "workday_select"
    field["options"] = ["Australia (+61)", "Canada (+1)", "United States (+1)"]
    answer = application_prefill.answer_field(field, _GOODLIFE)
    assert answer["answer"] == "Canada (+1)"


def test_the_plain_country_field_still_answers_canada():
    """The guard must not swallow the ordinary Country question."""
    answer = application_prefill.answer_field(
        _text("Country", required=True), _GOODLIFE)
    assert answer["answer"] == "Canada"


def test_the_plain_phone_field_still_answers_his_number():
    answer = application_prefill.answer_field(
        _text("Phone Number*", required=True), _GOODLIFE)
    assert answer["answer"] == application_prefill.PROFILE["phone"]


# --- 7. the forward control, and waiting for the step to finish painting -----

class FakeTenantPage:
    """A wizard whose forward control carries only the automation id this
    tenant really uses, and whose step needs `paints` polls before its controls
    appear — both measured off the live GoodLife run."""

    def __init__(self, forward_aid, controls, controls_after=None, paints=0):
        self.forward_aid = forward_aid
        self.controls = list(controls)
        self.controls_after = (list(controls_after)
                               if controls_after is not None else list(controls))
        self.paints = paints
        self.clicks = 0
        self.polls = 0

    def locator(self, selector):
        return _NextButton(self) if self.forward_aid in selector else _Found("")

    def get_by_role(self, role, name=None):
        return _Found("")          # no text fallback: the id must carry it

    def evaluate(self, script):
        self.polls += 1
        if self.clicks and self.polls <= self.paints:
            return []              # still painting
        return list(self.controls)

    def wait_for_timeout(self, ms):
        return None


def test_the_forward_control_is_found_by_this_tenants_automation_id():
    """[data-automation-id='bottom-navigation-next-button'] does not exist on
    goodlifefitness.wd3. Its Save and Continue button is pageFooterNextButton,
    which is why every step reported "next button never became visible" and
    burned NAV_TIMEOUT_MS waiting for something that was never coming."""
    page = FakeTenantPage("pageFooterNextButton",
                          controls=["name", "email"],
                          controls_after=["workAuth"])
    assert workday_applier._advance(page) is True
    assert page.clicks == 1


def test_the_previous_tenants_automation_id_still_works():
    """Other Workday tenants do use it; this is an addition, not a swap."""
    page = FakeTenantPage("bottom-navigation-next-button",
                          controls=["name"], controls_after=["workAuth"])
    assert workday_applier._advance(page) is True


def test_a_step_that_is_still_painting_is_not_read_as_a_stalled_wizard():
    """The live run dumped My Experience holding one input and no forward
    control, then reported the wizard stopped. The step wasn't broken — this
    SPA takes 4-12 seconds to paint its content area and it was read at 2.5.
    Advancing has to wait for the step to settle, not for a fixed sleep."""
    page = FakeTenantPage("pageFooterNextButton",
                          controls=["name"], controls_after=["resumeUpload"],
                          paints=3)
    assert workday_applier._advance(page) is True


def test_a_step_that_never_changes_is_still_a_stall():
    """The settle must not turn the validation wall into false progress."""
    page = FakeTenantPage("pageFooterNextButton", controls=["q1", "q2"])
    assert workday_applier._advance(page) is False


# --- 8. the progress bar, because the control list lied -----------------------
#
# Sep 12 2026, live on goodlifefitness.wd3: the walk clicked Save and Continue on
# My Experience, Workday moved to Application Questions — progress bar read
# "completed step 2 of 5 ... current step 3 of 5" and the screenshot showed it —
# and _advance reported the step as stuck. It compared form controls, and Workday
# leaves the step you just left in the document with its boxes collapsed, so both
# readings were the same two entries. The walk stopped one step short of the
# questions it existed to read.

_STEP2 = "current step 2 of 5 My Experience"
_STEP3 = "current step 3 of 5 Application Questions"


def test_a_step_that_moved_is_not_called_stuck_just_because_its_controls_linger():
    page = FakeWizardPage(
        controls=["settingsSelectorButton", "file-upload-input-ref"],
        controls_after=["settingsSelectorButton", "file-upload-input-ref"],
        active_step=_STEP2, active_step_after=_STEP3)
    assert workday_applier._advance(page) is True


def test_a_step_that_failed_validation_is_still_called_stuck():
    """The other direction, and the one that matters more: a re-rendered step
    keeps its place in the progress bar, so a rejected Save and Continue reads as
    no movement even though the controls changed underneath it."""
    page = FakeWizardPage(controls=["q1"], controls_after=["q1", "errorMessage"],
                          active_step=_STEP2, active_step_after=_STEP2)
    assert workday_applier._advance(page) is False


def test_a_tenant_with_no_progress_bar_still_falls_back_to_its_controls():
    """Every earlier test in this file describes that tenant. Keeping the
    fallback means the progress bar is an improvement, not a new dependency."""
    page = FakeWizardPage(controls=["name"], controls_after=["workAuth"])
    assert page.active_step == ""
    assert workday_applier._advance(page) is True


def test_the_active_step_is_read_off_workdays_own_markup():
    assert workday_applier._active_step(
        FakeWizardPage(controls=["q1"], active_step=_STEP3)) == _STEP3
    assert workday_applier._active_step(FakeWizardPage(controls=["q1"])) == ""


# --- 9. a spinner is not a settled step --------------------------------------

def test_a_loading_step_is_not_mistaken_for_a_finished_one():
    """Workday disables the forward control while a step fetches itself. Without
    that check _settle saw the leftover controls agree with themselves twice and
    returned after 2s onto a page that was still a spinner."""
    page = FakeWizardPage(controls=["settingsSelectorButton"], forward_enabled=False)
    workday_applier.STEP_RENDER_TIMEOUT_MS, saved = 30, workday_applier.STEP_RENDER_TIMEOUT_MS
    workday_applier.STEP_POLL_MS, saved_poll = 10, workday_applier.STEP_POLL_MS
    try:
        assert workday_applier._settle(page) == ["settingsSelectorButton"]
    finally:
        workday_applier.STEP_RENDER_TIMEOUT_MS = saved
        workday_applier.STEP_POLL_MS = saved_poll


# --- 10. Workday announces successes through the error channel ----------------

def test_an_upload_success_toast_is_not_reported_as_a_validation_error():
    """Live: role=alert carried "resume_....pdf successfully uploaded" and
    nothing else, so a stopped run would have emailed him that as the reason."""
    page = FakeWizardPage(
        controls=["q1"],
        errors=["resume_goodlife_4a00afa03112b5.pdf successfully uploaded"])
    assert workday_applier._step_errors(page) == []


def test_a_real_validation_error_alongside_a_success_toast_survives():
    page = FakeWizardPage(
        controls=["q1"],
        errors=["resume.pdf successfully uploaded", "Error: Select One is required"])
    assert workday_applier._step_errors(page) == ["Error: Select One is required"]


# --- 11. the question lives in the fieldset's legend ------------------------
# Measured on goodlifefitness.wd3 Sep 12: every question on Application
# Questions — five dropdowns and three textareas — keeps its text in
# ancestor::fieldset[1]/legend[1], three styling divs above the widget.

def test_the_question_is_read_off_the_fieldsets_legend():
    el = FakeElement(
        aria_label=" Select One Required",
        legend_text="Have you ever been trusted with confidential information"
                    " in previous work experiences?*",
        container_text="Select One",
    )
    field = form_schema._combobox_field_from_button(
        FakeFrame(), el, frame=FakeFrame())
    assert field is not None
    assert field["label"] == ("Have you ever been trusted with confidential"
                              " information in previous work experiences?*")
    assert field["required"] is True


def test_a_legend_that_wraps_the_widget_does_not_keep_the_placeholder():
    # A tenant whose <legend> encloses the widget rather than preceding it
    # yields the placeholder on its own line. It is boilerplate, not question.
    el = FakeElement(
        aria_label=" Select One Required",
        legend_text="Are you legally entitled to work in Canada?*\nSelect One",
        container_text="Select One",
    )
    field = form_schema._combobox_field_from_button(
        FakeFrame(), el, frame=FakeFrame())
    assert field["label"] == "Are you legally entitled to work in Canada?*"


def test_the_settings_menu_is_still_not_mistaken_for_a_question():
    # Workday's own chrome sits in every step as the same kind of button, with
    # no aria-label, no aria-labelledby and no fieldset around it.
    el = FakeElement(aria_label="", shown="Settings", container_text="Settings")
    assert form_schema._combobox_field_from_button(
        FakeFrame(), el, frame=FakeFrame()) is None


def test_a_textarea_with_no_label_anywhere_else_is_named_by_its_legend():
    # The bug this closes: an empty <textarea> leaves its wrapping divs with no
    # text at all, so the generic label walk returns "" and the field was
    # dropped outright — silently, never reaching blocked_by. On the live
    # GoodLife step that discarded the required availability question.
    el = FakeElement(
        tag="TEXTAREA",
        required="",
        legend_text="Please list the days and hours you are available to work.*",
        container_text="",
    )
    field = form_schema._dom_field_from_element(FakeFrame(), el)
    assert field is not None
    assert field["kind"] == "textarea"
    assert field["label"] == ("Please list the days and hours you are"
                             " available to work.*")
    assert field["required"] is True


# --- 12. the step that answered everything and still would not move ----------
# Walk of Sep 13 reached Application Questions, reported "8 fields, 0
# unanswered-required", clicked Save and Continue, and did not move. Three
# things were wrong at once and each hid the next.


class FakeOption:
    def __init__(self, text):
        self.text = text
        self.clicked = False

    def text_content(self, timeout=None):
        return self.text

    def click(self, timeout=None):
        self.clicked = True


class FakeListbox:
    def __init__(self, options):
        self.options = [FakeOption(o) for o in options]

    def wait_for(self, state=None, timeout=None):
        return None

    def locator(self, selector):
        return self

    def all(self):
        return self.options


class FakeCombobox:
    """A Workday dropdown that only opens on the Nth click.

    `opens_on_click` is the whole point: live, the "trusted with confidential
    information" button swallowed its first click without throwing and without
    setting aria-expanded, so the listbox never appeared and the 2s poll in
    open_combobox_listbox simply expired.
    """

    def __init__(self, listbox_id="lb1", opens_on_click=1):
        self.listbox_id = listbox_id
        self.opens_on_click = opens_on_click
        self.clicks = 0
        self.expanded = False

    def click(self, timeout=None):
        self.clicks += 1
        if self.opens_on_click and self.clicks >= self.opens_on_click:
            self.expanded = True

    def get_attribute(self, name, timeout=None):
        if name == "aria-expanded":
            # Unset before the first click, exactly as measured — the failing
            # field was not an already-open widget being toggled shut.
            return "true" if self.expanded else None
        if name == "aria-controls":
            return self.listbox_id if self.expanded else None
        return None


class FakeComboboxPage:
    def __init__(self, button, options):
        self.button = button
        self.listbox = FakeListbox(options)
        self.escapes = 0

    def locator(self, selector):
        if selector.startswith("[id="):
            return _Listboxed(self.listbox)
        return _Listboxed(self.button)

    def wait_for_timeout(self, ms):
        return None

    @property
    def keyboard(self):
        return self

    def press(self, key):
        if key == "Escape":
            self.escapes += 1


class _Listboxed:
    def __init__(self, target):
        self.target = target

    @property
    def first(self):
        return self.target


def _combobox(opens_on_click, options=("Yes", "No")):
    button = FakeCombobox(opens_on_click=opens_on_click)
    return button, FakeComboboxPage(button, list(options))


def test_a_dropdown_that_opens_first_time_is_not_clicked_twice():
    """The retry must not become a second click on every field: clicking an
    open combobox again is what closes it."""
    button, page = _combobox(opens_on_click=1)
    assert workday_applier._select_combobox_option(page, "q1", "Yes") is True
    assert button.clicks == 1
    assert page.escapes == 0


def test_a_dropped_opening_click_is_retried_and_the_answer_still_lands():
    """Live: the same field failed on its first click two runs running while
    the three other dropdowns on the step opened first time, and an immediate
    second click set the value in 0.07s. Without this the step reported a
    question he had already answered as one needing his input."""
    button, page = _combobox(opens_on_click=2)
    assert workday_applier._select_combobox_option(page, "q1", "Yes") is True
    assert button.clicks == 2
    # Escaped once between the attempts, so the retry starts from a closed
    # widget rather than clicking a half-open one shut.
    assert page.escapes == 1


def test_a_dropdown_that_never_opens_still_fails_rather_than_guessing():
    button, page = _combobox(opens_on_click=0)
    assert workday_applier._select_combobox_option(page, "q1", "Yes") is False
    assert button.clicks == 2


def test_the_retry_does_not_invent_an_option_that_is_not_offered():
    """The gate that matters: a dropdown opening on the retry is still only
    allowed to click an option the field actually lists."""
    button, page = _combobox(opens_on_click=2, options=("Yes", "No"))
    assert workday_applier._select_combobox_option(page, "q1", "Maybe") is False
    assert not any(o.clicked for o in page.listbox.options)


def test_workdays_errors_found_panel_is_read_even_with_no_automation_id():
    """Measured on goodlifefitness.wd3: the refusal drew four <button> elements
    reading "Error - <question>" and inline "Error: The field ... is required"
    text, none of which carry an automation id or role=alert. _step_errors
    returned [] while the page was naming, one by one, every question that had
    stopped the wizard — and the run emailed him the generic "stopped before
    reaching a Submit step" instead."""
    page = FakeWizardPage(
        controls=["q1"],
        error_panel=[
            "Error - Are you legally entitled to work in Canada?",
            "Error - Please indicate on scale of 1-10, how would you rate your "
            "commitment to upholding that confidentiality",
            "Error: The field How long can you commit to this availability? is "
            "required and must have a value.",
        ],
    )
    found = workday_applier._step_errors(page)
    assert len(found) == 3
    assert any("scale of 1-10" in m for m in found)
    assert any("legally entitled" in m for m in found)


def test_the_text_sweep_does_not_turn_a_success_toast_into_a_reason():
    """The same filter the role=alert sweep needs: Workday announces uploads
    through anything it likes."""
    page = FakeWizardPage(
        controls=["q1"],
        error_panel=["resume_goodlife.pdf successfully uploaded"])
    assert workday_applier._step_errors(page) == []


def test_the_text_sweep_does_not_report_the_same_message_twice():
    page = FakeWizardPage(
        controls=["q1"],
        errors=["Error - Are you legally entitled to work in Canada?"],
        error_panel=["Error - Are you legally entitled to work in Canada?"])
    assert workday_applier._step_errors(page) == [
        "Error - Are you legally entitled to work in Canada?"]


# --- 13. the last thing standing is his signature, not a missing answer -------
#
# The Sep 14 supervised walk cleared steps 1-3 for the first time and stopped on
# step 4, Voluntary Disclosures, holding a single required checkbox:
#
#     "Yes I have read and understand the terms and conditions for submitting
#      an application."
#
# sitting under "I verify that all statements made in my application for
# employment are true and correct". The engine is right to refuse it — that is
# his attestation and no rule should ever tick it. But the run then reported
# "1 required question(s) need your real answer", which reads as though an
# answer is missing. Nothing is missing: every question is answered and the
# application is waiting on a signature. Telling him the wrong thing here costs
# him a trip through the wizard hunting for a question that isn't there.
#
# The narrowness that matters: a checkbox is a signature control. A required
# *question* carrying consent-ish words is still a question, and must keep the
# old wording.


def _blocker(label, kind="checkbox", required=True):
    return {"label": label, "kind": kind, "required": required,
            "answer": "", "source": "needs_input", "needs_input": True,
            "hint": "No safe answer on file — fill this one in yourself."}


_TERMS = ("Yes I have read and understand the terms and conditions for "
          "submitting an application.*")


def test_the_goodlife_terms_checkbox_is_recognised_as_a_signature():
    assert workday_applier._only_needs_signature([_blocker(_TERMS)])


def test_a_real_unanswered_question_is_not_a_signature():
    """The question that actually stalled step 3 for weeks. If this ever counts
    as a signature, the run would tell him to 'just tick a box' while a genuine
    question sits blank."""
    assert not workday_applier._only_needs_signature([
        _blocker("Please indicate on scale of 1-10, how would you rate your "
                 "commitment to upholding that confidentiality",
                 kind="text")])


def test_a_signature_plus_a_real_question_is_not_just_a_signature():
    assert not workday_applier._only_needs_signature([
        _blocker(_TERMS),
        _blocker("What are your wage expectations?", kind="textarea")])


def test_consent_wording_on_a_non_checkbox_is_still_a_question():
    """Workday tenants do ask 'Do you agree to a background check?' as a
    dropdown. That is a fact about him, not a signature."""
    assert not workday_applier._only_needs_signature([
        _blocker("Do you agree to a criminal background check?",
                 kind="workday_select")])


def test_an_unrelated_checkbox_is_not_a_signature():
    assert not workday_applier._only_needs_signature([
        _blocker("I have a preferred name")])


def test_nothing_blocked_is_not_a_signature_hold():
    """Guards the branch order: an empty blocker list must not read as 'ready
    for signature' and must never reach the signature reason."""
    assert not workday_applier._only_needs_signature([])


def test_the_signature_reason_tells_him_the_form_is_finished():
    reason = workday_applier._signature_reason([_blocker(_TERMS)])
    low = reason.lower()
    assert "every answer" in low or "everything" in low
    # The thing he has to do, named.
    assert "tick" in low or "check" in low
    assert "submit" in low
    # The old wording claimed an answer was missing. It must not come back.
    assert "need your real answer" not in low
