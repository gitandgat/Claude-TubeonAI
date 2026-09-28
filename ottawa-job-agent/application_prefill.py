"""Turn a job the pipeline couldn't submit into a one-click finish-it package.

Every non-submitted outcome (captcha gate, unconfirmed submit, prefilled-pending-
review, bot-blocked, Workday without credentials, Job Bank Direct Apply, no form
reached at all) ends here instead of in a bare "here's the link" email. Given the
form's questions — the real ones from form_schema.py when a page was reached, the
typical set for that portal when it wasn't — this answers every question it can
answer honestly, flags the rest, and writes a branded page he opens once and
pastes from.

Three answer sources, in descending order of trust:
  1. Deterministic — his own profile, the SCREENING answers autofill_sheet.py
     already reuses on every form, and the availability rule below. No model
     involved, so these can't drift between runs.
  2. Generated — "why this company", "why this role", "tell us about yourself",
     "relevant experience" only, written by the local Ollama model under
     content_generator.GROUNDING (the same honesty rules the cover letter runs
     under). Capped per job, because each call is real wall-clock time.
  3. NEEDS YOUR INPUT — anything where a plausible guess would become a lie on a
     real application: a "tell me about a time" anecdote, salary expectations, a
     criminal-record check, a CPR/First Aid certification he doesn't hold, a
     relative working there. Flagged amber with a one-line reason, never filled.

Availability is deterministic, not a flag: days and evenings including weekends,
no overnight. An availability grid gets every day/morning/afternoon/evening cell
ticked and every overnight cell left alone, and a single "can you work nights?"
boolean answers No — so an overnight-heavy posting fails honestly at the form
instead of after he's already taken the job.

US-scoped work-authorization questions are never auto-answered, for the same
reason web_applier.py leaves them blank: he is a Canadian PR, so "authorized to
work in the United States?" flips to No and "require sponsorship?" flips to Yes.
Those go to NEEDS YOUR INPUT rather than inheriting the Canadian answer.
"""

import html
import json
import re
from pathlib import Path
from typing import List, Optional

from autofill_sheet import REFERENCES_NOTE, SCREENING
# _call / _strip_meta_commentary / GROUNDING / _job_context are content_generator's
# own private helpers, imported rather than re-implemented so every generated
# sentence in this repo goes through one prompt preamble and one meta-stripper.
from content_generator import GROUNDING, _call, _job_context, _strip_meta_commentary
from resume_data import PROFILE
from web_applier import BOOLEAN_ANSWERS, US_CONTEXT, _GENERIC_TEXT_FIELDS

PREFILL_DIR = Path(__file__).resolve().parent / "prefilled"
PREFILL_DIR.mkdir(exist_ok=True)

AVAILABILITY_ANSWER = "Days and evenings, including weekends. Not available for overnight shifts."
NO_OVERNIGHT_ANSWER = "No — available days and evenings including weekends, but not overnight."
DECLINE_ANSWER = "Prefer not to answer"

# Each generated answer is a local Ollama round trip (~10-30s on this machine),
# and a Workday wizard can ask a dozen free-text questions. Past the cap the rest
# are flagged for him rather than silently stretching a daily run past the
# watchdog.
MAX_GENERATED_ANSWERS = 4
GENERATED_MAX_TOKENS = 220

# "Have you worked here before?" is Yes only for places he has actually worked.
# PROFILE["experience"] can't be used directly — its first entry is the "Career
# Transition" placeholder covering the gap, which is not an employer.
PAST_EMPLOYERS = (
    "Carraway Traffic & Safety",
    "Sault Area Hospital",
    "Tha Sae Hospital",
)

_EDUCATION_LINE = "; ".join(
    f"{e['degree']}, {e['school']} ({e['dates']})" for e in PROFILE["education"]
)
_CERTIFICATIONS_LINE = "; ".join(PROFILE["certifications"])


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


# --- Question classification ------------------------------------------------

# Checked before every other rule: a wrong answer here is a lie on a real
# application, so each carries the reason it can only come from him.
_NEEDS_INPUT_RULES = [
    (re.compile(r"tell (me|us) about a time|describe a (situation|time|challenge)|"
                r"give (me|us) an example|a time when|an example of when", re.I),
     "Needs a real example from you — I won't invent one."),
    (re.compile(r"salary|compensation|hourly rate|expected pay|pay expectation|"
                r"wage expectation|desired (pay|rate|salary)", re.I),
     "Your number to set."),
    # He answered the conviction question itself on Sep 12 2026 ("No criminal
    # offence"), and that answer moved to _STANDING_ANSWERS below. What stays
    # here is everything his sentence does not cover: consenting to a check,
    # being bondable, and holding a clearance are three different questions,
    # and a clean record answers none of them.
    (re.compile(r"police (record|check)|background check|vulnerable sector|"
                r"security clearance|bondable|reference check", re.I),
     "Answer from your own record."),
    (re.compile(r"\bcpr\b|first aid|\baed\b|basic life support|\bbls\b", re.I),
     "Not on your certification list — answer Yes only if you've certified since."),
    (re.compile(r"relative|family member|(friend|anyone you know).*(work|employ)|"
                r"know (anyone|someone).*(work|employ)", re.I),
     "Only you know this."),
]

# Voluntary self-identification. Declining is a real, accepted answer on every
# one of these, so it is a filled answer rather than a flag.
_DECLINE_RE = re.compile(
    r"gender|\brace\b|ethnic|veteran|disabilit|self-?identif|visible minorit|"
    r"indigenous|aboriginal|sexual orientation|lgbt|pronoun|marital status",
    re.I,
)

_OVERNIGHT_RE = re.compile(r"overnight|night shift|nights|graveyard|11pm|midnight|third shift", re.I)
_AVAILABILITY_RE = re.compile(
    r"availab(le|ility).*(shift|schedule|work|hour)|(shift|schedule|hour).*availab|"
    r"which (shifts|hours|days)|willing to work|weekend|evening|days? of the week",
    re.I,
)
_DAY_OR_SHIFT_RE = re.compile(
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|morning|afternoon|evening",
    re.I,
)

_COVER_LETTER_RE = re.compile(r"cover letter|letter of (interest|application)|motivation letter", re.I)
_RESUME_RE = re.compile(r"resum|\bcv\b|curriculum vitae", re.I)

# Free-text questions the model may answer, and the prompt shape for each.
_GENERATED_RULES = [
    ("why_them",
     re.compile(r"why (do you want to work|are you interested in|this company|"
                r"do you (want|wish) to join)|interest in (our|this) (company|organization|team)|"
                r"why (us|our)", re.I),
     "Why does this employer specifically interest him?"),
    ("why_role",
     re.compile(r"why (this|the) (role|position|job)|why (are you|would you be) a (good|strong) fit|"
                r"what makes you a (good|strong) (fit|candidate)|why should we (hire|consider)|"
                r"what (do you bring|can you bring)", re.I),
     "Why is he a fit for this specific role?"),
    ("about",
     re.compile(r"tell us about yourself|about yourself|introduce yourself|"
                r"personal statement|summary of your background|brief (bio|introduction)", re.I),
     "A short first-person introduction covering his background."),
    ("experience",
     re.compile(r"relevant experience|related experience|describe your experience|"
                r"experience (relevant|related) to|qualifications for this|"
                r"how does your (experience|background)", re.I),
     "Which parts of his actual background are relevant to this posting?"),
]

# Deterministic profile answers. _GENERIC_TEXT_FIELDS is web_applier's own fill
# table (name/email/phone/address parts/LinkedIn/website), reused verbatim so the
# page shows exactly what the automated fill would have entered.
# "Phone Extension" / "Ext." — an extension he does not have. Blank is the
# honest answer; the generic phone rule's answer was not.
_PHONE_EXTENSION_RE = re.compile(r"\b(phone\s*)?(extension|ext\.?)\b", re.I)

# "Country Phone Code" wants +1, not "Canada" — it sits next to the number, and
# both the \bcountry\b rule and the phone rule claim it.
_PHONE_COUNTRY_CODE_RE = re.compile(
    r"\b(country\s*(phone|dial|calling|area)\s*code"
    r"|(phone|dial|calling)\s*country\s*code)\b", re.I)

_PROFILE_ANSWERS = [
    (re.compile(r"full address|mailing address|home address|^address$", re.I), PROFILE["address"]),
    (re.compile(r"\bcountry\b", re.I), PROFILE["address_components"]["country"]),
] + [(pattern, value) for pattern, value, _ in _GENERIC_TEXT_FIELDS] + [
    (re.compile(r"work (status|eligibility)|status in canada|immigration status|"
                r"citizenship status|permanent resident", re.I), PROFILE["status"]),
    (re.compile(r"start date|available to start|when can you start|earliest.*start|"
                r"notice period|availability to begin", re.I), SCREENING["Available start date"]),
    (re.compile(r"how did you hear|how do you hear|referral source|source of application|"
                r"where did you (hear|find|see)", re.I), SCREENING["How did you hear about us?"]),
    (re.compile(r"highest (level of )?education|education level|highest degree", re.I),
     SCREENING["Highest education"]),
    (re.compile(r"school|university|college|institution|degree|diploma|education", re.I),
     _EDUCATION_LINE),
    (re.compile(r"language", re.I), SCREENING["Languages"]),
    (re.compile(r"years of experience|how many years|length of experience", re.I),
     SCREENING["Years of experience (healthcare/coaching)"]),
    (re.compile(r"certification|credential|licen[cs]es? (you )?(hold|have)|"
                r"professional (designation|membership)", re.I), _CERTIFICATIONS_LINE),
    (re.compile(r"(18|eighteen) years|age of majority|of legal working age|legal age", re.I), "Yes"),
    (re.compile(r"relocat", re.I), "Not required — already based in Ottawa."),
    (re.compile(r"reference", re.I), REFERENCES_NOTE),
]

# Preference order for "how did you hear about us?" when the field constrains the
# answer to a fixed option list.
_HEAR_ABOUT_PREFERENCES = [
    re.compile(r"company (web)?site|our (web)?site|career site", re.I),
    re.compile(r"job board|job posting|online (job )?(board|posting|ad)", re.I),
    re.compile(r"online|internet|web search|search engine|google", re.I),
    re.compile(r"\bwebsite\b", re.I),
    re.compile(r"other", re.I),
]

# Deliberately demands an explicit reference to *this* employer. Without it,
# "have you ever worked in a fitness environment?" would inherit the No that
# only belongs to "have you ever worked for us?".
# The same question phrased with the employer's name instead of "this company"
# ("have you ever worked for GoodLife?"). Only trusted when a distinctive word
# from the company name is in the label — see _company_tokens.
_LOOSE_PRIOR_EMPLOYMENT_RE = re.compile(
    r"\b(previously|ever|before|in the past)\b.{0,60}(employed|worked)", re.I
)

# Words too generic to identify an employer: "have you ever worked in a fitness
# environment?" must not read as "…worked for GoodLife Fitness?".
_GENERIC_COMPANY_WORDS = {
    "inc", "ltd", "llc", "corp", "corporation", "company", "the", "and", "for",
    "fitness", "hospital", "health", "healthcare", "group", "services", "service",
    "centre", "center", "clinic", "care", "systems", "solutions", "canada", "ottawa",
}


def _company_tokens(company: str) -> list:
    return [t for t in _norm(company).split()
            if len(t) >= 4 and t not in _GENERIC_COMPANY_WORDS]


# Work-eligibility wording, used only to sharpen the hint on a US-scoped
# question that no BOOLEAN_ANSWERS pattern happened to match — e.g. "Are you
# authorized to work in the U.S. without sponsorship?" matches neither
# "legally authoriz" nor "require.*sponsorship", so it lands on the generic
# fallback and he'd get no clue why. It never answers anything.
_WORK_ELIGIBILITY_RE = re.compile(
    r"authoriz|eligib|entitle|sponsor|visa|work permit|right to work", re.I
)

_PREVIOUSLY_EMPLOYED_RE = re.compile(
    r"\b(previously|ever|before|in the past)\b.{0,60}(employed|worked).{0,60}"
    r"(here|(for|by|with|at) (us|this|our)|"
    r"this (company|organization|organisation|employer|club|hospital)|"
    r"our (company|organization|organisation|team))"
    r"|former (employee|staff)"
    r"|(are|were) you a (former|previous|past) employee",
    re.I,
)

# "Are you a current Associate (paid employee) at any of the following
# brands/organizations: GoodLife Fitness, Fit4Less, …" — GoodLife asks this on
# every posting and it blocked the Queen and Bank run. It is a fact about right
# now, not a judgement: someone applying from outside is not on their payroll.
# The wording never says "previously", so _PREVIOUSLY_EMPLOYED_RE misses it.
_CURRENTLY_EMPLOYED_RE = re.compile(
    r"\b(are you (currently|presently|now)\b.{0,40}(employed|working|an? (employee|associate|staff))"
    r"|are you an? current\b.{0,40}(employee|associate|staff|team member|contractor))",
    re.I,
)

# Words that turn a bare "are you currently employed?" — a question about his
# own situation — into one about theirs. Without a marker like this the No
# would be answering the wrong question.
_THIS_EMPLOYER_RE = re.compile(
    r"\b(here|with us|for us|by us|"
    r"(at|by|for|with|of) (this|our)\b|"
    r"this (company|organization|organisation|employer|club|hospital)|"
    r"our (company|organization|organisation|team))",
    re.I,
)


# --- Answering --------------------------------------------------------------

def _ready(field: dict, answer: str, source: str) -> dict:
    return {
        "label": field["label"],
        "kind": field.get("kind", "text"),
        "required": bool(field.get("required")),
        "answer": answer,
        "source": source,
        "needs_input": False,
        "hint": "",
    }


def _needs(field: dict, hint: str) -> dict:
    return {
        "label": field["label"],
        "kind": field.get("kind", "text"),
        "required": bool(field.get("required")),
        "answer": "",
        "source": "needs_input",
        "needs_input": True,
        "hint": hint,
    }


# Shortest string allowed to match an option by containment rather than
# outright. Below this, initialisms ("ON", "PR") collide with unrelated words.
_MIN_CONTAINMENT_CHARS = 4

# His address is stored as "ON" (right for a text box), but a Workday province
# dropdown lists full names. Same province either way — expand it rather than
# letting a two-letter containment match go hunting through the option list.
_PROVINCE_NAMES = {
    "ab": "Alberta", "bc": "British Columbia", "mb": "Manitoba",
    "nb": "New Brunswick", "nl": "Newfoundland and Labrador",
    "ns": "Nova Scotia", "nt": "Northwest Territories", "nu": "Nunavut",
    "on": "Ontario", "pe": "Prince Edward Island", "qc": "Quebec",
    "sk": "Saskatchewan", "yt": "Yukon",
}


def match_option(answer: str, options: list) -> Optional[str]:
    """Map a deterministic answer onto one of the field's real options.

    Returns None when nothing matches, so the caller flags the question instead
    of pasting text the form will reject. An unconstrained field (no options)
    keeps the answer as written."""
    if not options:
        return answer

    target = _norm(answer)
    for opt in options:
        if _norm(opt) == target:
            return opt

    # "Yes — Canadian Permanent Resident" still selects a plain "Yes".
    head = _norm(re.split(r"[—,\-(]", answer)[0])
    for opt in options:
        if head and _norm(opt) == head:
            return opt

    expanded = _norm(_PROVINCE_NAMES.get(target, ""))
    if expanded:
        for opt in options:
            if _norm(opt) == expanded:
                return opt

    # Containment, but only where it means something. A bare `in` test let a
    # two-letter answer land on any option that happened to contain those
    # letters — match_option("ON", ["None of the above", "Ontario"]) returns
    # "None of the above", a real option and the wrong answer, which is exactly
    # the kind of thing that must never be submitted under his name. Require a
    # substantial match sitting on word boundaries instead.
    for opt in options:
        norm_opt = _norm(opt)
        if not norm_opt:
            continue
        inner, outer = sorted((norm_opt, target), key=len)
        if len(inner) < _MIN_CONTAINMENT_CHARS:
            continue
        if re.search(r"\b{}\b".format(re.escape(inner)), outer):
            return opt

    return None


# --- standing answers he has given once, for questions that used to stall ------
#
# Each of these was a required question the wizard could not answer honestly, so
# the run stopped before Submit — correctly, but permanently, because nothing
# downstream could resolve them. He answered all three on Sep 12 2026. They are
# rules rather than literal strings because the same question arrives in
# different shapes on different tenants, and the answer is only ever chosen from
# the options the form itself offers.

_CRIMINAL_RECORD_RE = re.compile(
    r"convict|criminal (record|offen[cs]e|conviction|charge)|"
    r"been charged with (a|any) (crime|offen[cs]e)", re.I)

_CONFIDENTIAL_TRUST_RE = re.compile(
    r"confidential|discretion|sensitive information|privacy of (member|client|patient)",
    re.I)

_COMMITMENT_LENGTH_RE = re.compile(
    r"how long.*(commit|stay|remain|intend)|length of (commitment|availability)|"
    r"(commit|stay|remain).*how long|intend to stay", re.I)

# "more than 12 months", in the wordings tenants actually use. Ordered longest
# first so the top bucket wins when several match.
_LONG_COMMITMENT_PREFERENCES = [
    re.compile(r"(more than|over|at least|longer than)\s*(12|twelve)\s*month", re.I),
    re.compile(r"(12|twelve)\s*\+\s*month|(12|twelve)\s*month(s)?\s*(or more|\+)", re.I),
    re.compile(r"(more than|over|at least|longer than)\s*(1|one|a)\s*year|(1|one)\s*\+\s*year", re.I),
    re.compile(r"indefinit|long[- ]?term|permanent|no (set )?end date", re.I),
]


def _confidential_trust_answer(options: list) -> Optional[str]:
    """His "trusted score 10", applied to whichever shape the question takes.

    A 1-to-10 self-rating and a plain yes/no are the same statement from him, so
    both are answered; anything else is not, and falls through to a flag rather
    than guessing which end of an unfamiliar scale he meant.
    """
    if not options:
        return "10"
    numeric = [o for o in options if _norm(o).isdigit()]
    if numeric:
        return max(numeric, key=lambda o: int(_norm(o)))
    for opt in options:
        if _norm(opt) in ("yes", "strongly agree", "always"):
            return opt
    return None


def _commitment_length_answer(options: list) -> Optional[str]:
    """The longest bucket the form offers, but only if it reaches what he
    committed to. A form whose top option is "3 to 6 months" has no honest
    answer for "more than 12 months", so that question goes back to him."""
    if not options:
        return "More than 12 months"
    for pattern in _LONG_COMMITMENT_PREFERENCES:
        for opt in options:
            if pattern.search(opt):
                return opt
    return None


def _hear_about_answer(options: list) -> Optional[str]:
    if not options:
        return SCREENING["How did you hear about us?"]
    for pattern in _HEAR_ABOUT_PREFERENCES:
        for opt in options:
            if pattern.search(opt):
                return opt
    return None


def _availability_answer(label: str, kind: str) -> Optional[str]:
    """His stated availability, applied to whatever shape the form asks in."""
    is_tickbox = kind in ("checkbox", "radio", "select")
    # A checkbox row in an availability grid is an instruction, not a Yes/No —
    # say which way to leave it so the page can be worked through top to bottom.
    yes = "Tick this one" if kind == "checkbox" else "Yes"
    no = "Leave this one unticked" if kind == "checkbox" else "No"

    if _OVERNIGHT_RE.search(label):
        return no if is_tickbox else NO_OVERNIGHT_ANSWER

    # One cell of an availability grid ("Tuesday – Evening").
    if is_tickbox and _DAY_OR_SHIFT_RE.search(label):
        return yes

    if _AVAILABILITY_RE.search(label):
        return yes if is_tickbox else AVAILABILITY_ANSWER

    return None


def _availability_option(options: list) -> Optional[str]:
    """Pick the listed shift bundle that matches days + evenings including
    weekends. Any option containing overnight is disqualified outright, so a
    tempting "Any shift" never gets selected on his behalf."""
    safe = [o for o in options if not _OVERNIGHT_RE.search(o)]
    for opt in safe:
        if re.search(r"day", opt, re.I) and re.search(r"evening", opt, re.I):
            return opt
    for opt in safe:
        if re.search(r"\bday", opt, re.I):
            return opt
    return None


def _previously_employed_answer(company: str) -> str:
    normalized = _norm(company)
    for employer in PAST_EMPLOYERS:
        if _norm(employer) in normalized or normalized in _norm(employer):
            return "Yes"
    return "No"


def _generate_answer(kind: str, ask: str, job: dict) -> str:
    """One short first-person answer, under the same honesty rules as the cover
    letter. Returns "" when Ollama is unreachable so the caller flags the
    question rather than shipping an empty box."""
    length = "two or three sentences" if kind == "about" else "three or four sentences"
    prompt = (
        f"{GROUNDING}\n\n"
        f"{_job_context(job)}\n\n"
        f"Application question: {ask}\n"
        f"Write Sahawat's answer in {length}, first person, plain language. "
        f"No greeting, no sign-off, no heading — just the answer text."
    )
    return _strip_meta_commentary(_call(GENERATED_MAX_TOKENS, prompt))


def answer_field(field: dict, job: dict, cover_letter: str = "", resume_pdf: str = "",
                 generated_budget: int = 0) -> dict:
    """Answer one field, falling back to a value the form already holds.

    Workday pre-fills parts of its wizard from the candidate's own saved
    profile, so a field can arrive already correctly answered — Phone Device
    Type came in as "Mobile". No rule below speaks to that question, so it was
    reported as needing his input and, being required, stopped the run one step
    into a five-step wizard. A value already on the form is his own data, not a
    guess, so it counts as answered — but only as a fallback, so a real rule
    still wins and can still correct it.
    """
    answer = _derive_answer(field, job, cover_letter, resume_pdf, generated_budget)
    existing = str(field.get("value") or "").strip()
    if answer["needs_input"] and existing:
        return _ready(field, existing, "already_on_form")
    return answer


def _derive_answer(field: dict, job: dict, cover_letter: str = "", resume_pdf: str = "",
                   generated_budget: int = 0) -> dict:
    """Answer one form field. Never guesses: anything without a deterministic or
    honestly-generatable answer comes back flagged for him."""
    label = field.get("label", "") or ""
    kind = field.get("kind", "text") or "text"
    options = field.get("options") or []

    if kind == "file":
        if _RESUME_RE.search(label):
            name = Path(resume_pdf).name if resume_pdf else "resume PDF"
            return _ready(field, f"Upload: {name}", "resume")
        if _COVER_LETTER_RE.search(label):
            return _ready(field, "Upload or paste the cover letter below", "cover_letter")
        return _needs(field, "Upload this one yourself.")

    if _COVER_LETTER_RE.search(label):
        if cover_letter:
            return _ready(field, cover_letter, "cover_letter")
        return _needs(field, "No cover letter was generated for this job.")

    availability = _availability_answer(label, kind)
    if availability is not None:
        if options and availability not in ("No", NO_OVERNIGHT_ANSWER):
            picked = _availability_option(options)
            if picked:
                return _ready(field, picked, "availability")
        matched = match_option(availability, options)
        if matched is None:
            return _needs(field, "None of the options match days/evenings/weekends, no overnight.")
        return _ready(field, matched, "availability")

    if _CRIMINAL_RECORD_RE.search(label):
        matched = match_option("No", options)
        if matched is None:
            return _needs(field, "None of the options say No.")
        return _ready(field, matched, "standing_answer")

    if _CONFIDENTIAL_TRUST_RE.search(label):
        picked = _confidential_trust_answer(options)
        if picked is not None:
            return _ready(field, picked, "standing_answer")

    if _COMMITMENT_LENGTH_RE.search(label):
        picked = _commitment_length_answer(options)
        if picked is None:
            return _needs(field, "No option reaches the 12+ months you committed to.")
        return _ready(field, picked, "standing_answer")

    for pattern, hint in _NEEDS_INPUT_RULES:
        if pattern.search(label):
            return _needs(field, hint)

    if _DECLINE_RE.search(label):
        matched = match_option(DECLINE_ANSWER, options)
        return _ready(field, matched or DECLINE_ANSWER, "screening")

    company = job.get("company", "") or ""
    named_employer = bool(_LOOSE_PRIOR_EMPLOYMENT_RE.search(label)) and any(
        token in _norm(label) for token in _company_tokens(company)
    )
    if _CURRENTLY_EMPLOYED_RE.search(label) and (
            _THIS_EMPLOYER_RE.search(label)
            or any(token in _norm(label) for token in _company_tokens(company))):
        # An employer he has actually worked for is the one case where "are you
        # currently one of ours?" isn't answerable from the outside — the past
        # employment is on record, whether it ended is his to state.
        if _previously_employed_answer(company) == "Yes":
            return _needs(field, "You've worked here before — say whether that's current.")
        matched = match_option("No", options)
        return _ready(field, matched or "No", "screening")

    if _PREVIOUSLY_EMPLOYED_RE.search(label) or named_employer:
        answer = _previously_employed_answer(company)
        matched = match_option(answer, options)
        return _ready(field, matched or answer, "screening")

    for pattern, answer in BOOLEAN_ANSWERS:
        if not pattern.search(label):
            continue
        if US_CONTEXT.search(label):
            return _needs(field, "US-scoped — the Canadian answer doesn't carry over.")
        matched = match_option(answer, options)
        if matched is None:
            return _needs(field, "No option matches the honest Yes/No answer.")
        return _ready(field, matched, "screening")

    if re.search(r"how did you hear|referral source|where did you (hear|find|see)", label, re.I):
        answer = _hear_about_answer(options)
        if answer is None:
            return _needs(field, "None of the listed sources apply.")
        return _ready(field, answer, "screening")

    # Two fields the generic phone/country rules reach but cannot answer. Both
    # were caught in a live GoodLife run: "Phone Extension" came back holding
    # his phone number, and "Country Phone Code*" came back "Canada". A missed
    # question stops a run; a wrong value gets submitted and stays in the
    # employer's ATS under his name, so these are checked before the tables.
    if _PHONE_EXTENSION_RE.search(label):
        if field.get("required"):
            return _needs(field, "This form insists on an extension — say what to put.")
        return _ready(field, "", "profile")

    if _PHONE_COUNTRY_CODE_RE.search(label):
        for candidate in ("Canada (+1)", "+1", "Canada"):
            matched = match_option(candidate, options)
            if matched is not None:
                return _ready(field, matched if options else "+1", "profile")
        return _needs(field, "None of the listed dial codes is Canada's.")

    for pattern, answer in _PROFILE_ANSWERS:
        if not pattern.search(label):
            continue
        if not str(answer or "").strip():
            # The profile knows this field exists but holds nothing for it —
            # today, the postal code of the Cooper St address. Typing an empty
            # string and calling it ready is how a blank lands on a submitted
            # application; the honest move is to ask him for it once.
            return _needs(field, "Your profile has no value for this yet — add it.")
        matched = match_option(answer, options)
        if matched is None:
            return _needs(field, "No option matches what's on your profile.")
        return _ready(field, matched, "profile")

    for gen_kind, pattern, ask in _GENERATED_RULES:
        if not pattern.search(label):
            continue
        if generated_budget <= 0:
            return _needs(field, "Free-text answer — write this one in your own words.")
        text = _generate_answer(gen_kind, ask, job)
        if not text:
            return _needs(field, "Ollama was unreachable — draft this one yourself.")
        return _ready(field, text, "generated")

    if US_CONTEXT.search(label) and _WORK_ELIGIBILITY_RE.search(label):
        return _needs(field, "US-scoped — the Canadian answer doesn't carry over.")

    return _needs(field, "No safe answer on file — fill this one in yourself.")


def answer_fields(fields: list, job: dict, cover_letter: str = "", resume_pdf: str = "") -> list:
    """Answer every field, spending the generated-answer budget on the earliest
    free-text questions (which are the ones an employer actually reads)."""
    budget = MAX_GENERATED_ANSWERS
    answers = []
    for field in fields:
        if not (field.get("label") or "").strip():
            continue
        answer = answer_field(field, job, cover_letter, resume_pdf, generated_budget=budget)
        if answer["source"] == "generated":
            budget -= 1
        answers.append(answer)
    return answers


# --- Fallback question set --------------------------------------------------

# What to build a package from when no form was ever reached: the screening
# questions every application asks, plus the extra ones a Workday wizard adds.
# Labelled as typical rather than real so the page never implies these came off
# the employer's actual form.
_TYPICAL_FIELDS = [
    {"label": "First name", "kind": "text", "required": True},
    {"label": "Last name", "kind": "text", "required": True},
    {"label": "Email", "kind": "email", "required": True},
    {"label": "Phone", "kind": "tel", "required": True},
    {"label": "Street address", "kind": "text", "required": True},
    {"label": "City", "kind": "text", "required": True},
    {"label": "Province", "kind": "text", "required": True},
    {"label": "Postal code", "kind": "text", "required": True},
    {"label": "Are you legally authorized to work in Canada?", "kind": "select",
     "required": True, "options": ["Yes", "No"]},
    {"label": "Do you require sponsorship?", "kind": "select",
     "required": True, "options": ["Yes", "No"]},
    {"label": "Available start date", "kind": "date", "required": True},
    {"label": "Highest level of education", "kind": "text", "required": False},
    {"label": "Languages", "kind": "text", "required": False},
    {"label": "Resume / CV", "kind": "file", "required": True},
    {"label": "How did you hear about us?", "kind": "text", "required": False},
]

_WORKDAY_EXTRA_FIELDS = [
    {"label": "Have you previously been employed by this organization?", "kind": "select",
     "required": True, "options": ["Yes", "No"]},
    {"label": "Which shifts are you available to work?", "kind": "textarea", "required": False},
    {"label": "Voluntary self-identification", "kind": "select", "required": False,
     "options": ["Prefer not to answer"]},
]


def typical_fields(ats: str = "") -> list:
    fields = [dict(f) for f in _TYPICAL_FIELDS]
    if (ats or "").lower() == "workday":
        fields.extend(dict(f) for f in _WORKDAY_EXTRA_FIELDS)
    return fields


# --- Rendering --------------------------------------------------------------

def _answer_row(answer: dict) -> str:
    label = html.escape(answer["label"])
    if answer["required"]:
        label += ' <span class="req">required</span>'

    if answer["needs_input"]:
        return f"""    <div class="row needs">
      <div class="label">{label}</div>
      <div class="value"><b>Needs your input</b><span class="hint">{html.escape(answer["hint"])}</span></div>
      <span class="tag">you</span>
    </div>"""

    value = answer["answer"]
    return f"""    <div class="row">
      <div class="label">{label}</div>
      <div class="value">{html.escape(value)}</div>
      <button class="copy" onclick='copyText({json.dumps(value)}, this)'>Copy</button>
    </div>"""


def _section(title: str, rows: str) -> str:
    return f"""  <section>
    <h2>{html.escape(title)}</h2>
{rows}
  </section>"""


def _header_meta(job: dict) -> str:
    bits = [job.get("company", ""), job.get("location", "")]
    if job.get("score") is not None:
        bits.append(f"fit {job['score']}/10")
    # Two shapes reach here. A live job from job_agent.py carries walkability's full
    # dict; a record read back out of applications.json carries only the label string,
    # because tracker.record_pending flattens it on the way in. Accept both — any
    # consumer that rebuilds a package from the tracker (apply_interested.py) hits the
    # flattened shape, and crashing on it loses the whole run.
    commute = job.get("commute") or {}
    label = commute.get("label", "") if isinstance(commute, dict) else str(commute)
    if label:
        bits.append(label)
    return " · ".join(b for b in bits if b)


def render_html(job: dict, answers: list, apply_url: str, cover_letter: str = "",
                resume_pdf: str = "", questions_are_typical: bool = False) -> str:
    n_needs = sum(1 for a in answers if a["needs_input"])
    n_ready = len(answers) - n_needs
    posting_url = job.get("url", "") or ""

    caveat = ""
    if questions_are_typical:
        caveat = ('<p class="caveat">The form itself couldn\'t be reached, so these are the '
                  'questions this kind of application usually asks — check them against the real '
                  'form when you open it.</p>')

    sections = [_section("Application questions", "\n".join(_answer_row(a) for a in answers))]

    if cover_letter:
        sections.append(f"""  <section>
    <h2>Cover letter</h2>
    <pre class="letter">{html.escape(cover_letter)}</pre>
    <button class="copy" onclick='copyText({json.dumps(cover_letter)}, this)'>Copy cover letter</button>
  </section>""")

    if resume_pdf:
        sections.append(_section("Resume", _answer_row({
            "label": "Attach this file",
            "required": False,
            "needs_input": False,
            "answer": Path(resume_pdf).name,
        })))

    apply_button = ""
    if apply_url:
        apply_button = f'<a class="cta" href="{html.escape(apply_url)}">Apply here →</a>'
    posting_link = ""
    if posting_url and posting_url != apply_url:
        posting_link = f'<a class="secondary" href="{html.escape(posting_url)}">Open posting</a>'

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="robots" content="noindex" />
<title>{html.escape(job.get("title", "Application"))} — prefilled application</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
<style>
  :root {{ --amber:#D4A843; --charcoal:#2C2C2C; --warm-white:#FAF7F2; --teal:#5B9A8B; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:"Inter",sans-serif; background:var(--warm-white); color:var(--charcoal); padding:clamp(1.5rem,5vw,4rem); }}
  h1 {{ font-family:"Playfair Display",serif; font-size:clamp(1.8rem,1rem+3vw,3rem); }}
  .sub {{ color:#666; margin:0.5rem 0 1.5rem; max-width:60ch; }}
  .actions {{ display:flex; flex-wrap:wrap; gap:0.75rem; align-items:center; margin-bottom:1rem; }}
  .cta {{ display:inline-block; background:var(--amber); color:var(--charcoal); text-decoration:none;
    border-radius:999px; padding:0.85rem 1.9rem; font-weight:600; transition:transform 0.15s; }}
  .cta:hover {{ transform:translateY(-2px); }}
  .secondary {{ color:var(--teal); text-decoration:none; font-weight:600; font-size:0.9rem;
    border-bottom:1px solid rgba(91,154,139,0.4); }}
  .count {{ font-size:0.9rem; color:#666; margin-bottom:2.5rem; }}
  .count b {{ color:var(--charcoal); }}
  .caveat {{ background:rgba(212,168,67,0.12); border-left:3px solid var(--amber); padding:0.85rem 1.1rem;
    border-radius:0 8px 8px 0; font-size:0.9rem; margin-bottom:1.5rem; max-width:70ch; }}
  section {{ background:#fff; border-radius:14px; padding:1.5rem 1.75rem; margin-bottom:1.5rem;
    box-shadow:0 4px 20px rgba(44,44,44,0.06); border:1px solid rgba(44,44,44,0.08); }}
  h2 {{ font-size:0.8rem; letter-spacing:0.18em; text-transform:uppercase; color:var(--teal);
    margin-bottom:1.25rem; }}
  .row {{ display:grid; grid-template-columns:240px 1fr auto; gap:1rem; align-items:start;
    padding:0.75rem 0; border-top:1px solid rgba(44,44,44,0.07); }}
  .row:first-of-type {{ border-top:none; }}
  .row.needs {{ background:rgba(212,168,67,0.08); border-left:3px solid var(--amber);
    padding-left:0.9rem; margin-left:-0.9rem; border-radius:0 8px 8px 0; }}
  .label {{ font-weight:600; font-size:0.85rem; color:#555; }}
  .req {{ color:var(--amber); font-weight:600; font-size:0.7rem; letter-spacing:0.06em;
    text-transform:uppercase; }}
  .value {{ font-size:0.92rem; word-break:break-word; white-space:pre-wrap; }}
  .hint {{ display:block; color:#777; font-size:0.82rem; margin-top:0.2rem; }}
  .tag {{ background:var(--amber); color:var(--charcoal); border-radius:999px; padding:0.35rem 0.9rem;
    font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; }}
  .letter {{ font-family:"Inter",sans-serif; font-size:0.92rem; line-height:1.65; white-space:pre-wrap;
    margin-bottom:1.25rem; }}
  .copy {{ background:var(--charcoal); color:var(--warm-white); border:none; border-radius:999px;
    padding:0.45rem 1.1rem; font-size:0.8rem; font-weight:600; cursor:pointer; transition:background 0.2s; }}
  .copy:hover {{ background:var(--amber); color:var(--charcoal); }}
  .copy.done {{ background:var(--teal); }}
  @media (max-width:640px) {{ .row {{ grid-template-columns:1fr auto; }} .label {{ grid-column:1/-1; }} }}
</style></head>
<body>
<h1>{html.escape(job.get("title", "Application"))}</h1>
<p class="sub">{html.escape(_header_meta(job))}</p>
<div class="actions">{apply_button}{posting_link}</div>
<p class="count"><b>{n_ready}</b> answers ready · <b>{n_needs}</b> need your input</p>
{caveat}
{chr(10).join(sections)}
<script>
function copyText(text, btn) {{
  navigator.clipboard.writeText(text).then(() => {{
    const old = btn.textContent; btn.textContent = "Copied!"; btn.classList.add("done");
    setTimeout(() => {{ btn.textContent = old; btn.classList.remove("done"); }}, 1200);
  }});
}}
</script>
</body></html>"""


# --- Entry point ------------------------------------------------------------

def build_prefill(job: dict, form_fields: Optional[List[dict]] = None, cover_letter: str = "",
                  resume_pdf: str = "", apply_url: str = "") -> dict:
    """Write prefilled/<job_id>.html + .json for one job.

    form_fields comes from form_schema.extract_form_fields when a page was
    actually reached; None or [] means no form was seen, and the package falls
    back to the typical question set for that portal, clearly labelled as such.
    Returns the counts job_agent.py stores on the job and puts in the digest."""
    fields = list(form_fields or [])
    questions_are_typical = not fields
    if questions_are_typical:
        fields = typical_fields(job.get("ats", ""))

    answers = answer_fields(fields, job, cover_letter, resume_pdf)
    resolved_apply_url = apply_url or job.get("apply_url") or job.get("url", "") or ""

    n_needs = sum(1 for a in answers if a["needs_input"])
    n_ready = len(answers) - n_needs

    job_id = job.get("id") or _norm(f"{job.get('title', '')} {job.get('company', '')}").replace(" ", "-")
    html_path = PREFILL_DIR / f"{job_id}.html"
    json_path = PREFILL_DIR / f"{job_id}.json"

    html_path.write_text(
        render_html(job, answers, resolved_apply_url, cover_letter, resume_pdf, questions_are_typical),
        encoding="utf-8",
    )
    json_path.write_text(json.dumps({
        "job_id": job_id,
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "apply_url": resolved_apply_url,
        "posting_url": job.get("url", ""),
        "questions_are_typical": questions_are_typical,
        "n_ready": n_ready,
        "n_needs_input": n_needs,
        "answers": answers,
    }, indent=2), encoding="utf-8")

    return {
        "html": str(html_path),
        "json": str(json_path),
        "apply_url": resolved_apply_url,
        "n_ready": n_ready,
        "n_needs_input": n_needs,
        "n_required_needs_input": sum(1 for a in answers if a["needs_input"] and a["required"]),
        "questions_are_typical": questions_are_typical,
        "answers": answers,
    }


if __name__ == "__main__":
    # Offline demo: the typical Workday question set, no network, no Ollama call
    # (none of these labels route to a generated answer).
    demo_job = {
        "id": "demo",
        "title": "Personal Trainer - Ottawa Queen and Bank",
        "company": "GoodLife Fitness",
        "location": "Ottawa, ON",
        "url": "https://goodlifefitness.wd3.myworkdayjobs.com/Careers/job/demo/apply",
        "ats": "workday",
        "score": 8,
        "commute": {"label": "🚶 10 min walk"},
    }
    out = build_prefill(demo_job, None, cover_letter="", resume_pdf="resumes/fitness.pdf")
    print(f"{out['n_ready']} ready · {out['n_needs_input']} need input")
    print(out["html"])
