"""Auto-apply on company career-site forms via Playwright.

Fully autonomous (Sprout-mode): every form gets filled AND submitted when we
can do so honestly. Greenhouse/Lever use their known selectors; all other
sites get a best-effort fill, and if the page looks like a genuine application
form (a resume upload succeeded — the strongest signal), the submit button is
clicked too. A submit only counts as "submitted" when real confirmation text
appears afterwards; anything less is reported as unconfirmed so the digest
never claims an application that didn't happen. Only real profile/autofill
data is ever entered — unknown questions are left blank, never invented.

Job-board listing pages don't always embed the form — a "Quick Apply" / "Apply
Now" button often gates it behind a click (new tab, redirect, or in-page
reveal). When the listing page itself has no resume field, that button is
followed once and the same fill/submit logic re-runs on whatever it leads to.
"""

import re
import time
from pathlib import Path
from urllib.parse import urlparse

from fpdf import FPDF
from playwright.sync_api import sync_playwright

from autofill_sheet import SCREENING
from resume_data import PROFILE
from run_history import record_run

SCREENSHOT_DIR = Path(__file__).resolve().parent / "web_apply_screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

COVER_LETTER_DIR = Path(__file__).resolve().parent / "cover_letters"
COVER_LETTER_DIR.mkdir(exist_ok=True)

FIRST_NAME = "Sahawat"
LAST_NAME = "Nilwatcharamanee"

NAV_TIMEOUT_MS = 20000
ACTION_TIMEOUT_MS = 1500

# Boolean-style screening questions we can answer confidently everywhere.
# (label substring, must NOT also match) -> answer text to select/click
BOOLEAN_ANSWERS = [
    (re.compile(r"legally (authoriz|entitle)", re.I), "Yes"),
    (re.compile(r"require.*sponsorship", re.I), "No"),
    (re.compile(r"work(ing)? authoriz", re.I), "Yes"),
    (re.compile(r"driver'?s?\s*licen[cs]e", re.I), "Yes"),
    (re.compile(r"(located|based|residing).*ottawa", re.I), "Yes"),
]


def _safe_pdf_text(text: str) -> str:
    repl = {"–": "-", "—": "-", "‘": "'", "’": "'",
            "“": '"', "”": '"', "…": "..."}
    for uni, r in repl.items():
        text = text.replace(uni, r)
    return text.encode("latin-1", "replace").decode("latin-1")


def _cover_letter_pdf(job_id: str, cover_letter: str) -> str:
    """Render the cover letter to a one-page PDF for forms that require a file upload."""
    path = str(COVER_LETTER_DIR / f"cover_{job_id}.pdf")
    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10.5)
    pdf.multi_cell(0, 6, _safe_pdf_text(cover_letter))
    pdf.output(path)
    return path


def detect_ats(url: str) -> str:
    """First-pass guess from the job URL alone. Many companies white-label Greenhouse
    or Lever under their own domain and only embed it as an iframe once the page loads,
    so this is refined by _detect_ats_from_frames() after navigation."""
    host = urlparse(url).netloc.lower()
    if "greenhouse.io" in host:
        return "greenhouse"
    if "lever.co" in host:
        return "lever"
    if "myworkdayjobs.com" in host or ".workday.com" in host:
        return "workday"
    if "icims.com" in host:
        return "icims"
    return "generic"


def _detect_ats_from_frames(page, fallback: str) -> str:
    """Re-check ATS after the page has loaded by inspecting every frame's URL —
    the reliable signal for white-labeled Greenhouse/Lever embeds on custom domains."""
    for frame in page.frames:
        u = (frame.url or "").lower()
        if "greenhouse.io" in u:
            return "greenhouse"
        if "lever.co" in u:
            return "lever"
    return fallback


def _form_frame(page, ats: str):
    """Return the frame that actually hosts the application form fields."""
    for frame in page.frames:
        u = (frame.url or "").lower()
        if ats == "greenhouse" and "greenhouse.io" in u:
            return frame
        if ats == "lever" and "lever.co" in u:
            return frame
    return page.main_frame


def _fill(page, selector: str, value: str) -> bool:
    if not value:
        return False
    try:
        el = page.locator(selector).first
        if el.count() and el.is_visible(timeout=ACTION_TIMEOUT_MS):
            el.fill(value, timeout=ACTION_TIMEOUT_MS)
            return True
    except Exception:
        pass
    return False


def _upload(page, selector: str, filepath: str) -> bool:
    if not filepath or not Path(filepath).exists():
        return False
    try:
        el = page.locator(selector).first
        if el.count():
            el.set_input_files(filepath, timeout=ACTION_TIMEOUT_MS)
            return True
    except Exception:
        pass
    return False


def _answer_boolean_selects(page):
    """Best-effort: match <select> and radio-group questions against BOOLEAN_ANSWERS."""
    try:
        selects = page.locator("select").all()
    except Exception:
        selects = []
    for sel in selects:
        try:
            label_text = _nearby_label_text(page, sel)
            for pattern, answer in BOOLEAN_ANSWERS:
                if pattern.search(label_text):
                    sel.select_option(label=answer)
                    break
        except Exception:
            continue


def _nearby_label_text(page, element) -> str:
    """Grab the best-guess label text associated with a form field."""
    try:
        el_id = element.get_attribute("id")
        if el_id:
            label = page.locator(f"label[for='{el_id}']").first
            if label.count():
                return (label.inner_text() or "").strip()
    except Exception:
        pass
    try:
        aria = element.get_attribute("aria-label")
        if aria:
            return aria
    except Exception:
        pass
    try:
        # Fall back to the enclosing container's text (often includes the question)
        container = element.locator("xpath=ancestor::*[self::div or self::fieldset][1]").first
        if container.count():
            return (container.inner_text() or "")[:200]
    except Exception:
        pass
    return ""


CONFIRMATION_PATTERN = re.compile(
    r"application (has been |was )?(received|submitted)|thank you for applying|"
    r"successfully submitted|we('| ha)ve received your application",
    re.I,
)

# Cloudflare/bot-check interstitials on job aggregators (Glassdoor, ZipRecruiter, Indeed)
# block headless browsers outright. Filling never even reaches a real form on these pages,
# so they must never be reported as "prefilled" — that would tell the applicant a form is
# ready for review when nothing was actually filled in.
BOT_BLOCK_PATTERN = re.compile(
    r"performing security verification|checking your browser|just a moment|"
    r"verify you are human|humans only|access denied|are you a robot|"
    r"enable javascript and cookies to continue|additional verification required",
    re.I,
)


# Job-board "Quick Apply" / "Apply Now" buttons gate the real application form
# behind a click — the listing page itself never has a resume field. Anchored to
# match the whole button text so unrelated controls (e.g. "Apply Filter") never
# trigger a click by accident.
APPLY_BUTTON_PATTERN = re.compile(
    r"^\s*(quick\s*apply|apply\s*(now|today|here|online)?|apply for this (job|position|role))\s*!?\s*$",
    re.I,
)


def _find_apply_button(page):
    """Return the first visible 'Apply' control on the page, or None."""
    try:
        candidates = page.locator("a, button").all()
    except Exception:
        return None
    for el in candidates:
        try:
            if not el.is_visible(timeout=300):
                continue
            text = (el.inner_text(timeout=300) or "").strip()
            if APPLY_BUTTON_PATTERN.match(text):
                return el
        except Exception:
            continue
    return None


def _follow_apply_button(page, el):
    """Click an apply button and return whichever page should host the real form —
    a new tab if one opened, else the same page after it navigates or reveals a
    modal/SPA view in place."""
    try:
        with page.context.expect_page(timeout=5000) as new_page_info:
            el.click(timeout=ACTION_TIMEOUT_MS)
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT_MS)
        new_page.wait_for_timeout(1500)
        return new_page
    except Exception:
        pass
    try:
        page.wait_for_load_state("domcontentloaded", timeout=3000)
    except Exception:
        pass
    page.wait_for_timeout(1500)
    return page


def _apply_form(page, ats_guess, job, cover_letter, resume_pdf):
    """Detect the ATS actually rendered on this page and fill/submit it."""
    ats = _detect_ats_from_frames(page, ats_guess)
    if ats == "greenhouse":
        frame = _form_frame(page, ats)
        return ats, _apply_greenhouse(frame, page, job, cover_letter, resume_pdf)
    if ats == "lever":
        frame = _form_frame(page, ats)
        return ats, _apply_lever(frame, page, job, cover_letter, resume_pdf)
    return ats, _apply_generic(page, job, cover_letter, resume_pdf)


def _submit_and_verify(frame, page) -> bool:
    """Click submit, then require positive confirmation text before reporting success.

    A click alone is not proof: an invisible reCAPTCHA challenge, a blank required
    custom question, or a validation error can all silently no-op the click. Claiming
    "submitted" without checking for a real confirmation would be worse than not
    auto-submitting at all — the applicant would believe they'd applied when they hadn't.
    """
    clicked = False
    for sel in [
        "#submit_app",
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Submit Application')",
        "button:has-text('Submit application')",
    ]:
        try:
            btn = frame.locator(sel).first
            if btn.count() and btn.is_visible(timeout=ACTION_TIMEOUT_MS):
                btn.click(timeout=ACTION_TIMEOUT_MS)
                clicked = True
                break
        except Exception:
            continue

    if not clicked:
        return False

    page.wait_for_timeout(4000)
    try:
        visible_text = (frame.locator("body").inner_text(timeout=ACTION_TIMEOUT_MS) or "")
    except Exception:
        visible_text = ""
    try:
        visible_text += " " + (page.locator("body").inner_text(timeout=ACTION_TIMEOUT_MS) or "")
    except Exception:
        pass

    return bool(CONFIRMATION_PATTERN.search(visible_text))


def _apply_greenhouse(frame, page, job, cover_letter, resume_pdf) -> dict:
    _fill(frame, "#first_name", FIRST_NAME)
    _fill(frame, "#last_name", LAST_NAME)
    _fill(frame, "#email", PROFILE["email"])
    _fill(frame, "#phone", PROFILE["phone"])
    _upload(frame, "#resume", resume_pdf)

    # Some Greenhouse boards expose a typed cover-letter textarea; others want a file.
    if not _fill(frame, "textarea#cover_letter_text, textarea[name='cover_letter_text']", cover_letter):
        cl_pdf = _cover_letter_pdf(job["id"], cover_letter)
        _upload(frame, "#cover_letter", cl_pdf)

    _answer_boolean_selects(frame)

    submitted = _submit_and_verify(frame, page)
    return {"submitted": submitted, "attempted_submit": True}


def _apply_lever(frame, page, job, cover_letter, resume_pdf) -> dict:
    _fill(frame, "input[name='name']", PROFILE["name"])
    _fill(frame, "input[name='email']", PROFILE["email"])
    _fill(frame, "input[name='phone']", PROFILE["phone"])
    _fill(frame, "input[name*='Location' i]", PROFILE["address_display"])
    _fill(frame, "input[name*='LinkedIn' i]", f"https://{PROFILE['linkedin']}")
    _upload(frame, "input[name='resume']", resume_pdf)
    _fill(frame, "textarea[name='comments']", cover_letter)
    _answer_boolean_selects(frame)

    submitted = _submit_and_verify(frame, page)
    return {"submitted": submitted, "attempted_submit": True}


# Keyword -> profile value, checked against each visible text-input's label/placeholder/name.
_GENERIC_TEXT_FIELDS = [
    (re.compile(r"first\s*name", re.I), FIRST_NAME),
    (re.compile(r"last\s*name|surname", re.I), LAST_NAME),
    (re.compile(r"full\s*name|^name", re.I), PROFILE["name"]),
    (re.compile(r"e-?mail", re.I), PROFILE["email"]),
    (re.compile(r"phone|mobile|telephone", re.I), PROFILE["phone"]),
    (re.compile(r"street|address\s*line", re.I), PROFILE["address_components"]["street"]),
    (re.compile(r"city|town", re.I), PROFILE["address_components"]["city"]),
    (re.compile(r"province|state", re.I), PROFILE["address_components"]["province"]),
    (re.compile(r"postal|zip", re.I), PROFILE["address_components"]["postal_code"]),
    (re.compile(r"linkedin", re.I), f"https://{PROFILE['linkedin']}"),
    (re.compile(r"website|portfolio", re.I), f"https://{PROFILE['website']}"),
]


def _apply_generic(page, job, cover_letter, resume_pdf) -> dict:
    """Best-effort fill for non-standard sites, then submit when the page is
    verifiably an application form. The guard is the resume upload: newsletter
    boxes, search bars, and contact widgets never take a resume file, so a
    successful upload is the signal that clicking submit sends an application
    and not something else."""
    resume_uploaded = False
    try:
        inputs = page.locator(
            "input[type='text'], input[type='email'], input[type='tel'], input:not([type])"
        ).all()
    except Exception:
        inputs = []

    for el in inputs:
        try:
            if not el.is_visible(timeout=500):
                continue
            hint = " ".join(filter(None, [
                _nearby_label_text(page, el),
                el.get_attribute("placeholder") or "",
                el.get_attribute("name") or "",
            ]))
            for pattern, value in _GENERIC_TEXT_FIELDS:
                if pattern.search(hint):
                    el.fill(value, timeout=ACTION_TIMEOUT_MS)
                    break
        except Exception:
            continue

    # Resume / cover letter file inputs
    try:
        file_inputs = page.locator("input[type='file']").all()
    except Exception:
        file_inputs = []
    cl_pdf = None
    for el in file_inputs:
        try:
            hint = _nearby_label_text(page, el).lower()
            if "cover" in hint:
                cl_pdf = cl_pdf or _cover_letter_pdf(job["id"], cover_letter)
                el.set_input_files(cl_pdf, timeout=ACTION_TIMEOUT_MS)
            else:
                # Default assumption: first unlabeled/resume-ish file field is the resume
                el.set_input_files(resume_pdf, timeout=ACTION_TIMEOUT_MS)
                resume_uploaded = True
        except Exception:
            continue

    # Cover-letter textarea, if present
    try:
        textareas = page.locator("textarea").all()
        for ta in textareas:
            hint = _nearby_label_text(page, ta).lower()
            if "cover" in hint or "additional" in hint or "why" in hint:
                ta.fill(cover_letter, timeout=ACTION_TIMEOUT_MS)
                break
    except Exception:
        pass

    _answer_boolean_selects(page)

    if resume_uploaded:
        submitted = _submit_and_verify(page, page)
        return {"submitted": submitted, "attempted_submit": True}
    return {"submitted": False, "attempted_submit": False}


_RUN_HISTORY_STATUS = {
    "submitted": "Success",
    "submit_unconfirmed": "Failed",
    "prefilled_pending_review": "Skipped",
    "failed": "Failed",
    "blocked": "Skipped",
}


def apply_on_website(job: dict, cover_letter: str, resume_pdf: str) -> dict:
    """Thin logging wrapper around _apply_on_website(job, cover_letter, resume_pdf) —
    records the run to automation_runs.jsonl without altering its behavior."""
    start = time.time()
    result = _apply_on_website(job, cover_letter, resume_pdf)
    record_run(
        "Website Auto-Apply",
        f"{job.get('title', '?')} @ {job.get('company', '?')}",
        _RUN_HISTORY_STATUS.get(result.get("status"), "Skipped"),
        f"{result.get('status')} ({result.get('ats')})",
        duration_ms=int((time.time() - start) * 1000),
    )
    return result


def _apply_on_website(job: dict, cover_letter: str, resume_pdf: str) -> dict:
    """Attempt to fill and submit the application form at job['url'].

    Returns:
      {
        "status": "submitted"                  # confirmation text verified
                | "submit_unconfirmed"         # submit clicked, no confirmation found
                | "prefilled_pending_review"   # no safe submit path (no resume field)
                | "blocked"                    # bot-check interstitial, nothing filled
                | "failed",
        "ats": "greenhouse" | "lever" | "workday" | "icims" | "generic",
        "screenshot": str | None,
      }
    """
    ats_guess = detect_ats(job["url"])

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_default_timeout(NAV_TIMEOUT_MS)
            page.goto(job["url"], wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
            page.wait_for_timeout(2000)  # let SPA forms (Lever/Greenhouse embeds) render

            # Job aggregators (Glassdoor, ZipRecruiter, Indeed) throw headless browsers behind
            # a Cloudflare bot-check instead of the real posting. No form exists on this page —
            # filling anything is impossible, so don't let it fall through to "prefilled".
            body_text = ""
            try:
                body_text = page.locator("body").inner_text(timeout=ACTION_TIMEOUT_MS) or ""
            except Exception:
                pass
            if BOT_BLOCK_PATTERN.search(body_text):
                screenshot = None
                try:
                    screenshot = str(SCREENSHOT_DIR / f"{job['id']}.png")
                    page.screenshot(path=screenshot, full_page=True)
                except Exception:
                    screenshot = None
                browser.close()
                return {"status": "blocked", "ats": ats_guess, "screenshot": screenshot}

            # Many companies white-label Greenhouse/Lever under their own domain and only
            # reveal it via an embedded iframe once the page has loaded — re-check now.
            ats, result = _apply_form(page, ats_guess, job, cover_letter, resume_pdf)

            # Job-board listing pages (CharityVillage, CanadaJobs.works, etc.) often gate
            # the real form behind a "Quick Apply" / "Apply Now" button instead of
            # embedding it here, so there was never a resume field to find. Follow that
            # button once — it may open a new tab, navigate, or reveal an in-page form —
            # and retry on wherever it leads, re-detecting the ATS from scratch since it
            # commonly turns out to be a white-labeled Greenhouse/Lever form after all.
            if not result.get("attempted_submit"):
                apply_btn = _find_apply_button(page)
                if apply_btn is not None:
                    followed_page = _follow_apply_button(page, apply_btn)
                    followed_body = ""
                    try:
                        followed_body = followed_page.locator("body").inner_text(timeout=ACTION_TIMEOUT_MS) or ""
                    except Exception:
                        pass
                    if not BOT_BLOCK_PATTERN.search(followed_body):
                        ats, result = _apply_form(
                            followed_page, detect_ats(followed_page.url), job, cover_letter, resume_pdf
                        )
                        page = followed_page  # screenshot below should capture the real form

            screenshot = None
            try:
                screenshot = str(SCREENSHOT_DIR / f"{job['id']}.png")
                page.screenshot(path=screenshot, full_page=True)
            except Exception:
                screenshot = None

            browser.close()

            if result.get("submitted"):
                return {"status": "submitted", "ats": ats, "screenshot": screenshot}
            if result.get("attempted_submit"):
                return {"status": "submit_unconfirmed", "ats": ats, "screenshot": screenshot}
            return {"status": "prefilled_pending_review", "ats": ats, "screenshot": screenshot}

    except Exception as e:
        print(f"[web_applier] Failed on {job['url']}: {e}")
        return {"status": "failed", "ats": ats_guess, "screenshot": None}
