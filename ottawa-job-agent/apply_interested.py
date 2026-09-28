"""Consume the `interested` queue — the missing half of the swipe workflow.

swipe_review.py records right-swipes as `interested` and stops there; its own
docstring says so ("auto-apply-on-interested is a separate step to build").
Nothing read that status afterwards, so every right swipe was a no-op: 8 hand-picked
jobs sat in the tracker while 4 applications had ever gone out. This module is that
missing consumer — it turns a swipe into either a real submission or a one-click
prefilled package with the real apply link.

It is deliberately a standalone CLI rather than a stage inside job_agent.py: the
swipe queue is filled by hand at unpredictable times, and pairing it with the 4-hourly
launchd run would mean a job swiped at 9am waits until noon. Same shape as
resolve_captcha.py, which solves the same "act on one already-known job now" problem.

Usage:
    python3 apply_interested.py                 # package mode — every interested job, NO submissions
    python3 apply_interested.py <job_id>        # just that one
    python3 apply_interested.py --submit        # opt in to submission attempts as well

Package mode is the default on purpose. --submit is the only way a real application
leaves this module, and even then it submits only where the pipeline already has a
verified path: Workday tenants flagged `auto_apply: true` in known_workday.json, and
employer-site forms web_applier can confirm. Everything else — aggregator-only URLs,
CHEO and every other un-proven Workday tenant, anything whose required questions come
back NEEDS INPUT — degrades to the package, which is the honest outcome rather than a
half-filled form left on someone's careers site.

This module never emails an employer. Email drafts are a separate, human-reviewed step.
"""

import sys
from pathlib import Path
from typing import List, Optional, Tuple

import tracker
from application_prefill import build_prefill
from content_generator import tailor_resume, write_cover_letter
from employer_site import is_job_board_url, resolve_employer_apply_url
from job_sources import (_JUNK_COMPANY_PATTERN, _JUNK_TITLE_PATTERN,
                         _NOT_A_POSTING_PATTERN)
from resume_builder import build_pdf
from web_applier import apply_on_website
from workday_applier import apply_on_workday, auto_apply_allowed
from workday_source import is_health_informatics_text

BASE = Path(__file__).parent
RESUME_DIR = BASE / "resumes"

# Mirrors job_agent.RESUME_TAILOR_MIN_SCORE. Health-informatics postings get a tailored
# resume below it too (plan §6: they're the priority track and the tailoring is free —
# it runs on local Ollama).
RESUME_TAILOR_MIN_SCORE = 7


def _load_interested(only_id: Optional[str] = None) -> List[dict]:
    """Tracker records in pipeline job shape. applications.json keys entries by job id
    and stores no id *inside* the entry, so the key has to be merged in — every consumer
    downstream (build_prefill, the appliers, record_application) reads job["id"]."""
    data = tracker._load()
    if only_id:
        record = data.get(only_id)
        if not record:
            raise SystemExit(f"No application record found for job id '{only_id}'.")
        if record.get("status") != "interested":
            print(f"note: {only_id} has status '{record.get('status')}', not 'interested' — processing anyway.")
        return [{**record, "id": only_id}]
    return [{**record, "id": jid} for jid, record in data.items()
            if record.get("status") == "interested"]


def _unactionable_reason(job: dict) -> Optional[str]:
    """Why this entry can never be applied to, or None if it's fine.

    The two checks that matter are the ones the Sep 27 data-quality fix added to
    job_sources: a Web Search result whose url came back as JSON null was stored as the
    literal string "None", and a pay figure ("$25-$30 an hour") was stored where the
    company belongs. Both shapes are aggregator search-page hallucinations with no real
    posting behind them — there is nothing to resolve, so they are reported and skipped
    rather than fed to Playwright. Patterns are imported from job_sources rather than
    re-stated here: one rule in two places is how the tracker filled up with 319 junk
    entries that the discovery guard would have caught."""
    url = (job.get("url") or "").strip()
    if not url or url == "None":
        return "no usable URL (stored as empty/\"None\" — synthesized by the old Web Search bug)"
    company = (job.get("company") or "").strip()
    if _JUNK_COMPANY_PATTERN.search(company):
        return f"company is not a company: {company!r}"
    if _JUNK_TITLE_PATTERN.search(job.get("title") or ""):
        return f"title is not a job title: {job.get('title')!r}"
    if _NOT_A_POSTING_PATTERN.search(url):
        return f"URL is a search/listing page, not one posting: {url}"
    return None


def _build_documents(job: dict) -> Tuple[str, str]:
    """Cover letter + resume PDF path. Both run on local Ollama / fpdf, so cost is not a
    reason to skip either — the old "don't spend API calls on manual-only jobs"
    short-circuit no longer applies (plan, design principles)."""
    cover_letter = write_cover_letter(job)

    category = job.get("category") or "outreach_sales"
    score = job.get("score") or 0
    is_health = is_health_informatics_text(f"{job.get('title', '')} {job.get('description', '')}")

    if score >= RESUME_TAILOR_MIN_SCORE or is_health:
        emphasis = tailor_resume(job)
        resume_pdf = build_pdf(category, summary=emphasis.get("summary"),
                               skills=emphasis.get("skills"), job_id=job["id"])
    else:
        resume_pdf = build_pdf(category)
    return cover_letter, resume_pdf


def _attempt_submit(job: dict, cover_letter: str, resume_pdf: str) -> dict:
    """Route to the applier that matches the job's ATS, exactly as job_agent.py does.
    Returns the applier result dict; callers treat anything but status == "submitted"
    as "fall through to the package"."""
    if job.get("ats") == "workday" or "myworkdayjobs.com" in (job.get("url") or ""):
        if not auto_apply_allowed(job):
            return {"status": "skipped",
                    "reason": "Workday tenant is not flagged auto_apply in known_workday.json"}
        return apply_on_workday(job, cover_letter, resume_pdf)
    return apply_on_website(job, cover_letter, resume_pdf)


def _process(job: dict, submit: bool) -> str:
    """Handle one interested job. Returns the one-line outcome to print in the summary."""
    label = f"{job.get('title', '?')} @ {job.get('company', '?')}"

    skip = _unactionable_reason(job)
    if skip:
        return f"SKIPPED   {label}\n            {skip}"

    resolved = resolve_employer_apply_url(job)
    job = {**job, **resolved}
    apply_url = resolved["apply_url"]
    target = resolved["apply_target"]

    cover_letter, resume_pdf = _build_documents(job)

    # Aggregators are discovery-only, never an apply target — a Playwright run against a
    # LinkedIn/Indeed URL lands on a bot-check interstitial, not a form.
    submittable = submit and target != "job_board" and not is_job_board_url(apply_url)

    if submittable:
        result = _attempt_submit(job, cover_letter, resume_pdf)
        if result.get("status") == "submitted":
            tracker.record_application(job, result.get("ats") or "web")
            return f"SUBMITTED {label}\n            {apply_url}"
        note = f"{result.get('status')}: {result.get('reason') or 'no confirmation seen'}"
        prefill = build_prefill(job, result.get("form_fields"), cover_letter, resume_pdf,
                                result.get("apply_url") or apply_url)
        tracker.update_status(job["id"], "draft_ready",
                             f"package built after submit attempt ({note})")
        return (f"PACKAGE   {label}\n            submit attempt -> {note}\n"
                f"            {prefill['n_ready']} answers ready, {prefill['n_needs_input']} need you\n"
                f"            {prefill['apply_url']}")

    prefill = build_prefill(job, None, cover_letter, resume_pdf, apply_url)
    reason = "aggregator URL — no employer form to submit" if target == "job_board" else \
             ("package mode" if not submit else "no verified submit path")
    tracker.update_status(job["id"], "draft_ready", f"prefilled package built ({reason})")
    return (f"PACKAGE   {label}\n            {reason}\n"
            f"            {prefill['n_ready']} answers ready, {prefill['n_needs_input']} need you\n"
            f"            {prefill['apply_url']}")


def main() -> None:
    args = [a for a in sys.argv[1:]]
    submit = "--submit" in args
    ids = [a for a in args if not a.startswith("--")]
    if len(ids) > 1:
        raise SystemExit(__doc__)

    jobs = _load_interested(ids[0] if ids else None)
    if not jobs:
        print("Nothing swiped right and unprocessed — the interested queue is empty.")
        return

    mode = "SUBMIT (real applications may go out)" if submit else "PACKAGE ONLY (no submissions)"
    print(f"{len(jobs)} interested job(s) · mode: {mode}\n")

    for job in jobs:
        print(_process(job, submit))
        print()

    print("Prefilled packages are in prefilled/. Open the HTML, hit 'Apply here', paste the answers.")
    if not submit:
        print("Re-run with --submit once the packages look right, to let it try submitting too.")


if __name__ == "__main__":
    main()
