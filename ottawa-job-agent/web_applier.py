"""Auto-apply on company career-site forms via Playwright.

Fully autonomous (Sprout-mode): every form gets filled AND submitted when we
can do so honestly. Greenhouse/Lever use their known selectors; all other
sites get a best-effort fill, and if the page looks like a genuine application
form (a real name/email field got filled, or a resume upload succeeded), the
submit button is clicked too. A submit only counts as "submitted" when real
confirmation text appears afterwards; anything less is reported as
unconfirmed so the digest never claims an application that didn't happen.
Only real profile/autofill data is ever entered — unknown questions are left
blank, never invented.

Two things this deliberately never automates: a captcha challenge blocking
submit (only a human may answer it — bypassing that would be evading an
anti-bot measure the site put there on purpose), and anything with no digital
form at all (mail/phone/in-person instructions, or a sign-in-gated apply flow
Sahawat hasn't personally authenticated for via jobbank_session.py). Both stay
FYI-only in the digest.

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

from agent_config import is_review_only
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
    # "Are you eligible to work for any employer in Canada?" is the same fact as
    # the legally-authorized line above, phrased the way Ottawa employers ask it.
    # It matched nothing before, so the one required question on a live Greenhouse
    # posting that we *can* honestly answer was being left blank.
    (re.compile(r"eligible to work", re.I), "Yes"),
    (re.compile(r"driver'?s?\s*licen[cs]e", re.I), "Yes"),
    (re.compile(r"(located|based|residing).*ottawa", re.I), "Yes"),
]

# The Yes/No answers above are only true for CANADA-context questions (Sahawat
# is a Canadian PR based in Ottawa). "Authorized to work in the United States?"
# → the honest answer is No, and "require sponsorship?" flips to Yes for a US
# role. Never auto-answer US-scoped questions — leave them blank so a required
# one fails validation and the job falls back to the honest FYI path.
US_CONTEXT = re.compile(r"united states|\bu\.?s\.?a?\b|h-?1b", re.I)


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


def _is_greenhouse_app_url(u: str) -> bool:
    """True only for URLs that host an actual Greenhouse posting/application —
    boards.greenhouse.io/<co>/jobs/<id>, job-boards.greenhouse.io, or the
    embed/job_app iframe. Careers-hub pages embed Greenhouse *search* widgets
    (embed/job_board) whose frames also match a bare "greenhouse.io" check,
    which sent the filler after forms that don't exist."""
    return "greenhouse.io" in u and ("/jobs/" in u or "embed/job_app" in u)


def _detect_ats_from_frames(page, fallback: str) -> str:
    """Re-check ATS after the page has loaded by inspecting every frame's URL —
    the reliable signal for white-labeled Greenhouse/Lever embeds on custom domains."""
    for frame in page.frames:
        u = (frame.url or "").lower()
        if _is_greenhouse_app_url(u):
            return "greenhouse"
        if "lever.co" in u:
            return "lever"
    return fallback


def _form_frame(page, ats: str):
    """Return the frame that actually hosts the application form fields."""
    for frame in page.frames:
        u = (frame.url or "").lower()
        if ats == "greenhouse" and _is_greenhouse_app_url(u):
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
            if US_CONTEXT.search(label_text) and "canada" not in label_text.lower():
                continue
            for pattern, answer in BOOLEAN_ANSWERS:
                if pattern.search(label_text):
                    sel.select_option(label=answer)
                    break
        except Exception:
            continue
    _answer_boolean_radios(page)
    _answer_comboboxes(page)


def _answer_boolean_radios(page):
    """Same idea for radio-group questions (Lever renders all its custom Yes/No
    screening questions as radios, which the <select> pass above never saw —
    leaving required work-authorization questions blank and every submit stuck
    at validation)."""
    try:
        radios = page.locator("input[type='radio']").all()
    except Exception:
        radios = []

    # Group the radios into questions by their shared name attribute.
    groups = {}
    for r in radios:
        try:
            name = r.get_attribute("name") or ""
        except Exception:
            continue
        if name:
            groups.setdefault(name, []).append(r)

    for options in groups.values():
        try:
            question = _nearby_label_text(page, options[0])
            if US_CONTEXT.search(question) and "canada" not in question.lower():
                continue
            answer = None
            for pattern, ans in BOOLEAN_ANSWERS:
                if pattern.search(question):
                    answer = ans
                    break
            if not answer:
                continue
            for opt in options:
                value = (opt.get_attribute("value") or "").strip()
                opt_label = value or _radio_option_text(opt)
                if opt_label.lower().startswith(answer.lower()):
                    # Lever hides the real <input> behind a styled span, so
                    # check() times out on visibility — click the label instead.
                    try:
                        opt.check(timeout=ACTION_TIMEOUT_MS)
                    except Exception:
                        label = opt.locator("xpath=ancestor::label[1]").first
                        if label.count():
                            label.click(timeout=ACTION_TIMEOUT_MS)
                    break
        except Exception:
            continue


# Greenhouse (and any other React form) renders a dropdown as an <input
# role="combobox"> driven by React state. There is no <select>, no radio, and no
# hidden input to write, so both passes above see nothing at all on such a form.
_COMBOBOX_SELECTOR = "input[role='combobox']"

# Only an option the site itself rendered may ever be chosen. Typing a value into
# a react-select input without picking a real option leaves the field empty in
# React's state while looking filled on screen — the form would submit blank.
_LOCATION_LABEL = re.compile(r"\blocation\b|\bcity\b|where are you", re.I)
_COUNTRY_LABEL = re.compile(r"^\s*country\b|country of", re.I)


def _combobox_answer(box, label: str) -> str:
    """The honest answer for this dropdown, or "" to leave it blank."""
    try:
        field_id = (box.get_attribute("id") or "").lower()
    except Exception:
        field_id = ""

    if field_id == "country" or _COUNTRY_LABEL.search(label):
        return PROFILE["address_components"]["country"]
    if "location" in field_id or _LOCATION_LABEL.search(label):
        components = PROFILE["address_components"]
        return "{}, {}".format(components["city"], components["province"])

    for pattern, answer in BOOLEAN_ANSWERS:
        if pattern.search(label):
            return answer
    return ""


# A question further down a long application form is below the fold, and a click
# that has to scroll there first needs more than the 1500ms an in-view click takes.
_COMBOBOX_CLICK_TIMEOUT_MS = 5000
# A location autocomplete queries a server on each keystroke, so its menu arrives
# well after a static Yes/No list would have.
_OPTION_WAIT_MS = 4000


def _listbox_selector(box) -> str:
    """CSS scoping the options to THIS combobox's own open menu.

    A global "[role='option']" search is wrong on a real application form. The
    phone field's country picker keeps 244 dial-code options in the DOM at all
    times, so every dropdown saw that same list, matched nothing in it, and left
    every question blank — while the location field's ten real options sat past
    them, never reached. ARIA already publishes the link from a combobox to its
    own menu, and the id is only populated once the menu is open.
    """
    try:
        controls = (box.get_attribute("aria-controls") or "").strip()
    except Exception:
        controls = ""
    if controls:
        return "[id='{}'] [role='option']".format(controls)

    # react-select names its options after the field even before it wires up
    # aria-controls. Scoping to nothing is better than scoping to the whole page.
    try:
        field_id = (box.get_attribute("id") or "").strip()
    except Exception:
        field_id = ""
    if field_id:
        return "[id^='react-select-{}-option']".format(field_id)
    return ""


def _combobox_options(frame, box, search: str = "") -> list:
    """Open the combobox and return the (text, locator) options it really renders.

    Option text is read in one batched call rather than one round trip per option:
    a country list runs to ~500 entries, and a per-option read with the page's
    20-second default timeout is the exact bug that hung the Workday wizard in
    Sep 2026. The locators handed back are built by index without touching the
    page, so nothing here can inherit that default.
    """
    try:
        box.scroll_into_view_if_needed(timeout=_COMBOBOX_CLICK_TIMEOUT_MS)
    except Exception:
        pass
    try:
        # Clicking an already-open react-select closes it, which would undo the
        # first search attempt on the retry pass.
        if (box.get_attribute("aria-expanded") or "").strip().lower() != "true":
            box.click(timeout=_COMBOBOX_CLICK_TIMEOUT_MS)
    except Exception:
        return []
    if search:
        try:
            box.type(search, delay=20, timeout=_COMBOBOX_CLICK_TIMEOUT_MS)
        except Exception:
            pass

    selector = _listbox_selector(box)
    if not selector:
        return []

    menu = frame.locator(selector)
    try:
        menu.first.wait_for(timeout=_OPTION_WAIT_MS)
        texts = menu.evaluate_all(
            "els => els.map(el => (el.textContent || '').trim())")
    except Exception:
        return []

    return [(text, menu.nth(index))
            for index, text in enumerate(texts) if text]


def _matching_option(options: list, answer: str, is_location: bool):
    """The one option that honestly means `answer`, or None.

    A location needs both the city and the region to match: "Ottawa" alone would
    happily select Ottawa, Illinois and put a false address on his application.
    """
    wanted = answer.strip().lower()
    if is_location:
        for text, option in options:
            low = text.lower()
            if "ottawa" in low and ("canada" in low or ", on" in low or "ontario" in low):
                return option
        return None

    for text, option in options:
        if text.strip().lower() == wanted:
            return option
    for text, option in options:
        if text.strip().lower().startswith(wanted):
            return option
    return None


def _combobox_searches(answer: str, is_location: bool) -> tuple:
    """What to type into this combobox to make its real options appear.

    A location field renders nothing until it has a query, and its server-side
    lookup returns nothing for "Ottawa, ON" — so search on the city alone and let
    _matching_option keep the strict city-and-region test. Search broad, match
    narrow: the loose half never picks anything on its own.
    """
    if is_location:
        return (answer.split(",")[0].strip(),)
    return ("", answer)


def _choose_combobox_option(frame, box, answer: str, is_location: bool) -> bool:
    """Pick `answer` from what this combobox actually offers.

    Returns False without writing anything when nothing matches. A required
    question left blank stops the submit at validation, which is the honest
    outcome — inventing an option the employer never offered is not.
    """
    for search in _combobox_searches(answer, is_location):
        option = _matching_option(_combobox_options(frame, box, search),
                                  answer, is_location)
        if option is None:
            continue
        try:
            option.click(timeout=ACTION_TIMEOUT_MS)
            return True
        except Exception:
            return False
    return False


def _answer_comboboxes(frame):
    """Answer react-select dropdowns, the ones the <select> and radio passes miss.

    On a Greenhouse posting this is every dropdown on the form: required work
    authorization, AODA accommodation, country, and candidate location all render
    as comboboxes. Before this pass they were left blank on every board, so the
    submit was rejected by validation every time and the invisible reCAPTCHA badge
    on the page then mislabelled the outcome as a captcha gate.
    """
    try:
        boxes = frame.locator(_COMBOBOX_SELECTOR).all()
    except Exception:
        return

    for box in boxes:
        try:
            if not box.is_visible(timeout=ACTION_TIMEOUT_MS):
                continue
            label = _nearby_label_text(frame, box)
            if US_CONTEXT.search(label) and "canada" not in label.lower():
                continue
            answer = _combobox_answer(box, label)
            if not answer:
                continue
            is_location = ("location" in (box.get_attribute("id") or "").lower()
                           or bool(_LOCATION_LABEL.search(label)))
            if not _choose_combobox_option(frame, box, answer, is_location):
                # Leave it blank and closed rather than half-open over the form.
                try:
                    box.press("Escape", timeout=ACTION_TIMEOUT_MS)
                except Exception:
                    pass
        except Exception:
            continue


def _radio_option_text(radio) -> str:
    """Text of the individual option (its wrapping label), not the whole question."""
    try:
        label = radio.locator("xpath=ancestor::label[1]").first
        if label.count():
            return (label.inner_text() or "").strip()
    except Exception:
        pass
    return ""


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
    r"thanks for applying|successfully (submitted|applied)|you('| ha)ve successfully applied|"
    r"we('| ha)ve received your application|application (complete|confirmed)|"
    r"candidature (a été (bien )?reçue|envoyée|soumise)|"
    r"merci (d'avoir postulé|pour votre candidature)|"
    r"nous avons (bien )?reçu votre candidature",
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

# Bot-check interstitials that redirect the browser off the employer's domain
# entirely. Matching these by host is far more reliable than by body copy:
# Radware's page renders almost no static text (the CIHI/Njoyn challenge slips
# straight past BOT_BLOCK_PATTERN above), but it always parks the tab on its own
# validation host first. Checked in addition to the text pattern, not instead:
# a same-origin "checking your browser" page never changes host.
INTERSTITIAL_HOSTS = ("validate.perfdrive.com",)


def _is_interstitial(url: str) -> bool:
    try:
        host = (url or "").split("//", 1)[-1].split("/", 1)[0].lower()
    except Exception:
        return False
    return any(host == h or host.endswith("." + h) for h in INTERSTITIAL_HOSTS)


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


# Job boards whose footer/contact emails must never receive an application —
# they host the posting, they aren't the employer.
_BOARD_DOMAINS = re.compile(
    r"charityvillage|indeed|glassdoor|ziprecruiter|linkedin|jobbank|workopolis"
    r"|jobillico|careerbeacon|simplyhired|monster|talent\.com|jobgether|lever\.co"
    r"|greenhouse|myworkdayjobs|icims|jobs\.ca|eluta"
    # cercottawa.ca is a community employment resource centre — it lists other
    # employers' openings and doesn't hire for them (confirmed directly by CERC
    # staff after the pipeline emailed info@cercottawa.ca 8x for fabricated job
    # titles scraped off their shared listings page in Aug 2026).
    r"|cercottawa", re.I,
)
_JUNK_LOCALPART = re.compile(
    r"no-?reply|donotreply|privacy|webmaster|abuse|unsubscribe|postmaster|example", re.I
)
_HIRING_KEYWORDS = re.compile(r"hr|career|job|recruit|talent|apply|hiring|resume", re.I)
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def _pick_apply_email(candidates: list, page_host: str) -> str:
    """Choose the address most likely to be the employer's application inbox.
    Prefer hiring-keyword addresses; otherwise accept only an address whose
    domain matches the page's own host (the employer's site). Anything on a
    job-board domain or infrastructure localpart is discarded — mass-mailing a
    board's info@ would be spam, not an application."""
    seen_addrs = []
    for addr in candidates:
        a = addr.strip().strip(".").lower()
        if a in seen_addrs or _JUNK_LOCALPART.search(a.split("@")[0]):
            continue
        if _BOARD_DOMAINS.search(a.split("@")[1]):
            continue
        seen_addrs.append(a)
    for a in seen_addrs:
        if _HIRING_KEYWORDS.search(a.split("@")[0]):
            return a
    for a in seen_addrs:
        domain_core = a.split("@")[1].rsplit(".", 2)[-2]
        if domain_core and domain_core in page_host.lower():
            return a
    return ""


def _harvest_apply_email(page) -> str:
    """Best-effort application email from the posting page: mailto links first
    (explicit invitation to email), then addresses in the visible text."""
    candidates = []
    try:
        for href in page.eval_on_selector_all(
            "a[href^='mailto:']", "els => els.map(e => e.getAttribute('href'))"
        ):
            addr = (href or "")[7:].split("?")[0]
            if addr:
                candidates.append(addr)
    except Exception:
        pass
    try:
        body = page.locator("body").inner_text(timeout=ACTION_TIMEOUT_MS) or ""
        candidates.extend(_EMAIL_RE.findall(body))
    except Exception:
        pass
    try:
        host = urlparse(page.url).netloc
    except Exception:
        host = ""
    return _pick_apply_email(candidates, host)


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

    # Lever redirects to .../thanks and Greenhouse to a confirmation page on
    # success — an equally positive signal that survives wording differences
    # the text pattern below might miss.
    try:
        if re.search(r"/thanks(\b|/|$)|confirmation", page.url, re.I):
            return True
    except Exception:
        pass

    try:
        visible_text = (frame.locator("body").inner_text(timeout=ACTION_TIMEOUT_MS) or "")
    except Exception:
        visible_text = ""
    try:
        visible_text += " " + (page.locator("body").inner_text(timeout=ACTION_TIMEOUT_MS) or "")
    except Exception:
        pass

    return bool(CONFIRMATION_PATTERN.search(visible_text))


# The reCAPTCHA v3 / invisible badge is 256x60. The smallest thing a human is
# ever asked to click, the v2 checkbox anchor, is 304x78.
_CAPTCHA_MIN_HEIGHT_PX = 70
_INVISIBLE_CAPTCHA = re.compile(r"size=invisible", re.I)


def _has_interactive_captcha(page) -> bool:
    """True only when a human really must solve something.

    reCAPTCHA v3 and both invisible variants inject the same iframe as a real
    challenge while demanding no interaction at all, and Greenhouse carries an
    invisible enterprise badge on every posting. Counting those told him a form
    was "fully pre-filled, one human click from done" when the real blocker was
    an unanswered required question — so he'd open the link and find the same
    validation wall. The bar here is a challenge that is rendered, sized for a
    person, and not self-declared invisible.
    """
    for selector in ("div.g-recaptcha", "div.h-captcha"):
        try:
            for element in page.locator(selector).all():
                if (element.get_attribute("data-size") or "").strip().lower() == "invisible":
                    continue
                if element.is_visible(timeout=ACTION_TIMEOUT_MS):
                    return True
        except Exception:
            continue

    try:
        frames = page.locator(
            "iframe[src*='hcaptcha'], iframe[src*='recaptcha'], "
            "iframe[title*='captcha' i]").all()
    except Exception:
        return False

    for frame in frames:
        try:
            if _INVISIBLE_CAPTCHA.search(frame.get_attribute("src") or ""):
                continue
            box = frame.bounding_box()
            if box and box["height"] >= _CAPTCHA_MIN_HEIGHT_PX:
                return True
        except Exception:
            continue
    return False


def _maybe_submit(frame, page) -> dict:
    """Click submit and verify — unless review-only mode is active (agent_config.py),
    in which case report the same shape as "no safe submit path was found" so the
    pipeline lands on its existing prefilled_pending_review status instead of a new
    one, keeping digest/tracker/dashboard code unchanged. Checked fresh on every call
    (not cached) since the flag can flip between runs, including scheduled ones."""
    if is_review_only():
        return {"submitted": False, "attempted_submit": False}
    return {"submitted": _submit_and_verify(frame, page), "attempted_submit": True}


def _apply_greenhouse(frame, page, job, cover_letter, resume_pdf) -> dict:
    filled_name = _fill(frame, "#first_name", FIRST_NAME)
    _fill(frame, "#last_name", LAST_NAME)
    filled_email = _fill(frame, "#email", PROFILE["email"])
    _fill(frame, "#phone", PROFILE["phone"])
    _upload(frame, "#resume", resume_pdf)

    # No name AND no email field means this page doesn't hold the application
    # form at all (careers hub, description-only page). Report honestly so the
    # caller's follow-the-apply-button retry gets its chance instead of a fake
    # "submit clicked" claim.
    if not (filled_name or filled_email):
        return {"submitted": False, "attempted_submit": False}

    # Some Greenhouse boards expose a typed cover-letter textarea; others want a file.
    if not _fill(frame, "textarea#cover_letter_text, textarea[name='cover_letter_text']", cover_letter):
        cl_pdf = _cover_letter_pdf(job["id"], cover_letter)
        _upload(frame, "#cover_letter", cl_pdf)

    _answer_boolean_selects(frame)

    return _maybe_submit(frame, page)


def _current_company_text() -> str:
    """Honest 'current company' for required fields: he is between roles, so
    name the transition and the most recent real employer from the profile."""
    entries = PROFILE.get("experience", [])
    if entries and entries[0]["company"].lower() != "career transition":
        return entries[0]["company"]
    if len(entries) > 1:
        return f"In transition (most recent: {entries[1]['company']})"
    return "In transition"


def _apply_lever(frame, page, job, cover_letter, resume_pdf) -> dict:
    filled_name = _fill(frame, "input[name='name']", PROFILE["name"])
    filled_email = _fill(frame, "input[name='email']", PROFILE["email"])
    _fill(frame, "input[name='phone']", PROFILE["phone"])

    # Same honest-report rule as Greenhouse: no name/email field = no form here
    # (we're on the posting/description page), so let the caller retry via the
    # apply button instead of pretending a submit was attempted.
    if not (filled_name or filled_email):
        return {"submitted": False, "attempted_submit": False}

    # "Current company" (name='org') is required on many Lever boards and was
    # the lone validation blocker on an otherwise fully-filled form (Jul 18,
    # AIP Connect). He has no current employer — say so honestly rather than
    # dressing the gap up as a job.
    _fill(frame, "input[name='org']", _current_company_text())
    _fill(frame, "input[name='location']", "Ottawa, ON, Canada")
    _fill(frame, "input[name*='Location' i]", PROFILE["address_display"])
    _fill(frame, "input[name*='LinkedIn' i]", f"https://{PROFILE['linkedin']}")
    _upload(frame, "input[name='resume']", resume_pdf)
    _fill(frame, "textarea[name='comments']", cover_letter)
    _answer_boolean_selects(frame)

    return _maybe_submit(frame, page)


# Keyword -> profile value, checked against each visible text-input's label/placeholder/name.
# is_identity flags the fields _apply_greenhouse/_apply_lever already trust as their submit
# signal (a filled name or email field) — phone/address/LinkedIn/etc alone don't prove this
# is an application form, so they don't count toward that same bar here.
_GENERIC_TEXT_FIELDS = [
    (re.compile(r"first\s*name", re.I), FIRST_NAME, True),
    (re.compile(r"last\s*name|surname", re.I), LAST_NAME, True),
    (re.compile(r"full\s*name|^name", re.I), PROFILE["name"], True),
    (re.compile(r"e-?mail", re.I), PROFILE["email"], True),
    (re.compile(r"phone|mobile|telephone", re.I), PROFILE["phone"], False),
    (re.compile(r"street|address\s*line", re.I), PROFILE["address_components"]["street"], False),
    (re.compile(r"city|town", re.I), PROFILE["address_components"]["city"], False),
    (re.compile(r"province|state", re.I), PROFILE["address_components"]["province"], False),
    (re.compile(r"postal|zip", re.I), PROFILE["address_components"]["postal_code"], False),
    (re.compile(r"linkedin", re.I), f"https://{PROFILE['linkedin']}", False),
    (re.compile(r"website|portfolio", re.I), f"https://{PROFILE['website']}", False),
]


def _apply_generic(page, job, cover_letter, resume_pdf) -> dict:
    """Best-effort fill for non-standard sites, then submit when the page is
    verifiably an application form. The guard used to be the resume upload
    alone, but most non-ATS forms don't expose a file input the selectors
    here recognize (drag-and-drop widgets, multi-step wizards, "paste resume
    text" boxes) — so a form that was fully and correctly filled never got
    submitted. The bar is now the same one _apply_greenhouse/_apply_lever
    already trust: a real name or email field got filled, not just any text
    input. A resume upload, when one is found, is still stronger evidence
    on top of that."""
    resume_uploaded = False
    filled_identity_field = False
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
            for pattern, value, is_identity in _GENERIC_TEXT_FIELDS:
                if pattern.search(hint):
                    el.fill(value, timeout=ACTION_TIMEOUT_MS)
                    filled_identity_field = filled_identity_field or is_identity
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

    if resume_uploaded or filled_identity_field:
        return _maybe_submit(page, page)
    return {"submitted": False, "attempted_submit": False}


_RUN_HISTORY_STATUS = {
    "submitted": "Success",
    "submit_unconfirmed": "Failed",
    "prefilled_pending_review": "Skipped",
    "failed": "Failed",
    "blocked": "Skipped",
}


HEADED_CAPTCHA_WAIT_S = 360
_CAPTCHA_POLL_INTERVAL_MS = 3000


def _wait_for_human_to_clear_captcha(page, timeout_s: int = HEADED_CAPTCHA_WAIT_S) -> bool:
    """Poll the live page while a human solves the captcha and clicks Submit in
    the visible window. Returns True once confirmation text appears, False if
    timeout_s elapses unresolved."""
    print(
        f"[web_applier] Captcha detected — solve it and click Submit in the open "
        f"window (waiting up to {timeout_s}s)..."
    )
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        page.wait_for_timeout(_CAPTCHA_POLL_INTERVAL_MS)
        try:
            body_text = page.locator("body").inner_text(timeout=ACTION_TIMEOUT_MS) or ""
        except Exception:
            continue
        if CONFIRMATION_PATTERN.search(body_text):
            print("[web_applier] Confirmation text detected — submission verified.")
            return True
    print("[web_applier] Timed out waiting for captcha resolution.")
    return False


def apply_on_website(job: dict, cover_letter: str, resume_pdf: str, headless: bool = True) -> dict:
    """Thin logging wrapper around _apply_on_website(job, cover_letter, resume_pdf) —
    records the run to automation_runs.jsonl without altering its behavior."""
    start = time.time()
    result = _apply_on_website(job, cover_letter, resume_pdf, headless=headless)
    record_run(
        "Website Auto-Apply",
        f"{job.get('title', '?')} @ {job.get('company', '?')}",
        _RUN_HISTORY_STATUS.get(result.get("status"), "Skipped"),
        f"{result.get('status')} ({result.get('ats')})",
        duration_ms=int((time.time() - start) * 1000),
    )
    return result


def _apply_on_website(job: dict, cover_letter: str, resume_pdf: str, headless: bool = True) -> dict:
    """Attempt to fill and submit the application form at job['url'].

    Args:
      headless: False opens a visible browser window and, if a captcha blocks
        submission, pauses for a human to solve it and click Submit live
        instead of reporting captcha_gate immediately. Default True preserves
        the unattended pipeline's exact existing behavior.

    Returns:
      {
        "status": "submitted"                  # confirmation text verified
                | "submit_unconfirmed"         # submit clicked, no confirmation found
                | "prefilled_pending_review"   # no safe submit path (no resume field)
                | "blocked"                    # bot-check interstitial, nothing filled
                | "failed",
        "ats": "greenhouse" | "lever" | "workday" | "icims" | "generic",
        "screenshot": str | None,
        "apply_url": str,        # where the form actually lives, after following
                                 # the Apply button / into the ATS iframe
        "form_fields": list,     # the form's questions (form_schema shape), so a
                                 # non-submitted job still gets a full prefilled
                                 # package instead of a bare link
      }
    """
    ats_guess = detect_ats(job["url"])

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
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
            if BOT_BLOCK_PATTERN.search(body_text) or _is_interstitial(page.url):
                screenshot = None
                try:
                    screenshot = str(SCREENSHOT_DIR / f"{job['id']}.png")
                    page.screenshot(path=screenshot, full_page=True)
                except Exception:
                    screenshot = None
                # page.url here is usually the bot-check's own host, which is
                # worthless in a digest — the link has to be something he can
                # actually open, so fall back to the posting we started from.
                blocked_url = page.url
                if _is_interstitial(blocked_url) or not blocked_url:
                    blocked_url = job.get("url", "") or blocked_url
                browser.close()
                return {
                    "status": "blocked",
                    "ats": ats_guess,
                    "screenshot": screenshot,
                    "apply_url": blocked_url,
                    "form_fields": [],
                }

            # Lever hosts the posting text at jobs.lever.co/<co>/<id> and the actual
            # form one path segment deeper at .../apply — filling the posting page
            # does nothing. Jump straight to the form URL before touching anything.
            parsed = urlparse(page.url)
            if "lever.co" in parsed.netloc.lower() and not parsed.path.rstrip("/").endswith("/apply"):
                apply_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}/apply"
                page.goto(apply_url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
                page.wait_for_timeout(2000)

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

            # An unconfirmed submit with a captcha widget on the page isn't a
            # mystery — the captcha IS the blocker. Lever fires hCaptcha on
            # submit across its boards; only a human may answer it, so report
            # the truth: fully pre-filled, one human click from done.
            has_captcha = False
            if not result.get("submitted"):
                has_captcha = _has_interactive_captcha(page)

            # In headed/live mode, a captcha isn't a dead end — pause here so
            # the human watching the visible window can solve it and click
            # Submit themselves, then verify what actually happened before
            # closing. Headless (the unattended pipeline) never reaches this.
            if has_captcha and result.get("attempted_submit") and not headless:
                if _wait_for_human_to_clear_captcha(page):
                    result["submitted"] = True
                    has_captcha = False
                try:
                    page.screenshot(path=screenshot, full_page=True)
                except Exception:
                    pass

            # Must happen while the browser is still open: if nothing was
            # submittable, the page may name an application inbox that unlocks
            # the captcha-free email lane.
            found_email = ""
            if not (result.get("submitted") or result.get("attempted_submit")):
                found_email = _harvest_apply_email(page)

            # Also while the browser is open: read the form's questions and the URL
            # of the page/frame actually hosting it, so anything short of a verified
            # submission can still be turned into a prefilled application package
            # instead of a bare "here's the link" email. Skipped once submitted —
            # that page is a confirmation, not a form.
            #
            # form_schema is imported here rather than at module level because it
            # imports _form_frame/_nearby_label_text from this module; a top-level
            # import would be circular.
            form_fields = []
            form_url = page.url
            if not result.get("submitted"):
                try:
                    from form_schema import extract_form_fields
                    form_fields = extract_form_fields(page, ats)
                except Exception:
                    form_fields = []
                try:
                    form_url = getattr(_form_frame(page, ats), "url", "") or page.url
                except Exception:
                    pass

            browser.close()

            if _is_interstitial(form_url) or not form_url:
                form_url = job.get("url", "") or form_url

            outcome = {
                "ats": ats,
                "screenshot": screenshot,
                "apply_url": form_url,
                "form_fields": form_fields,
            }

            if result.get("submitted"):
                return dict(outcome, status="submitted")
            if has_captcha and result.get("attempted_submit"):
                return dict(outcome, status="captcha_gate")
            if result.get("attempted_submit"):
                return dict(outcome, status="submit_unconfirmed")
            return dict(outcome, status="prefilled_pending_review", found_email=found_email)

    except Exception as e:
        print(f"[web_applier] Failed on {job['url']}: {e}")
        return {
            "status": "failed",
            "ats": ats_guess,
            "screenshot": None,
            "apply_url": job.get("url", ""),
            "form_fields": [],
        }
