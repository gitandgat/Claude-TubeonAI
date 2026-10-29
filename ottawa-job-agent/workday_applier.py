"""Workday auto-apply through Sahawat's own candidate account.

Workday is the one ATS in this pipeline that refuses to take an application from
an anonymous browser: every posting funnels through a candidate account on the
employer's own tenant. web_applier.py's generic path detects `workday` and then
fails, because there is no form on the page until you sign in — which is why
GoodLife and CHEO postings have never once been submitted.

This module reuses his own account on the employer's ATS (not a job board, so
there is no ban risk), walks the wizard, answers every question through
application_prefill's engine, and submits ONLY when every required answer is one
it could fill honestly. Anything else — a question that needs his real input, a
saved session that's expired, a step it can't recognize — stops and hands back
`prefilled_pending_review` so job_agent.py emails him the package instead. A
skipped submission is always safer than a fabricated answer sitting permanently
in an employer's ATS under his name.

Scope guard (deliberate, per plan §7): only tenants flagged `auto_apply: true` in
known_workday.json are ever submitted for. GoodLife is seeded true; everything
else — CHEO included — gets the prefill package until the wizard is proven on one
real GoodLife posting. Flipping a tenant on is then a one-line JSON change.

Sign-in is never automated: his email and password would have to live in this
code or in .env to do that, and he asked not to have his password touch this
codebase at all. Instead workday_session.py opens a real, visible browser once
so he can log in himself, and saves only the resulting session cookies
(Playwright storage_state). This module loads that saved session per tenant; a
tenant with no saved session, or one whose session has expired, degrades to the
prefill package with a reason telling him which command re-establishes it.
"""

import re
import time
from typing import Optional

from playwright.sync_api import sync_playwright

import workday_session
from agent_config import is_review_only
from application_prefill import answer_fields
from form_schema import extract_dom_fields, open_combobox_listbox
from run_history import record_run
from web_applier import (
    ACTION_TIMEOUT_MS,
    CONFIRMATION_PATTERN,
    NAV_TIMEOUT_MS,
    SCREENSHOT_DIR,
    _fill,
    _nearby_label_text,
    _upload,
)
from workday_source import load_known_workday

# Workday's wizard is slower than a plain form post — each "Save and Continue"
# re-renders the whole step server-side.
STEP_SETTLE_MS = 2500
# How long a wizard step is allowed to take to paint, and how often to look.
STEP_RENDER_TIMEOUT_MS = 20000
STEP_POLL_MS = 1000
MAX_WIZARD_STEPS = 8

# Workday ships stable `data-automation-id` attributes across every tenant; they
# are the only reliable selectors here, since the visible labels are per-tenant
# configurable. Each is paired with a visible-text fallback below in case a
# tenant has customized the control.
#
# _SIGN_IN_LINK is also the liveness check for a saved session: an anonymous
# visitor sees it, a signed-in candidate doesn't. Defined in workday_session so
# the capture step judges "signed in" by exactly the same rule this run does.
_SIGN_IN_LINK = workday_session.SIGN_IN_LINK
# Two ids, because tenants disagree. goodlifefitness.wd3 renders its Save and
# Continue as pageFooterNextButton and has no bottom-navigation-next-button at
# all — a live run waited NAV_TIMEOUT_MS on every step for a control that was
# never going to appear, then reported the wizard had no forward control.
_NEXT_BUTTON = ("[data-automation-id='pageFooterNextButton'], "
                "[data-automation-id='bottom-navigation-next-button']")
_RESUME_UPLOAD = (
    "input[data-automation-id='file-upload-input-ref'], "
    "[data-automation-id='quickApplyResumeUpload'] input[type='file'], "
    "input[type='file']"
)
# The "Start Your Application" interstitial (Autofill with Resume / Apply
# Manually / Use My Last Application) renders after the header/footer — its
# automation-id can vary by tenant build, so this also matches on visible
# text via _click_either's fallback rather than relying on the id alone.
_APPLY_LANDING_BUTTONS = (
    "[data-automation-id='applyManually'], "
    "[data-automation-id='autofillWithResume'], "
    "[data-automation-id='useMyLastApplication']"
)

# A step whose forward control reads like this is the last one — clicking it IS
# the submission, so every required answer must be honest before it's touched.
_SUBMIT_TEXT = re.compile(r"^\s*submit\s*$", re.I)

# Workday routes its success announcements through the same role=alert channel
# as its validation failures — see _step_errors.
_SUCCESS_ALERT = re.compile(
    r"successfully (uploaded|saved|added|removed|deleted)|"
    r"upload (complete|successful)", re.I)

# The final gate on a Workday application is not a question — it is his
# signature. GoodLife's reads "Yes I have read and understand the terms and
# conditions for submitting an application", sitting under "I verify that all
# statements made in my application for employment are true and correct".
#
# No rule ticks this, ever: attesting that his application is true is his to
# do, not the agent's. But the run has to say so accurately. Reporting it as a
# question that "needs your real answer" sends him back through five wizard
# steps looking for a blank he will not find, when in fact the form is finished
# and waiting on one click.
#
# Deliberately narrow on two axes, because widening either one would let the
# agent tell him a genuine unanswered question is "just a box to tick":
#   * kind must be checkbox. A checkbox is a signature control. Tenants ask
#     "Do you agree to a background check?" as a dropdown — consent wording,
#     but a fact about him, and still a real question.
#   * the label must carry attestation wording. "I have a preferred name" is a
#     checkbox and is not a signature.
_ATTESTATION_TEXT = re.compile(
    r"terms and conditions|privacy (policy|notice)|"
    r"\bi (have read|certify|verify|acknowledge|declare|consent|agree)\b|"
    r"read and (understand|accept)|"
    r"statements? .{0,40}(true|correct)", re.I)


def _is_signature(blocker: dict) -> bool:
    """One required checkbox whose label reads as an attestation."""
    if str(blocker.get("kind") or "").strip().lower() != "checkbox":
        return False
    return bool(_ATTESTATION_TEXT.search(str(blocker.get("label") or "")))


def _only_needs_signature(blocked_by: list) -> bool:
    """True when the run answered every actual question and the sole thing left
    is him signing. An empty list is not a signature hold — nothing is blocked,
    so the caller's earlier branches own that case."""
    return bool(blocked_by) and all(_is_signature(b) for b in blocked_by)


def _signature_reason(blocked_by: list) -> str:
    labels = "; ".join(b["label"] for b in blocked_by[:3])
    return ("every answer on this application is filled in — it needs your "
            "signature to go: open the link, tick \"{}\" and click Submit"
            .format(labels))


def _outcome(status: str, apply_url: str, form_fields: Optional[list] = None,
             screenshot: Optional[str] = None, reason: str = "") -> dict:
    """Same shape web_applier.apply_on_website returns, so job_agent.py's existing
    branches handle a Workday result without a single new code path."""
    return {
        "status": status,
        "ats": "workday",
        "screenshot": screenshot,
        "apply_url": apply_url,
        "form_fields": list(form_fields or []),
        "reason": reason,
    }


def tenant_for_job(job: dict) -> Optional[dict]:
    """The known_workday.json entry this job belongs to, or None if it isn't from
    a registered tenant. Matches on the slug the source recorded at fetch time,
    falling back to the slug in the URL for jobs that arrived some other way."""
    tenant = (job.get("workday_tenant") or "").lower()
    if not tenant:
        m = re.search(r"https?://([a-z0-9\-]+)\.wd\d+\.myworkdayjobs\.com",
                      job.get("url", "") or "", re.I)
        if not m:
            return None
        tenant = m.group(1).lower()

    for entry in load_known_workday().get("tenants", []):
        if (entry.get("tenant") or "").lower() == tenant:
            return entry
    return None


def auto_apply_allowed(job: dict) -> bool:
    """True only for tenants explicitly approved for unattended submission. An
    unregistered tenant is never approved — the registry is the whole guard."""
    entry = tenant_for_job(job)
    return bool(entry and entry.get("auto_apply"))


def _body_text(page) -> str:
    try:
        return page.locator("body").inner_text(timeout=ACTION_TIMEOUT_MS) or ""
    except Exception:
        return ""


def _click(page, selector: str) -> bool:
    try:
        el = page.locator(selector).first
        if el.count() and el.is_visible(timeout=ACTION_TIMEOUT_MS):
            el.click(timeout=ACTION_TIMEOUT_MS)
            return True
    except Exception:
        pass
    return False


def _click_text(page, pattern: str) -> bool:
    """Fallback for tenants that have customized a control away from its usual
    automation id — match the button or link by its visible text instead."""
    for role in ("button", "link"):
        try:
            el = page.get_by_role(role, name=re.compile(pattern, re.I)).first
            if el.count():
                el.click(timeout=ACTION_TIMEOUT_MS)
                return True
        except Exception:
            continue
    return False


def _click_either(page, selector: str, text_pattern: str) -> bool:
    return _click(page, selector) or _click_text(page, text_pattern)


def _screenshot(page, job_id: str) -> Optional[str]:
    try:
        path = str(SCREENSHOT_DIR / "{}-workday.png".format(job_id))
        page.screenshot(path=path, full_page=True)
        return path
    except Exception:
        return None


def _is_authenticated(page) -> bool:
    """True once Workday is treating this browser as a signed-in candidate
    rather than an anonymous visitor.

    The logic lives in workday_session.is_signed_in because the capture and the
    run that consumes its file have to agree: a capture that judged sign-in
    differently is how, on Sep 12, a logged-out browser was saved as a good
    session and reported "Signed in" to him. Both sides now paint first, read
    Workday's own Sign In control second, and fail closed.

    This side does not need the tenant-host check the capture side adds — the
    applier drove the browser here itself and knows what it loaded.
    """
    return workday_session.is_signed_in(page)


def _answerable(fields: list) -> list:
    """The fields answer_fields() will actually return an answer for, in the same
    order — it skips blank-label fields, so this is what zips 1:1 with its output.
    The answer dicts carry no selector of their own, which is why the pairing
    matters: the field is the only thing that knows where to type the answer."""
    return [f for f in fields if (f.get("label") or "").strip()]


def _fill_current_step(page, job: dict, cover_letter: str, resume_pdf: str) -> tuple:
    """Answer every field Workday is showing on this wizard step.

    Returns (fields, unanswered_required). form_schema does the reading, so the
    questions on the prefill sheet are literally the ones on the form.
    """
    # extract_dom_fields queries the DOM synchronously with no wait of its own.
    # Each wizard step re-renders its fields client-side after the step
    # transition (the "Apply Manually" click, or a prior _advance()), and that
    # render isn't done by the time the fixed STEP_SETTLE_MS sleep elapses
    # often enough to matter — same race as the landing-page button, one step
    # later. _NEXT_BUTTON is present on every step (including Submit), so its
    # visibility is a reliable "this step has finished rendering" signal.
    try:
        page.wait_for_selector(_NEXT_BUTTON, state="visible", timeout=NAV_TIMEOUT_MS)
    except Exception:
        pass

    try:
        fields = extract_dom_fields(page, "workday")
    except Exception:
        fields = []
    if not fields:
        return [], []

    pairs = list(zip(_answerable(fields), answer_fields(fields, job, cover_letter, resume_pdf)))
    unanswered_required = [a for _f, a in pairs if a["needs_input"] and a["required"]]

    for field, answer in pairs:
        if answer["needs_input"] or field.get("kind") == "file":
            continue
        name = field.get("name") or ""
        if not name:
            continue

        # Already showing the answer — Workday pre-filled it from his own
        # profile. Re-clicking a combobox only risks knocking it off a value
        # that was right to begin with.
        current = str(field.get("value") or "").strip()
        if current and current.lower() == str(answer["answer"]).strip().lower():
            continue

        selector = "[name='{0}'], #{0}, [data-automation-id='{0}']".format(name)
        if field.get("kind") == "select":
            try:
                page.locator(selector).first.select_option(
                    label=answer["answer"], timeout=ACTION_TIMEOUT_MS)
                continue
            except Exception:
                pass
        elif field.get("kind") == "radio":
            _check_radio_option(page, name, answer["answer"])
            continue
        elif field.get("kind") == "workday_select":
            # A dropdown that refuses the click leaves a required question
            # blank. Silently moving on used to hand that to Workday's own
            # validation, which just refuses Next with no trace of why — treat
            # it as unanswered so the run reports it instead of stalling.
            if not _select_combobox_option(page, name, answer["answer"]):
                if answer["required"]:
                    unanswered_required.append(dict(
                        answer,
                        needs_input=True,
                        hint="Couldn't set this dropdown to '{}' — set it yourself.".format(
                            answer["answer"]),
                    ))
            continue
        _fill(page, selector, answer["answer"])

    return fields, unanswered_required


def _check_radio_option(page, name: str, value: str) -> bool:
    """A radio group's options all share one `name`, and Playwright's
    .fill() (what the generic _fill() falls back to) silently no-ops on
    type=radio inputs — it targets .first, which can't be steered toward
    "Yes" vs "No" anyway. Find the specific option whose own label text
    matches the answer and .check() it, which is the correct Playwright
    call for radio/checkbox inputs."""
    if not value:
        return False
    try:
        options = page.locator(f"input[type='radio'][name='{name}']").all()
    except Exception:
        options = []
    target = value.strip().lower()
    for opt in options:
        try:
            label_text = (_nearby_label_text(page, opt) or "").strip().lower()
        except Exception:
            continue
        if label_text == target or label_text.startswith(target):
            try:
                opt.check(timeout=ACTION_TIMEOUT_MS)
                return True
            except Exception:
                continue
    return False


def _select_combobox_option(page, name: str, value: str) -> bool:
    """Workday's "Select One" fields are a <button aria-haspopup="listbox">,
    not a native <select> — .select_option() and .fill() both no-op on them.
    Click the button by name to open the listbox, find the option whose text
    exactly matches the answer (already chosen from the field's real,
    extracted options by application_prefill.match_option — never invented
    here), and click it. Mirrors _check_radio_option's pattern for the same
    reason: this widget needs a real click, not a value assignment.

    Scoped through open_combobox_listbox so the options clicked here are the
    ones this button actually owns — see that function for what reading a
    stale listbox did to every field on the step."""
    if not value:
        return False

    target = value.strip().lower()

    # Workday drops the occasional opening click. Measured on
    # goodlifefitness.wd3: the "trusted with confidential information"
    # question lost its first click on two consecutive runs while the three
    # other dropdowns on the same step opened first time. It was not a toggle
    # of an already-open widget (aria-expanded was unset before the click) and
    # the click did not throw — the listbox simply never appeared, so the poll
    # in open_combobox_listbox spent its 2s and the step reported a required
    # question as one he had to answer by hand. Clicking again immediately
    # afterwards opened it and set the answer in 0.07s, so one retry is the
    # whole fix; looping further would just be guessing at a flake we have
    # never seen twice on the same field.
    for _attempt in (1, 2):
        try:
            button = page.locator(f"button[name='{name}']").first
            button.click(timeout=ACTION_TIMEOUT_MS)
        except Exception:
            return False

        listbox = open_combobox_listbox(page, button)
        if listbox is not None:
            try:
                listbox.wait_for(state="visible", timeout=ACTION_TIMEOUT_MS)
                for opt in listbox.locator("li[role='option']").all():
                    try:
                        text = (opt.text_content(timeout=ACTION_TIMEOUT_MS) or "").strip().lower()
                    except Exception:
                        continue
                    if text == target:
                        opt.click(timeout=ACTION_TIMEOUT_MS)
                        return True
            except Exception:
                pass

        # Either the listbox never opened, or it opened without the answer in
        # it. Escape either way, so the retry starts from a closed widget
        # instead of clicking a half-open one shut.
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass

    return False


def _step_controls(page) -> list:
    """Identify the form controls the current step is showing.

    Deliberately cheap and label-free — ids and automation-ids only — because
    this runs twice per advance purely to answer "is this still the same step?".

    Visibility is not a refinement here, it is the whole point. Workday hides the
    step you just left rather than unmounting it: measured on goodlifefitness.wd3,
    My Experience's Select files / Add / delete-file controls were all still in
    the document after the wizard had moved on to Application Questions, just
    with no boxes. Counting them made the control list identical either side of a
    successful advance, which is how _advance came to report a step it had in
    fact completed as one the wizard refused to leave.
    """
    try:
        return page.evaluate(
            "() => Array.from(document.querySelectorAll("
            "'input, select, textarea, button[aria-haspopup=\"listbox\"]'))"
            ".filter(e => !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length))"
            ".map(e => e.id || e.getAttribute('data-automation-id') || e.name || e.type || '')"
        ) or []
    except Exception:
        return []


def _active_step(page) -> str:
    """Which step Workday's own progress bar says is current, e.g.
    "current step 3 of 5 Application Questions".

    This is the only unambiguous answer to "did the wizard move?", and it is
    plain tenant-neutral Workday markup rather than anything GoodLife configured.
    Comparing form controls was always a proxy for it, and a poor one: a step can
    re-render after a validation failure with a different control list, and — as
    the hidden leftovers in _step_controls show — two genuinely different steps
    can present the same one.
    """
    try:
        el = page.locator("[data-automation-id='progressBarActiveStep']").first
        if el.count():
            return " ".join((el.inner_text(timeout=ACTION_TIMEOUT_MS) or "").split())
    except Exception:
        pass
    return ""


def _forward_enabled(page) -> bool:
    """Whether the footer's forward button is currently clickable.

    Workday disables it while a step is fetching itself, so this doubles as a
    "has this step finished loading" signal — observed live: Save and Continue
    came back disabled the moment Application Questions began loading, and the
    content area was a spinner for as long as it stayed that way.
    """
    try:
        el = page.locator(_NEXT_BUTTON).first
        return bool(el.count()) and el.is_enabled(timeout=ACTION_TIMEOUT_MS)
    except Exception:
        return False


def _step_errors(page) -> list:
    """Workday's own validation messages for the current step.

    When the wizard refuses to move, the page is already displaying exactly
    what is wrong ("Errors Found", then one line per unanswered question). The
    run used to discard that and report the generic "stopped before reaching a
    Submit step", which told him nothing he could act on.

    role=alert is swept last and is the loose one: Workday announces successes
    through it too, so the live My Experience step offered "resume_....pdf
    successfully uploaded" as its only "error". Left in, that lands in the reason
    line of an email telling him why his application stopped.
    """
    messages = []
    for selector in ("[data-automation-id='errorMessage']",
                     "[data-automation-id='validationErrorLabel']",
                     "[role='alert']"):
        try:
            for node in page.locator(selector).all():
                text = " ".join((node.inner_text(timeout=ACTION_TIMEOUT_MS) or "").split())
                if text and text not in messages and not _SUCCESS_ALERT.search(text):
                    messages.append(text)
        except Exception:
            continue

    # The selectors above found nothing on the step that actually refused to
    # move. Measured on goodlifefitness.wd3: a rejected Save and Continue drew
    # an "Errors Found" panel over four <button> elements reading
    # "Error - <question>", plus one inline "Error: The field <question> is
    # required and must have a value." beneath each field. None of them carry
    # an automation id, a role=alert, or any other handle — so the run reported
    # the generic "stopped before reaching a Submit step" while the page was
    # listing, by name, every question that had stopped it. Text is all Workday
    # gives here, so text is what this matches: innermost nodes only, or every
    # wrapper around a message would report it again.
    try:
        found = page.evaluate(
            "() => Array.from(document.querySelectorAll('button, a, div, span, p'))"
            ".filter(e => !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length))"
            ".filter(e => /^Error\\s*[-:\\u2013\\u2014]/.test((e.textContent || '').trim()))"
            ".filter(e => !Array.from(e.children).some("
            "c => /^Error\\s*[-:\\u2013\\u2014]/.test((c.textContent || '').trim())))"
            ".map(e => (e.textContent || '').trim())"
        ) or []
    except Exception:
        found = []
    for text in found:
        text = " ".join(text.split())
        if text and text not in messages and not _SUCCESS_ALERT.search(text):
            messages.append(text)
    return messages


def _settle(page) -> list:
    """Wait until the step has finished painting, and return its controls.

    Workday's apply wizard is a single-page app: on the live GoodLife tenant the
    content area needs four to twelve seconds to render, while a fixed
    STEP_SETTLE_MS sleep gave it 2.5. A step read that early looks broken rather
    than slow — My Experience came back holding one input and no forward
    control, and the run reported the wizard had stopped. Polling the step's own
    controls and stopping when two consecutive readings agree costs about two
    seconds on a step that is already up and waits as long as a slow one needs.

    Agreeing twice is necessary but not sufficient: a step still fetching itself
    holds a stable list for as long as the spinner is up, so on its own that test
    called Application Questions settled after 2.0s while it was blank. Workday
    disables the forward button for exactly that interval, so requiring it to be
    live again is what separates "stable because it is finished" from "stable
    because it has not started".
    """
    deadline = time.time() + STEP_RENDER_TIMEOUT_MS / 1000.0
    last = None
    while time.time() < deadline:
        page.wait_for_timeout(STEP_POLL_MS)
        now = _step_controls(page)
        if now and now == last and _forward_enabled(page):
            return now
        last = now
    return last or []


def _advance(page) -> bool:
    """Move the wizard on one step. False means it did not move.

    Clicking is not moving. A step that fails Workday's validation re-renders
    itself, and reporting that click as progress is what let a run spin on the
    Application Questions step until MAX_WIZARD_STEPS ran out and then blame a
    missing Submit step.

    Workday's progress bar answers this directly, so ask it first. Comparing form
    controls was the original test and is kept only for a tenant that renders no
    progress bar — it is the weaker measure, and on Sep 12 it was wrong in the
    expensive direction: it called a completed My Experience step a stuck one and
    stopped the walk one step short of the Application Questions we were trying
    to read. Wrong-and-stopped is still the right way to be wrong here, because
    the alternative is a run that believes it is somewhere it is not while a
    Submit button sits under its cursor.
    """
    before_step = _active_step(page)
    before = _step_controls(page)
    if not _click_either(page, _NEXT_BUTTON, r"save and continue|continue|next"):
        return False
    after = _settle(page)
    if before_step:
        return _active_step(page) != before_step
    if before and after == before:
        return False
    return True


def _next_button_is_submit(page) -> bool:
    try:
        el = page.locator(_NEXT_BUTTON).first
        if el.count():
            text = el.inner_text(timeout=ACTION_TIMEOUT_MS) or ""
            return bool(_SUBMIT_TEXT.search(text.strip()))
    except Exception:
        pass
    return False


def apply_on_workday(job: dict, cover_letter: str, resume_pdf: str, headless: bool = True) -> dict:
    """Logging wrapper, mirroring web_applier.apply_on_website."""
    start = time.time()
    result = _apply_on_workday(job, cover_letter, resume_pdf, headless=headless)
    record_run(
        "Workday Auto-Apply",
        "{} @ {}".format(job.get("title", "?"), job.get("company", "?")),
        {"submitted": "Success", "submit_unconfirmed": "Failed", "failed": "Failed"}.get(
            result.get("status"), "Skipped"),
        "{}: {}".format(result.get("status"), result.get("reason") or "ok"),
        duration_ms=int((time.time() - start) * 1000),
    )
    return result


def _apply_on_workday(job: dict, cover_letter: str, resume_pdf: str, headless: bool = True) -> dict:
    apply_url = job.get("url", "") or ""
    job_id = job.get("id", "workday")

    if not auto_apply_allowed(job):
        entry = tenant_for_job(job)
        who = entry["company_name"] if entry else "this Workday tenant"
        return _outcome(
            "prefilled_pending_review", apply_url,
            reason="{} is not approved for unattended Workday submission yet".format(who),
        )

    entry = tenant_for_job(job)
    tenant = entry["tenant"] if entry else None
    if not tenant or not workday_session.session_exists(tenant):
        who = entry["company_name"] if entry else "this tenant"
        return _outcome(
            "prefilled_pending_review", apply_url,
            reason="no saved Workday session for {} — run `python3 workday_session.py {}` "
                   "once to sign in yourself, then automated runs can reuse it".format(
                       who, tenant or "<tenant>"),
        )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = workday_session.new_context_with_session(browser, tenant)
            page = context.new_page()
            page.set_default_timeout(NAV_TIMEOUT_MS)
            page.goto(apply_url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)

            # The header/footer render immediately on domcontentloaded, but the
            # landing buttons are fetched client-side afterwards. A fixed sleep
            # here races that fetch and loses often enough to matter — wait for
            # the actual control instead of a guessed delay. The wizard's own
            # progress bar counts as an arrival too: a candidate who already has
            # a draft never gets a landing page at all, so waiting only on its
            # buttons burns the whole timeout before discovering a wizard that
            # painted seconds earlier.
            try:
                page.wait_for_selector(
                    _APPLY_LANDING_BUTTONS
                    + ", [data-automation-id='progressBarActiveStep']",
                    state="visible", timeout=NAV_TIMEOUT_MS)
            except Exception:
                pass

            # Some tenants offer "Autofill with Resume" alongside "Apply Manually".
            # Manual is the one whose fields this engine can read and answer;
            # autofill guesses from the PDF and can silently mangle them.
            clicked_manual = _click_either(
                page, "[data-automation-id='applyManually']", r"apply manually")
            page.wait_for_timeout(STEP_SETTLE_MS)

            # Workday drops a candidate who already has a draft application on
            # this posting straight into the wizard and renders no landing page,
            # so there is no "Apply Manually" to click and its absence is the
            # expected state rather than a failure. Measured on
            # goodlifefitness.wd3: the first walk after a fresh sign-in opened
            # directly on "current step 1 of 5 My Information", and the run
            # bailed here blaming a loading race while the wizard sat fully
            # painted behind it. The progress bar is the proof we are inside.
            already_in_wizard = bool(_active_step(page))

            if not clicked_manual and not already_in_wizard:
                shot = _screenshot(page, job_id)
                form_url = page.url
                browser.close()
                return _outcome(
                    "prefilled_pending_review", form_url, screenshot=shot,
                    reason="couldn't find/click \"Apply Manually\" on {}'s Workday "
                           "landing page — it may not have finished loading in time, "
                           "or this posting's apply flow differs from the usual "
                           "one".format(entry["company_name"]),
                )

            if not _is_authenticated(page):
                shot = _screenshot(page, job_id)
                form_url = page.url
                browser.close()
                return _outcome(
                    "prefilled_pending_review", form_url, screenshot=shot,
                    reason="saved Workday session for {} looks expired — run "
                           "`python3 workday_session.py {}` again to refresh it".format(
                               entry["company_name"], tenant),
                )

            all_fields = []
            blocked_by = []
            resume_uploaded = False
            submitted = False
            attempted_submit = False
            review_only_hold = False
            stalled_on = []

            for _step in range(MAX_WIZARD_STEPS):
                # The resume input only exists on the My Experience step, so try
                # every step until one takes it.
                if not resume_uploaded:
                    resume_uploaded = _upload(page, _RESUME_UPLOAD, resume_pdf)
                    if resume_uploaded:
                        page.wait_for_timeout(STEP_SETTLE_MS)

                fields, unanswered = _fill_current_step(page, job, cover_letter, resume_pdf)
                all_fields.extend(fields)
                blocked_by.extend(unanswered)

                # The gate this whole module is built around. A required question
                # the engine wouldn't invent an answer for stops the run here —
                # and there's no point walking further, since Workday won't let a
                # required field go unanswered anyway.
                if blocked_by:
                    break

                if _next_button_is_submit(page):
                    # Mirrors web_applier._maybe_submit's review-only guard — checked
                    # fresh here (not cached) since the flag can flip between runs.
                    # Without this, reaching Submit with review_only ON would still
                    # click it: nothing else in this wizard checks the flag.
                    if is_review_only():
                        review_only_hold = True
                        break
                    attempted_submit = True
                    _advance(page)
                    submitted = bool(CONFIRMATION_PATTERN.search(_body_text(page)))
                    break

                if not _advance(page):
                    # Either there was no forward control, or Workday refused to
                    # move. In the second case the page is already showing why,
                    # and on this tenant the why is usually a question that did
                    # not exist when the step was read: answering "Yes" to
                    # GoodLife's confidential-information question reveals a
                    # required "rate 1-10" follow-up, and Workday's validation
                    # pass re-renders the questionnaire, which drops dropdown
                    # values it had not committed (measured: two of five
                    # dropdowns were back to "Select One" after the refusal,
                    # having been set successfully minutes earlier).
                    #
                    # Both are first-pass-only problems, so read the step again
                    # and answer what is in front of us now. The gate is
                    # untouched — a required question the engine still cannot
                    # answer honestly stops the run here exactly as before.
                    fields, unanswered = _fill_current_step(
                        page, job, cover_letter, resume_pdf)
                    seen_labels = set(f.get("label") for f in all_fields)
                    all_fields.extend(
                        f for f in fields if f.get("label") not in seen_labels)
                    if unanswered:
                        blocked_by.extend(unanswered)
                        break
                    if not _advance(page):
                        stalled_on = _step_errors(page)
                        break

            shot = _screenshot(page, job_id)
            form_url = page.url
            # Save the rolling cookies back so the next run starts from this
            # run's session rather than from the snapshot taken when he last
            # signed in. Guarded on still being authenticated: writing a
            # logged-out state over a good one would cost him a sign-in.
            if _is_authenticated(page):
                workday_session.refresh_session(context, tenant)
            browser.close()

            if submitted:
                return _outcome("submitted", form_url, all_fields, shot)
            if review_only_hold:
                return _outcome(
                    "prefilled_pending_review", form_url, all_fields, shot,
                    reason="reached the Submit step with every required answer ready, but "
                           "review-only mode held it back — run `python3 agent_config.py off` "
                           "to let this submit for real",
                )
            if attempted_submit:
                return _outcome(
                    "submit_unconfirmed", form_url, all_fields, shot,
                    reason="Submit clicked but Workday showed no confirmation text",
                )
            if blocked_by:
                # Same status either way, so the digest, tracker and
                # seen_jobs keys are untouched — only the reason he reads
                # changes, and only when nothing is actually unanswered.
                if _only_needs_signature(blocked_by):
                    return _outcome(
                        "prefilled_pending_review", form_url, all_fields, shot,
                        reason=_signature_reason(blocked_by),
                    )
                labels = "; ".join(a["label"] for a in blocked_by[:3])
                return _outcome(
                    "prefilled_pending_review", form_url, all_fields, shot,
                    reason="stopped before Submit — {} required question(s) need your real "
                           "answer: {}".format(len(blocked_by), labels),
                )
            if stalled_on:
                return _outcome(
                    "prefilled_pending_review", form_url, all_fields, shot,
                    reason="the wizard wouldn't move past this step — Workday reported: "
                           "{}".format("; ".join(stalled_on[:3])),
                )
            return _outcome(
                "prefilled_pending_review", form_url, all_fields, shot,
                reason="the wizard stopped before reaching a Submit step",
            )

    except Exception as e:
        print("[workday_applier] Failed on {}: {}".format(apply_url, e))
        return _outcome("failed", apply_url, reason=str(e))


if __name__ == "__main__":
    # Read-only check: which registered tenants are approved, and does each
    # have a saved sign-in session? Never opens a browser, never applies to
    # anything.
    for _entry in load_known_workday().get("tenants", []):
        _flag = "AUTO-APPLY" if _entry.get("auto_apply") else "package only"
        _session = "session saved" if workday_session.session_exists(_entry["tenant"]) else "NO SESSION"
        print("  [{:>12}] {} ({}.{}) — {}".format(
            _flag, _entry["company_name"], _entry["tenant"], _entry["wd_host"], _session))
