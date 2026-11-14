"""A fully packaged application still failed, because the answers only ever
reached the email. The browser filled name/email/phone/resume and the handful of
Yes/No questions whose wording is hardcoded in BOOLEAN_ANSWERS, then clicked
submit and let the board reject the form over a required question nobody had
typed into. The run came back "submit_unconfirmed", which reads like a system
fault rather than the truth.

These tests cover the two halves of the fix: the answer engine's answers get
typed into the posting's own questions, and a required question with no honest
answer stops the submit instead of wasting a click on a form that cannot pass.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import web_applier


class FakeInput:
    """Stand-in for a Playwright locator over one text input or <select>."""

    def __init__(self, tag="input", present=True):
        self.tag = tag
        self.present = present
        self.value = None
        self.selected_label = None

    # -- locator protocol ------------------------------------------------
    @property
    def first(self):
        return self

    def count(self):
        return 1 if self.present else 0

    def is_visible(self, timeout=None):
        return self.present

    def is_editable(self, timeout=None):
        return self.present

    def evaluate(self, _script):
        return self.tag.upper()

    def fill(self, value, timeout=None):
        self.value = value

    def select_option(self, label=None, timeout=None):
        self.selected_label = label


class FakeFrame:
    def __init__(self, fields):
        """fields maps a form name to the FakeInput that answers for it."""
        self.fields = fields
        self.requested = []

    def locator(self, selector):
        self.requested.append(selector)
        for name, field in self.fields.items():
            if '"{0}"'.format(name) in selector:
                return field
        return FakeInput(present=False)


def _answer(label, name, value, **kw):
    row = {
        "label": label,
        "name": name,
        "kind": "text",
        "required": True,
        "answer": value,
        "source": "profile",
        "needs_input": False,
        "hint": "",
    }
    row.update(kw)
    return row


def test_custom_question_is_typed_into_the_form():
    """The point of the whole change: a question only this posting asks, named
    question_8995444005 by Greenhouse and unrecoverable from its label, gets the
    answer the emailed package shows him."""
    salary = FakeInput()
    frame = FakeFrame({"question_8995444005": salary})

    filled = web_applier._fill_planned_answers(
        frame, [_answer("What is your desired salary?", "question_8995444005", "$70,000")]
    )

    assert filled == 1
    assert salary.value == "$70,000"


def test_native_select_is_chosen_by_label():
    """"How did you hear about us?" is a plain <select> whose wording appears in
    no BOOLEAN_ANSWERS pattern, so nothing used to answer it."""
    source = FakeInput(tag="select")
    frame = FakeFrame({"source": source})

    filled = web_applier._fill_planned_answers(
        frame,
        [_answer("How did you hear about us?", "source", "Online job posting", kind="select")],
    )

    assert filled == 1
    assert source.selected_label == "Online job posting"


def test_needs_input_answer_is_left_blank():
    """The AODA accommodation question is about his health. Leaving it empty is
    the whole point — a guess would stake a claim on his behalf."""
    aoda = FakeInput()
    frame = FakeFrame({"question_8995443005": aoda})

    filled = web_applier._fill_planned_answers(
        frame,
        [
            _answer(
                "Would you require any accommodations?",
                "question_8995443005",
                "",
                needs_input=True,
                hint="Your call.",
            )
        ],
    )

    assert filled == 0
    assert aoda.value is None


def test_answer_without_a_field_name_is_skipped():
    """Lever has no questions API, so packages built for it carry the typical
    question set with empty names. Those describe no real form and must not be
    guessed at by label."""
    frame = FakeFrame({})

    filled = web_applier._fill_planned_answers(
        frame, [_answer("Why do you want this role?", "", "Because ...")]
    )

    assert filled == 0
    assert frame.requested == []


def test_resume_upload_row_is_not_typed_as_text():
    """A file field's answer row is a description ("Upload: resume.pdf"), not
    something to type into the file input."""
    resume = FakeInput()
    frame = FakeFrame({"resume": resume})

    filled = web_applier._fill_planned_answers(
        frame, [_answer("Resume", "resume", "Upload: resume.pdf", kind="file")]
    )

    assert filled == 0
    assert resume.value is None


# -- the submit gate -----------------------------------------------------

def test_unanswered_required_question_blocks_the_submit():
    answers = [
        _answer("Eligible to work in Canada?", "question_1", "Yes"),
        _answer("What is your desired salary?", "question_2", "", needs_input=True),
    ]

    blocked = web_applier._unanswered_required(answers)

    assert blocked == ["What is your desired salary?"]


def test_optional_unanswered_question_does_not_block():
    """Plenty of boards ask optional demographic questions. Skipping those is
    normal and must not hold up an otherwise complete application."""
    answers = [
        _answer("Eligible to work in Canada?", "question_1", "Yes"),
        _answer("Gender", "question_2", "", required=False, needs_input=True),
    ]

    assert web_applier._unanswered_required(answers) == []


def test_required_file_field_does_not_block():
    """The resume is uploaded by its own step; its answer row is prose."""
    answers = [_answer("Resume", "resume", "Upload: resume.pdf", kind="file")]

    assert web_applier._unanswered_required(answers) == []


def test_gate_declines_instead_of_clicking(monkeypatch):
    """The old path clicked anyway and reported submit_unconfirmed. Nothing may
    be clicked, and the outcome must name the question that stopped it."""
    clicked = []
    monkeypatch.setattr(web_applier, "is_review_only", lambda: False)
    monkeypatch.setattr(
        web_applier, "_submit_and_verify", lambda f, p: clicked.append(True) or True
    )

    result = web_applier._maybe_submit(
        None, None, [_answer("What is your desired salary?", "question_2", "", needs_input=True)]
    )

    assert clicked == []
    assert result["submitted"] is False
    assert result["attempted_submit"] is False
    assert result["declined_submit"] is True
    assert result["needs_input_labels"] == ["What is your desired salary?"]


def test_gate_allows_submit_when_every_required_question_is_answered(monkeypatch):
    """Koboldmetals asks nothing beyond the standard fields, so it must still go
    through — the gate is a guard, not a blanket stop on auto-apply."""
    monkeypatch.setattr(web_applier, "is_review_only", lambda: False)
    monkeypatch.setattr(web_applier, "_submit_and_verify", lambda f, p: True)

    result = web_applier._maybe_submit(
        None, None, [_answer("Eligible to work in Canada?", "question_1", "Yes")]
    )

    assert result == {"submitted": True, "attempted_submit": True}


def test_review_only_marks_a_deliberate_decline(monkeypatch):
    """declined_submit is what stops the caller from mistaking a filled form for
    a page that had no form and wandering off after an Apply button."""
    monkeypatch.setattr(web_applier, "is_review_only", lambda: True)

    result = web_applier._maybe_submit(None, None, [])

    assert result["declined_submit"] is True
    assert result["attempted_submit"] is False
