"""Extract application-form questions from a job's ATS page.

Greenhouse: structured, straight from the public API (`?questions=true`) keyed
by board token + job id parsed from the posting URL — most reliable, since it
returns real required flags and option values instead of guessing from HTML.
Lever / generic / Workday: DOM extraction on whichever frame actually hosts
the form, reusing web_applier's own frame-detection and label-reading helpers
so this module never re-implements ATS quirks web_applier.py already knows.

Each field comes back as {label, kind, required, options, name}. kind is one
of: text, email, tel, textarea, select, radio, checkbox, file, date.
"""

import re
from typing import Optional
from urllib.parse import urlparse

import requests

from web_applier import _form_frame, _nearby_label_text

GREENHOUSE_TIMEOUT = 15

_GREENHOUSE_JOB_ID_RE = re.compile(r"/jobs/(\d+)")

# Greenhouse reports a question's type inside question["fields"][i]["type"], not on
# the question itself, and its live values are these. The flat keys below them
# ("single_select", "yes_no", "attachment") are kept because the fixtures and older
# boards use them, but no live board has been seen to emit them: reading only the
# flat shape is why every question on every real posting came back kind "text",
# which meant the resume was never attached and select questions were answered as
# free text with no option list to match against.
_GREENHOUSE_TYPE_MAP = {
    "input_text": "text",
    "input_file": "file",
    "textarea": "textarea",
    "multi_value_single_select": "select",
    "multi_value_multi_select": "checkbox",
    "single_select": "select",
    "multi_select": "checkbox",
    "yes_no": "select",
    "attachment": "file",
}

_KIND_BY_INPUT_TYPE = {
    "email": "email",
    "tel": "tel",
    "date": "date",
    "checkbox": "checkbox",
    "radio": "radio",
}

_SKIP_INPUT_TYPES = {"submit", "button", "hidden", "image", "reset"}

# Workday renders "Select One" questions as a <button aria-haspopup="listbox">
# next to a hidden, id-less, name-less <input type="text"> — never a native
# <select>. Without this, extract_dom_fields matches only that hidden input,
# whose label/name both fall back to the button's own placeholder text
# ("Select One"), so the real question is never extracted or filled and
# Workday's own validation rejects every Next click. Confirmed against the
# live "How Did You Hear About Us?" / "Province or Territory" widgets.
_COMBOBOX_LISTBOX_SELECTOR = "ul[role='listbox']:has(li#select-one)"
_COMBOBOX_REQUIRED_TAIL_RE = re.compile(r"\s*Required\s*$", re.I)
_COMBOBOX_PLACEHOLDER = "select one"
# How long to wait for a combobox to report its own listbox id after a click.
_COMBOBOX_OPEN_TIMEOUT_MS = 2000
_COMBOBOX_POLL_MS = 100


def _greenhouse_board_token(url: str) -> Optional[str]:
    parts = [p for p in urlparse(url).path.split("/") if p]
    return parts[0] if parts else None


def _greenhouse_job_id(url: str) -> Optional[str]:
    m = _GREENHOUSE_JOB_ID_RE.search(url)
    return m.group(1) if m else None


def _greenhouse_field(question: dict) -> dict:
    """One question -> one pipeline field.

    A question can carry several fields: "Resume/CV" comes back as
    ["input_file", "textarea"] because Greenhouse accepts an upload or pasted text.
    A file is the better answer there (the pipeline always has a resume PDF and
    never has pasted resume text), so a file field wins when one is offered.
    """
    sub = [f for f in (question.get("fields") or []) if isinstance(f, dict)]
    kinds = [_GREENHOUSE_TYPE_MAP.get(str(f.get("type") or ""), "text") for f in sub]
    if "file" in kinds:
        chosen = sub[kinds.index("file")]
        kind = "file"
    elif sub:
        chosen, kind = sub[0], kinds[0]
    else:
        # Flat legacy/fixture shape: type and options sit on the question itself.
        chosen, kind = question, _GREENHOUSE_TYPE_MAP.get(str(question.get("type") or ""), "text")

    raw_options = chosen.get("values") or question.get("options") or []
    options = [str(o.get("label") or "").strip() for o in raw_options if isinstance(o, dict)]
    return {
        "label": str(question.get("label") or "").strip(),
        "kind": kind,
        "required": bool(question.get("required")),
        "options": [o for o in options if o],
        "name": str(chosen.get("name") or question.get("name") or question.get("label") or "").strip(),
    }


def extract_greenhouse_fields(url: str) -> Optional[list]:
    """Fetch every application question straight from Greenhouse's public API.

    Returns None (not []) on any failure — token/job-id parse miss, network
    error, bad JSON — so the caller falls back to DOM extraction instead of
    reporting a job as having zero questions when the lookup simply failed.
    """
    token = _greenhouse_board_token(url)
    job_id = _greenhouse_job_id(url)
    if not token or not job_id:
        return None

    api_url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs/{job_id}?questions=true"
    try:
        resp = requests.get(api_url, timeout=GREENHOUSE_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None

    fields = [_greenhouse_field(q) for q in (data.get("questions") or [])]
    return [f for f in fields if f["label"]]


def _is_required(el, label: str) -> bool:
    try:
        if el.get_attribute("required") is not None:
            return True
        if (el.get_attribute("aria-required") or "").lower() == "true":
            return True
    except Exception:
        pass
    return label.rstrip().endswith("*")


def _select_options(el) -> list:
    try:
        return [
            (o.text_content() or "").strip()
            for o in el.locator("option").all()
            if (o.text_content() or "").strip()
        ]
    except Exception:
        return []


def _radio_group_label(frame, el) -> str:
    """Radio groups: prefer the enclosing <fieldset> over the individual
    option's own nearby text. Workday wraps each Yes/No question in a
    <fieldset> holding the real question; the nearest div ancestor of any
    one radio input is just that option's own label (e.g. "Yes"), which is
    what _nearby_label_text's generic fallback would otherwise return."""
    try:
        fieldset = el.locator("xpath=ancestor::fieldset[1]").first
        if fieldset.count():
            text = (fieldset.inner_text() or "").strip()
            if text:
                return text
    except Exception:
        pass
    return _nearby_label_text(frame, el)


def _is_combobox_shadow_input(el) -> bool:
    """The hidden text <input> Workday renders beside a "Select One" button
    has no id or name of its own; without this check it gets mis-extracted
    as a bogus text field using the button's placeholder as both label and
    name. Detected by: no id/name, and a `button[aria-haspopup='listbox']`
    sibling in the same wrapping div."""
    try:
        if el.get_attribute("id") or el.get_attribute("name"):
            return False
        return bool(el.evaluate(
            "e => !!e.closest('div')?.querySelector(\"button[aria-haspopup='listbox']\")"
        ))
    except Exception:
        return False


def _combobox_label_from_aria(aria_label: str, current_value: str = "") -> tuple:
    """Workday's combobox aria-label encodes the field's *current value*, not a
    fixed placeholder: an empty one reads "{Question} Select One Required" but a
    filled one reads "{Question} Mobile Required". Stripping only "Select One"
    therefore leaves the value baked into the question text ("Phone Device Type
    Mobile Required"), which matches no answer rule, so a field the form had
    already filled correctly came back flagged as needing his input and stopped
    the whole run. Strip the trailing "Required", then whatever value the button
    is displaying — placeholder or real."""
    label = _COMBOBOX_REQUIRED_TAIL_RE.sub("", aria_label or "").strip()
    required = label != (aria_label or "").strip()

    tail = (current_value or "").strip() or _COMBOBOX_PLACEHOLDER
    if tail and label.lower().endswith(tail.lower()):
        label = label[: len(label) - len(tail)].strip()
    return label, required


def _combobox_current_value(button) -> str:
    """The value the combobox already shows, or "" when it's still unset.

    Workday pre-fills these from the candidate's own saved profile, so a real
    value here is his data, not a guess — worth keeping rather than overwriting.
    """
    try:
        shown = (button.text_content(timeout=2000) or "").strip()
    except Exception:
        return ""
    return "" if shown.lower() == _COMBOBOX_PLACEHOLDER else shown


def open_combobox_listbox(page, button):
    """Open a Workday combobox and return the listbox belonging to *that*
    button, or None if it can't be identified.

    Workday leaves a closed listbox in the DOM (verified live: 2 still present
    150ms after Escape), so `page.locator(...).first` resolves to whichever one
    is first in document order — usually the previous field's, which
    `wait_for(visible)` then accepts immediately. That silently shifted every
    field's options onto its neighbour: Country was offered the "how did you
    hear" list, Province or Territory got 250 country names, Phone Device Type
    got the 13 provinces. No answer could match, so no combobox was ever filled.

    An open button publishes its own listbox id in aria-controls (live:
    source->ysgw3 6 options, country->ysgw0 250, countryRegion->ysgw2 14,
    phoneType->ysgw5 3), so that is the only binding used here. Returning None
    when it's absent leaves the question for him to answer, which is the right
    failure: a wrong-but-real option submitted under his name is worse than a
    blank one.
    """
    waited = 0
    while waited <= _COMBOBOX_OPEN_TIMEOUT_MS:
        try:
            if (button.get_attribute("aria-expanded") or "").lower() == "true":
                listbox_id = (button.get_attribute("aria-controls") or "").strip()
                if listbox_id:
                    return page.locator("[id='{}']".format(listbox_id)).first
        except Exception:
            return None
        page.wait_for_timeout(_COMBOBOX_POLL_MS)
        waited += _COMBOBOX_POLL_MS
    return None


def _close_combobox(page) -> None:
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass


def _combobox_options(page, button) -> list:
    """Click the button open and read the real options out of its own listbox,
    skipping the disabled "Select One" placeholder."""
    try:
        button.click(timeout=2000)
    except Exception:
        return []

    options = []
    listbox = open_combobox_listbox(page, button)
    if listbox is not None:
        try:
            listbox.wait_for(state="visible", timeout=2000)
            for opt in listbox.locator("li[role='option']").all():
                try:
                    if (opt.get_attribute("aria-disabled", timeout=2000) or "").lower() == "true":
                        continue
                    text = (opt.text_content(timeout=2000) or "").strip()
                    if text:
                        options.append(text)
                except Exception:
                    continue
        except Exception:
            pass

    _close_combobox(page)
    return options


def _fieldset_question_text(el) -> str:
    """The question Workday keeps in the <legend> of the fieldset wrapping a control.

    Measured on goodlifefitness.wd3's Application Questions, every question on the
    step — dropdown and textarea alike — is a <fieldset> whose <legend> holds the
    full text, with the widget three styling <div>s below it. Asking for the
    nearest enclosing div-or-fieldset lands on one of those styling divs, which
    reads only "Select One" for a dropdown and nothing at all for an empty
    textarea. That is why all five required dropdowns came back as "Unidentified
    dropdown on this step" and why the step's three textareas — including the
    required availability one — were dropped from the schema entirely.

    Line breaks are deliberately left intact. The caller strips a trailing
    placeholder line ("Select One") and a trailing "Required" by looking at
    lines, so flattening the text here would smuggle that boilerplate into the
    question on any tenant whose legend wraps the widget rather than preceding
    it.
    """
    try:
        legend = el.locator("xpath=ancestor::fieldset[1]/legend[1]").first
        if legend.count():
            return (legend.inner_text() or "").strip()
    except Exception:
        pass
    return ""


def _combobox_question_text(frame, el, current_value: str) -> str:
    """Recover a combobox's question when its aria-label carries no question.

    My Information's widgets label themselves ("Country Select One Required"),
    but GoodLife's Application Questions put the question in the markup and
    leave the button reading only "Select One Required" — which the aria path
    strips down to nothing. The question is still on the page either side of
    the widget, so read it from aria-labelledby first (explicit) and from the
    wrapping container second, then take off the same trailing boilerplate.
    """
    raw = ""
    try:
        ids = (el.get_attribute("aria-labelledby") or "").split()
    except Exception:
        ids = []
    for label_id in ids:
        try:
            node = frame.locator("[id='{}']".format(label_id)).first
            if node.count():
                raw = " ".join((node.inner_text() or "").split())
                if raw:
                    break
        except Exception:
            continue

    if not raw:
        raw = _fieldset_question_text(el)

    if not raw:
        try:
            container = el.locator(
                "xpath=ancestor::*[self::div or self::fieldset][1]").first
            if container.count():
                raw = (container.inner_text() or "")[:300]
        except Exception:
            raw = ""

    # The container text includes the widget's own visible value on its last
    # line ("...work in Canada?*\nSelect One"); drop it so the question is left.
    lines = [ln.strip() for ln in (raw or "").splitlines() if ln.strip()]
    tail = (current_value or "").strip() or _COMBOBOX_PLACEHOLDER
    lines = [ln for ln in lines if ln.lower() != tail.lower()]
    text = " ".join(" ".join(lines).split())
    return _COMBOBOX_REQUIRED_TAIL_RE.sub("", text).strip()


def _combobox_field_from_button(page, el, frame=None) -> Optional[dict]:
    try:
        aria_label = el.get_attribute("aria-label") or ""
    except Exception:
        aria_label = ""

    current_value = _combobox_current_value(el)
    label, required = _combobox_label_from_aria(aria_label, current_value)

    if not label:
        label = _combobox_question_text(frame if frame is not None else page,
                                        el, current_value)
        required = required or label.rstrip().endswith("*")

    if not label:
        try:
            labelled_by = (el.get_attribute("aria-labelledby") or "").strip()
        except Exception:
            labelled_by = ""
        if not (aria_label or "").strip() and not labelled_by:
            # Not a question at all. Workday's own Settings menu is the same
            # button[aria-haspopup='listbox'] and sits in the chrome of every
            # step; the live GoodLife run reported it as a required unanswered
            # dropdown on both steps it reached. A real form question always
            # leaves at least one mark — an aria-label, even a boilerplate one,
            # or an aria-labelledby — so the absence of both is the line.
            return None

        # Deliberately a blocker rather than a drop. Returning None here is what
        # let a step of six required questions contribute nothing to the schema
        # and nothing to blocked_by, so the run walked past them reporting no
        # problem. A control nobody can name is one he has to answer himself.
        return {
            "label": "Unidentified dropdown on this step — open the form and answer it",
            "kind": "workday_select",
            "required": True,
            "options": [],
            "name": "",
            "value": current_value,
        }

    try:
        name = el.get_attribute("name") or el.get_attribute("id") or label
    except Exception:
        name = label

    return {
        "label": label[:300],
        "kind": "workday_select",
        "required": required,
        "options": _combobox_options(page, el),
        "name": name,
        "value": current_value,
    }


def _dom_field_from_element(frame, el) -> Optional[dict]:
    try:
        tag = (el.evaluate("e => e.tagName") or "").lower()
    except Exception:
        return None

    if tag == "textarea":
        kind = "textarea"
    elif tag == "select":
        kind = "select"
    elif tag == "input":
        try:
            input_type = (el.get_attribute("type") or "text").lower()
        except Exception:
            input_type = "text"
        if input_type in _SKIP_INPUT_TYPES or input_type == "radio":
            return None
        kind = _KIND_BY_INPUT_TYPE.get(input_type, "text")
    else:
        return None

    label = _nearby_label_text(frame, el)
    if not label:
        # An empty <textarea> gives its wrapping divs no text to read, so the
        # generic label walk returns nothing and the field would be dropped
        # without ever reaching blocked_by. Workday names it in the fieldset.
        label = " ".join(_fieldset_question_text(el).split())
    if not label:
        return None

    try:
        name = el.get_attribute("name") or el.get_attribute("id") or label
    except Exception:
        name = label

    return {
        "label": label.strip()[:300],
        "kind": kind,
        "required": _is_required(el, label),
        "options": _select_options(el) if kind == "select" else [],
        "name": name,
    }


def extract_dom_fields(page, ats: str) -> list:
    """Best-effort DOM extraction on whichever frame actually hosts the form —
    used for Lever, generic career-site forms, and Workday (once signed in).
    Radio groups collapse to one field per `name` so a Yes/No question isn't
    reported as two identical rows."""
    frame = _form_frame(page, ats)
    fields = []
    seen_radio_names = set()

    try:
        elements = frame.locator(
            "input, select, textarea, button[aria-haspopup='listbox']"
        ).all()
    except Exception:
        elements = []

    for el in elements:
        try:
            tag = (el.evaluate("e => e.tagName") or "").lower()
        except Exception:
            tag = ""

        if tag == "button":
            field = _combobox_field_from_button(page, el, frame=frame)
            if field:
                fields.append(field)
            continue

        try:
            input_type = (el.get_attribute("type") or "").lower()
        except Exception:
            input_type = ""

        if tag == "input" and input_type not in ("radio",) and _is_combobox_shadow_input(el):
            continue

        if input_type == "radio":
            try:
                name = el.get_attribute("name") or ""
            except Exception:
                name = ""
            if not name or name in seen_radio_names:
                continue
            seen_radio_names.add(name)
            label = _radio_group_label(frame, el)
            if not label:
                continue
            fields.append({
                "label": label.strip()[:300],
                "kind": "radio",
                "required": True,
                "options": [],
                "name": name,
            })
            continue

        field = _dom_field_from_element(frame, el)
        if field:
            fields.append(field)

    return fields


def extract_form_fields(page, ats: str) -> list:
    """Question extraction entry point. Greenhouse goes through the public API
    (real required flags and option values); everything else falls back to
    DOM extraction on the frame currently hosting the form."""
    if ats == "greenhouse":
        frame = _form_frame(page, ats)
        frame_url = getattr(frame, "url", "") or page.url
        fields = extract_greenhouse_fields(frame_url)
        if fields is not None:
            return fields
    return extract_dom_fields(page, ats)
