"""The answer engine: what it fills in, and — more important — what it refuses to.

The whole point of the prefill package is that he can trust every filled row
without re-checking it. So these tests are weighted toward the refusals: a
question the engine has no honest answer to must come back flagged, never
guessed. `generated_budget=0` throughout keeps free-text questions flagging
instead of reaching Ollama, which also keeps the suite offline.
"""

import json

import re

import pytest

import application_prefill as ap

GOODLIFE = {
    "id": "gl1",
    "title": "Personal Trainer - Ottawa Queen and Bank",
    "company": "GoodLife Fitness",
    "location": "Ottawa, ON",
    "description": "Deliver personal training sessions at the Queen and Bank club.",
}

CHEO = {
    "id": "h1",
    "title": "Health Information Analyst",
    "company": "CHEO",
    "location": "Ottawa, ON",
    "description": "Support EMR data quality and coding/abstracting workflows.",
}


def field(label, kind="text", options=None, required=False):
    return {
        "label": label,
        "kind": kind,
        "required": required,
        "options": list(options or []),
        "name": label,
    }


def answer(label, job=CHEO, **kw):
    return ap.answer_field(field(label, **kw), job, generated_budget=0)


# --- address: 335 Cooper St, in every shape a form asks for it ---

@pytest.mark.parametrize("label,expected", [
    ("Street address", "335 Cooper St"),
    ("Address line 1", "335 Cooper St"),
    ("City", "Ottawa"),
    ("Province", "ON"),
    ("Full address", "335 Cooper St, Ottawa, ON K2P 0G6"),
    ("Postal code", "K2P 0G6"),
    ("Zip/Postal Code", "K2P 0G6"),
])
def test_address_fields_use_the_cooper_street_address(label, expected):
    result = answer(label)
    assert result["answer"] == expected
    assert not result["needs_input"]


def test_the_postal_code_is_coopers_own_not_the_previous_addresss():
    """K2P 2E2 was 341 MacLaren's. Cooper St is two blocks north and carries
    K2P 0G6 — the same FSA, a different code. Between the move and Sep 12 2026
    this field deliberately asked rather than guessed, because a real-looking
    wrong postcode on a submitted application is worse than a blank one:
    nobody downstream would catch it."""
    result = answer("Postal code")
    assert result["answer"] == "K2P 0G6"
    assert "K2P 2E2" not in json.dumps(result)


def test_a_blank_profile_value_never_fills_a_field_silently(monkeypatch):
    """The general rule the postal code was briefly one case of: a table entry
    whose value is empty is a question for him, not an empty string typed into
    a form and reported as ready.

    Pinned against an injected blank row rather than against whichever field
    happens to be empty today. When this was written the postal code was the
    live example; he supplied K2P 0G6 on Sep 12 2026, and a test written around
    that example would have retired the rule along with the gap."""
    monkeypatch.setattr(ap, "_PROFILE_ANSWERS",
                        [(re.compile(r"badge colour", re.I), "")] + list(ap._PROFILE_ANSWERS))
    result = answer("Badge colour", required=True)
    assert result["needs_input"] is True
    assert result["answer"] == ""


def test_no_address_field_still_carries_a_previous_address():
    filled = ap.answer_fields(ap.typical_fields(), CHEO, resume_pdf="/tmp/r.pdf")
    blob = json.dumps(filled)
    assert "Metcalfe" not in blob
    assert "MacLaren" not in blob
    assert "335 Cooper St" in blob


# --- availability: days + evenings + weekends, never overnight ---

def test_overnight_boolean_answers_no():
    result = answer("Are you available for overnight shifts?", kind="select",
                    options=["Yes", "No"])
    assert result["answer"] == "No"
    assert not result["needs_input"]


def test_overnight_free_text_says_no_and_says_why():
    result = answer("Describe your availability for night shift work", kind="textarea")
    assert result["answer"] == ap.NO_OVERNIGHT_ANSWER
    assert result["answer"].startswith("No")


def test_availability_grid_leaves_overnight_unticked():
    """A checkbox row is an instruction, not a Yes/No — it has to say which way
    to leave the box so the grid can be worked through top to bottom."""
    assert answer("Overnight", kind="checkbox")["answer"] == "Leave this one unticked"


@pytest.mark.parametrize("cell", [
    "Monday - Morning", "Tuesday - Evening", "Saturday - Afternoon", "Sunday - Morning",
])
def test_availability_grid_ticks_every_day_and_non_overnight_shift(cell):
    assert answer(cell, kind="checkbox")["answer"] == "Tick this one"


def test_free_text_availability_states_the_full_answer():
    result = answer("What is your availability for shifts?", kind="textarea")
    assert result["answer"] == ap.AVAILABILITY_ANSWER
    assert "weekend" in result["answer"].lower()
    assert "overnight" in result["answer"].lower()


# --- work authorization, and the US-context guard ---

def test_canadian_work_authorization_answers_yes():
    result = answer("Are you legally authorized to work in Canada?",
                    kind="select", options=["Yes", "No"])
    assert result["answer"] == "Yes"


def test_sponsorship_answers_no():
    result = answer("Will you now or in the future require sponsorship?",
                    kind="select", options=["Yes", "No"])
    assert result["answer"] == "No"


@pytest.mark.parametrize("label", [
    "Are you legally authorized to work in the United States?",
    "Are you authorized to work in the U.S. without sponsorship?",
])
def test_us_scoped_authorization_is_flagged_not_inherited(label):
    """His Canadian PR status answers the Canadian question and nothing else.
    Copying that Yes onto a US form would be a false statement on an
    application."""
    result = answer(label, kind="select", options=["Yes", "No"])
    assert result["needs_input"]
    assert "US" in result["hint"] or "U.S" in result["hint"]


# --- questions only he can answer ---

@pytest.mark.parametrize("label,expected_hint_fragment", [
    ("Tell us about a time you handled a difficult client", "real example"),
    ("Describe a challenge you overcame at work", "real example"),
    ("What are your salary expectations?", "number"),
    ("Desired hourly rate", "number"),
    ("Do you hold a current CPR certification?", "certification list"),
    ("Are you certified in First Aid?", "certification list"),
    # The conviction question itself moved off this list on Sep 12 2026, when he
    # answered it — see test_a_criminal_conviction_question_is_answered_no. What
    # remains flagged is the rest of the family his answer does not speak to.
    ("Are you willing to undergo a vulnerable sector check?", "own record"),
    ("Are you bondable?", "own record"),
    ("Do you have any relatives working at this company?", "Only you know"),
])
def test_needs_input_questions_are_flagged_with_a_usable_hint(label, expected_hint_fragment):
    result = answer(label, kind="select", options=["Yes", "No"])
    assert result["needs_input"], label
    assert expected_hint_fragment.lower() in result["hint"].lower()
    assert not result["answer"]


def test_anecdote_question_is_never_generated_even_with_budget():
    """The anecdote rule has to beat the Ollama path, not just the empty-budget
    path — inventing a story he never lived is the one failure mode that
    survives into a real interview."""
    result = ap.answer_field(
        field("Tell me about a time you resolved a conflict", kind="textarea"),
        CHEO, generated_budget=ap.MAX_GENERATED_ANSWERS,
    )
    assert result["needs_input"]


def test_unmatched_question_is_flagged_rather_than_guessed():
    result = answer("How many push-ups can you do in one minute?")
    assert result["needs_input"]


# --- prior employment ---

def test_previously_employed_is_yes_only_for_real_past_employers():
    result = ap.answer_field(
        field("Have you ever been employed by us?", kind="select", options=["Yes", "No"]),
        {"company": "Sault Area Hospital", "title": "Clerk", "description": ""},
        generated_budget=0,
    )
    assert result["answer"] == "Yes"


def test_previously_employed_is_no_for_a_new_employer():
    result = ap.answer_field(
        field("Have you previously been employed by GoodLife Fitness?",
              kind="select", options=["Yes", "No"]),
        GOODLIFE, generated_budget=0,
    )
    assert result["answer"] == "No"


def test_generic_industry_experience_is_not_read_as_prior_employment():
    """"Worked in a fitness environment?" must not inherit the No that belongs
    only to "worked for GoodLife?" — he has worked in fitness."""
    result = ap.answer_field(
        field("Have you ever worked in a fitness environment?",
              kind="select", options=["Yes", "No"]),
        GOODLIFE, generated_budget=0,
    )
    assert result["needs_input"]


# --- voluntary disclosures ---

@pytest.mark.parametrize("label", [
    "Gender", "Race / ethnicity", "Do you identify as a person with a disability?",
    "Are you a member of a visible minority?", "Veteran status",
])
def test_eeo_questions_decline_to_answer(label):
    result = answer(label, kind="select",
                    options=["Yes", "No", "Prefer not to answer"])
    assert result["answer"] == "Prefer not to answer"
    assert not result["needs_input"]


# --- option matching ---

def test_match_option_exact():
    assert ap.match_option("Yes", ["Yes", "No"]) == "Yes"


def test_match_option_uses_the_head_of_a_qualified_answer():
    assert ap.match_option("Yes — Canadian Permanent Resident", ["Yes", "No"]) == "Yes"


def test_match_option_returns_none_when_nothing_fits():
    """None is the signal to flag the question. Returning the raw answer here
    would paste text a <select> can't accept and silently break the form."""
    assert ap.match_option("Maybe", ["Yes", "No"]) is None


def test_match_option_passes_through_an_unconstrained_field():
    assert ap.match_option("Anything at all", []) == "Anything at all"


def test_select_with_no_matching_option_is_flagged():
    result = answer("Are you legally authorized to work in Canada?",
                    kind="select", options=["Citizen", "Study permit"])
    assert result["needs_input"]


def test_how_did_you_hear_picks_a_true_option():
    result = answer("How did you hear about us?", kind="select",
                    options=["Referral", "Company website", "Career fair"])
    assert result["answer"] == "Company website"


# --- attachments ---

def test_resume_field_names_the_actual_pdf():
    result = ap.answer_field(field("Resume / CV", kind="file", required=True),
                             CHEO, resume_pdf="/tmp/Sahawat-resume.pdf",
                             generated_budget=0)
    assert "Sahawat-resume.pdf" in result["answer"]


def test_cover_letter_field_carries_the_generated_letter():
    result = ap.answer_field(field("Cover letter", kind="textarea"), CHEO,
                             cover_letter="Dear hiring team,", generated_budget=0)
    assert result["answer"] == "Dear hiring team,"


def test_cover_letter_field_without_a_letter_is_flagged():
    result = answer("Cover letter", kind="textarea")
    assert result["needs_input"]


# --- typical-question fallback ---

def test_typical_fields_add_the_workday_extras():
    assert len(ap.typical_fields("workday")) > len(ap.typical_fields())


def test_typical_fields_are_all_answerable_offline():
    """The fallback set is what a Workday-gated job gets, so none of it may
    depend on Ollama being up — every question must resolve deterministically
    or be flagged, not silently vanish."""
    filled = ap.answer_fields(ap.typical_fields("workday"), CHEO,
                              cover_letter="CL", resume_pdf="/tmp/r.pdf")
    assert len(filled) == len(ap.typical_fields("workday"))
    assert all(a["source"] != "generated" for a in filled)


# --- the package itself ---

def test_build_prefill_writes_both_artifacts_and_counts_honestly(tmp_path, monkeypatch):
    monkeypatch.setattr(ap, "PREFILL_DIR", tmp_path)
    fields = [
        field("First name", required=True),
        field("Email", kind="email", required=True),
        field("What are your salary expectations?", required=True),
        field("Tell us about a time you led a team"),
    ]
    result = ap.build_prefill(GOODLIFE, fields, cover_letter="CL",
                              resume_pdf="/tmp/r.pdf",
                              apply_url="https://example.com/job/apply")

    assert result["n_ready"] == 2
    assert result["n_needs_input"] == 2
    # Only the salary question is required, so only it blocks a submission.
    assert result["n_required_needs_input"] == 1
    assert result["apply_url"] == "https://example.com/job/apply"
    assert not result["questions_are_typical"]

    assert (tmp_path / "gl1.html").exists()
    assert (tmp_path / "gl1.json").exists()
    assert "https://example.com/job/apply" in (tmp_path / "gl1.html").read_text()


def test_build_prefill_without_fields_falls_back_to_typical_questions(tmp_path, monkeypatch):
    monkeypatch.setattr(ap, "PREFILL_DIR", tmp_path)
    result = ap.build_prefill(GOODLIFE, None, resume_pdf="/tmp/r.pdf",
                              apply_url="https://example.com/job/apply")

    assert result["questions_are_typical"]
    assert result["n_ready"] > 0
    # The caveat has to be visible in the HTML, not just set in the JSON — he
    # must never mistake a guessed question set for the employer's real form.
    html = (tmp_path / "gl1.html").read_text()
    assert 'class="caveat"' in html
    assert "check them against the real form" in html


# --- the three answers he supplied on Sep 12 2026 -----------------------------
#
# The Queen and Bank wizard stalled on three required questions the engine had
# no honest answer for, so it correctly refused to submit. He answered all three
# in one line: "No criminal offence, Trusted score 10, commit more than 12
# months". These pin those answers, and — just as importantly — pin the edges
# his sentence does NOT cover, because the criminal-record rule used to flag a
# whole family of questions and only one of them is now answered.


def test_a_criminal_conviction_question_is_answered_no():
    """Was a flag ("Answer from your own record.") until he answered it."""
    result = answer("Have you ever been convicted of a criminal offence?", required=True)
    assert result["answer"] == "No"
    assert not result["needs_input"]


def test_a_criminal_record_question_is_answered_no_however_it_is_worded():
    for label in (
        "Do you have a criminal record?",
        "Have you ever been convicted of a criminal offence for which a pardon has not been granted?",
        "Have you been convicted of a crime?",
    ):
        result = answer(label, required=True)
        assert result["answer"] == "No", label
        assert not result["needs_input"], label


def test_the_criminal_answer_is_picked_from_the_forms_own_options():
    result = answer("Have you ever been convicted of a criminal offence?",
                    kind="select", options=["Yes", "No", "Prefer not to answer"], required=True)
    assert result["answer"] == "No"


def test_questions_his_answer_does_not_cover_are_still_flagged():
    """"No criminal offence" is not consent to a check, not a bondability
    declaration, and not a clearance he holds. The old rule caught all of these
    with one regex; answering one of them must not silently answer the rest."""
    for label in (
        "Are you willing to undergo a criminal background check?",
        "Are you bondable?",
        "Do you hold a valid security clearance?",
        "Can you provide a vulnerable sector check?",
    ):
        result = answer(label, required=True)
        assert result["needs_input"] is True, label


def test_a_confidential_information_rating_takes_his_ten():
    result = answer("On a scale of 1 to 10, how well can you be trusted with "
                    "confidential information?",
                    kind="select", options=[str(n) for n in range(1, 11)], required=True)
    assert result["answer"] == "10"
    assert not result["needs_input"]


def test_a_confidential_information_question_asked_as_yes_no_takes_yes():
    """Same statement, different question shape. A 10-out-of-10 trust rating and
    a "yes" are the same answer from him; flagging the yes/no variant would stall
    the wizard on a question he has already answered."""
    result = answer("Can you be trusted with confidential information?",
                    kind="select", options=["Yes", "No"], required=True)
    assert result["answer"] == "Yes"
    assert not result["needs_input"]


def test_a_commitment_length_question_takes_more_than_twelve_months():
    result = answer("How long can you commit to this availability?",
                    kind="select",
                    options=["Less than 6 months", "6 to 12 months", "More than 12 months"],
                    required=True)
    assert result["answer"] == "More than 12 months"
    assert not result["needs_input"]


def test_a_commitment_length_question_matches_a_differently_worded_longest_option():
    """Workday tenants word these ranges however they like. He said "more than
    12 months", so the longest bucket is his answer whatever it is called — but
    it is still chosen from the options the form actually offers."""
    result = answer("How long do you intend to stay in this position?",
                    kind="select",
                    options=["0-6 months", "6-12 months", "12+ months"], required=True)
    assert result["answer"] == "12+ months"
    assert not result["needs_input"]


def test_a_commitment_question_with_no_long_option_is_flagged_not_forced():
    """If the longest bucket on offer is shorter than what he committed to,
    there is no honest option to pick and the question goes back to him."""
    result = answer("How long can you commit?", kind="select",
                    options=["Less than 3 months", "3 to 6 months"], required=True)
    assert result["needs_input"] is True
