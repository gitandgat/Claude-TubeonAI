"""Email addresses that appear on job postings but are NOT application inboxes.

Many employers print an accommodation / accessibility contact on every posting,
e.g. the City of Ottawa's "Please contact the Employee Service Centre at
613-580-2424 extension 12211 or via email at esc-cse@ottawa.ca". The apply-email
harvesters (web_applier._pick_apply_email and the job_sources description
fallback) used to accept such an address because its domain matches the
employer's site. On 2026-09-07 that sent a City of Ottawa application to the
City's accommodation inbox instead of through the posting's "Apply now" form,
and tracker.already_emailed() then held back every later City of Ottawa job as
a "duplicate recipient".

is_non_application_inbox() rejects an address when it is on a known list, or
when every place it appears in the posting text is an accommodation /
accessibility sentence (and that sentence doesn't ask for a resume).
"""
import re

KNOWN_NON_APPLICATION_INBOXES = frozenset({
    "esc-cse@ottawa.ca",  # City of Ottawa Employee Service Centre (accommodation requests)
})

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

_ACCOMMODATION_CONTEXT = re.compile(
    r"accommodat|accessib|alternat(?:e|ive) formats?|accessible formats?|disabilit"
    r"|\bAODA\b|human rights code|employee service cent(?:re|er)"
    r"|mesures d.adaptation|adaptation",
    re.I,
)
# A sentence that explicitly asks for a resume/CV is an application instruction
# even if it also mentions accommodation ("send your resume to x; accommodation
# is available on request").
_RESUME_CONTEXT = re.compile(r"r[eé]sum[eé]|\bCV\b|cover letter|curriculum", re.I)
_SENTENCE_BREAK = re.compile(r"[.!?](?:\s+|$)|\n+")


def _occurrence_is_accommodation(text: str, start: int, end: int) -> bool:
    before_pieces = _SENTENCE_BREAK.split(text[max(0, start - 400):start])
    current = before_pieces[-1] + text[start:end] + _SENTENCE_BREAK.split(text[end:end + 160])[0]
    previous = before_pieces[-2] if len(before_pieces) >= 2 else ""
    if _ACCOMMODATION_CONTEXT.search(current):
        return not _RESUME_CONTEXT.search(current)
    if _RESUME_CONTEXT.search(current):
        return False
    return bool(_ACCOMMODATION_CONTEXT.search(previous))


def is_non_application_inbox(address: str, text: str = "") -> bool:
    """True if `address` should never be used as an application inbox.

    With `text` (the posting body), an address is rejected only when it appears
    in the text and every appearance is in an accommodation context. An address
    that doesn't appear in the text (e.g. it came from a mailto link alone) is
    judged by the known list only."""
    if not address:
        return False
    addr = address.strip().strip(".").lower()
    if addr in KNOWN_NON_APPLICATION_INBOXES:
        return True
    if not text:
        return False
    hits = [m for m in re.finditer(re.escape(addr), text, re.I)]
    if not hits:
        return False
    return all(_occurrence_is_accommodation(text, m.start(), m.end()) for m in hits)


def first_application_email(text: str):
    """First email in `text` that isn't a non-application inbox, or None."""
    for m in _EMAIL_RE.finditer(text or ""):
        if not is_non_application_inbox(m.group(), text):
            return m.group()
    return None
