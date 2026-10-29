#!/usr/bin/env python3
"""Ottawa Job Application Agent — runs daily via LaunchAgent."""

import json
import os
import re
import subprocess
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Validate required env vars
required = ["SERPER_API_KEY", "GMAIL_APP_PASSWORD", "OUTLOOK_APP_PASSWORD"]
missing = [k for k in required if not os.environ.get(k)]
if missing:
    print(f"[job_agent] Missing env vars: {', '.join(missing)}")
    sys.exit(1)

from agent_config import is_review_only, mark_serper_alert_shown, should_alert_serper_exhausted
from autofill_sheet import build_autofill_sheet
from ats_boards import AtsBoardsSource, discover_boards_from_jobs
from content_generator import score_fit, tailor_resume, write_cover_letter, write_email_subject
from application_prefill import build_prefill
from email_sender import draft_application, send_digest
from employer_site import resolve_employer_apply_url
from health_boards_source import HealthBoardsSource
from job_sources import JobSources
from jobbank_apply import apply_jobbank_direct
from jobbank_source import JobBankSource
import jobbank_session
from microsite_builder import build_index, build_microsite
from qualification_gate import check_qualification_gate
from resume_builder import build_pdf
import retry_policy
from walkability import classify_commute, commute_score_adjustment
from web_applier import apply_on_website
from workday_applier import apply_on_workday
from workday_source import (WorkdaySource, discover_workday_tenants_from_jobs,
                            is_health_informatics_text)
import tracker
from run_history import record_run

SEEN_FILE = Path(__file__).parent / "seen_jobs.json"

# Minimum fit score to act on a job (0–10)
MIN_SCORE = 5

# Minimum fit score to build a standout microsite + video script
MICROSITE_MIN_SCORE = 8

# Minimum fit score to spend a Haiku call bespoke-tailoring the resume PDF.
# Below this, jobs still get a real application with the plain per-category
# resume (cached, no per-job file) — avoids piling up a unique tailored PDF
# for every single job when most of the fit difference within a category is
# marginal.
RESUME_TAILOR_MIN_SCORE = 7

# Health informatics / health data is the priority track. score_fit's prompt
# already names it top priority, but the model's score alone left these postings
# indistinguishable from a customer-service job in digest order — this is the
# deterministic thumb on the scale that actually sorts them to the top.
HEALTH_TRACK_BOOST = 2

# Live base URL where published microsites are served (public Vercel project)
LIVE_BASE = "https://microsites-gitandgats-projects.vercel.app"

# Rare-posting categories: never skipped on fit score, and flagged as ★ RARE in
# the digest. They auto-apply like everything else (fully hands-off mode).
ALWAYS_NOTIFY_CATEGORIES = {"thai_embassy"}


def is_expired(job: dict) -> bool:
    """Return True if the job's application deadline has passed or it's marked closed."""
    if job.get("status") == "closed":
        return True

    deadline = job.get("deadline")
    if not deadline:
        return False  # no deadline known — keep, but flag in digest

    m = re.search(r"\d{4}-\d{2}-\d{2}", deadline)
    if not m:
        return False
    try:
        dl = datetime.strptime(m.group(), "%Y-%m-%d").date()
        return dl < date.today()
    except ValueError:
        return False


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)


def load_seen() -> dict:
    if SEEN_FILE.exists():
        try:
            return json.loads(SEEN_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_seen(seen: dict):
    SEEN_FILE.write_text(json.dumps(seen, indent=2))


def failure_seen_entry(job: dict, status: str, score, reason: str, prior) -> dict:
    """The seen_jobs.json entry for a job that finished a run without being
    applied to.

    Carries the two extra fields retry_policy needs on a later run: the reason
    the attempt ended, and how many real attempts this job has now had. Without
    the reason recorded here, a future run cannot tell a job that broke on a bug
    from one that was deliberately left to a human, and must therefore refuse to
    retry either — which is exactly how the 17 GoodLife postings got stuck.
    """
    return {
        "status": status,
        "score": score,
        "date": str(datetime.now().date()),
        "title": job["title"],
        "company": job["company"],
        "no_apply_reason": reason,
        "attempts": retry_policy.next_attempt_count(prior, reason),
    }


def attach_prefill(job_with_content: dict, cover_letter: str, resume_pdf: str,
                   form_fields: Optional[list] = None, apply_url: str = ""):
    """Build the prefilled application package for a job that wasn't submitted, and
    put the real apply link at the front of its digest next_step.

    Every card that isn't a confirmed submission is something Sahawat has to finish
    by hand, and the old cards gave him a posting URL and a generic autofill sheet —
    so the finishing step still meant re-reading the form and re-typing answers he'd
    already given a dozen times. This turns each of those into a one-sitting task:
    the exact link, every answer the engine could fill honestly, and the handful it
    genuinely can't.

    form_fields comes from the Playwright attempt when it reached a real form; None
    means build from the portal's typical question set instead, which build_prefill
    labels as such so nothing is passed off as the posting's real questions.

    apply_url likewise comes from the attempt: the page the form actually lives on
    after following the Apply button, which is usually several redirects deeper than
    the posting URL. Empty falls back to the job's own url inside build_prefill.

    Mutates job_with_content in place, the way the surrounding branches already do,
    and keeps whatever branch-specific instruction was already set (running
    resolve_captcha.py, re-checking a Direct Apply, etc.) after the apply line.
    Never raises: the package is a convenience layered on an already-honest notify
    card, so a failure here must not cost him the card.
    """
    # The web-apply branches record the detected portal as web_apply_ats; that's the
    # key that decides whether the typical question set includes Workday's extras.
    if not job_with_content.get("ats") and job_with_content.get("web_apply_ats"):
        job_with_content["ats"] = job_with_content["web_apply_ats"]

    try:
        prefill = build_prefill(job_with_content, form_fields, cover_letter, resume_pdf, apply_url)
    except Exception as e:
        log(f"  Prefill package failed ({e}) — sending the card without it")
        return

    job_with_content["prefill"] = prefill
    job_with_content["apply_url"] = prefill["apply_url"]
    job_with_content["prefill_path"] = prefill["html"]

    counts = f"{prefill['n_ready']} answers prefilled, {prefill['n_needs_input']} need your input"
    if prefill["questions_are_typical"]:
        counts += " (typical questions for this portal — the real form may differ)"
    apply_line = f"Apply here → {prefill['apply_url']}. {counts} (see attached)."

    existing = (job_with_content.get("next_step") or "").strip()
    job_with_content["next_step"] = f"{apply_line} {existing}".strip()
    log(f"  Prefill package: {prefill['n_ready']} ready · {prefill['n_needs_input']} need input")


def run(only_categories: Optional[set] = None):
    log("=== Ottawa Job Agent starting ===")
    if only_categories:
        log(f"  Scoped run — categories: {sorted(only_categories)}")

    seen = load_seen()

    # seen_jobs.json is permanent by design, which is right for a job that truly
    # finished and wrong for one that failed on a bug: the 17 GoodLife postings
    # that hit the Sep 8 combobox-timeout were never re-attempted once the fix
    # shipped, because their ids were already recorded. retry_policy re-opens
    # exactly those — a run that broke before submitting anything — and never one
    # that may already have put an application in front of an employer. The set is
    # subtracted from every source's skip_ids as well, since a source that skips
    # the id never gives the pipeline a chance to reconsider it.
    retry_ids = set(retry_policy.select_retries(seen))
    skip_ids = set(seen) - retry_ids
    if retry_ids:
        log(f"Re-opening {len(retry_ids)} previously-failed job(s) for another attempt")
        for job_id in sorted(retry_ids):
            prior = seen[job_id]
            log(f"  RETRY: {prior.get('title', '?')} at {prior.get('company', '?')} "
                f"— was {prior.get('status')} "
                f"({prior.get('no_apply_reason') or 'no reason recorded'})")

    alerts = []

    if is_review_only():
        log("  ⚠ REVIEW-ONLY mode active — forms will be filled but not submitted (toggle: python3 agent_config.py off)")

    log("Fetching jobs from all sources...")
    sources = JobSources()
    all_jobs = sources.fetch_all(only_categories)
    log(f"  Web search: {len(all_jobs)} jobs")
    if sources.credits_exhausted:
        msg = "Serper search credits are exhausted — web search is contributing 0 jobs until you buy more. The free tier is a one-time 2,500-query grant, not a monthly quota, so this will not resolve itself: add prepaid credits at serper.dev/api-key (ATS Direct and Job Bank keep running unaffected)."
        log(f"  ⚠ {msg}")
        if should_alert_serper_exhausted():
            alerts.append(msg)
            mark_serper_alert_shown()

    # Direct-ATS boards (Greenhouse/Lever public JSON APIs). Grows its own token
    # registry from today's web-search hits, then polls every known token directly
    # for the full, exact, structured listing — no LLM parsing, no extra Serper
    # cost. Wrapped like Job Bank so an outage here can't take down the run.
    # Skipped on a scoped run — its token registry spans every category ever
    # discovered, and its jobs are tagged "ats_direct" rather than the category
    # that found them, so there's no way to keep it in-scope; the category
    # filter below would just discard everything it returns anyway.
    if not only_categories:
        try:
            new_boards = discover_boards_from_jobs(all_jobs)
            if new_boards:
                log(f"  ATS boards: discovered {new_boards} new board(s)")
            ats_jobs = AtsBoardsSource().fetch_all(skip_ids=skip_ids)
            log(f"  ATS Direct: {len(ats_jobs)} jobs")
            all_jobs = all_jobs + ats_jobs
        except Exception as e:
            log(f"  ATS boards source failed (continuing without it): {e}")

    # Workday tenants polled directly (GoodLife + CHEO today). This is the only
    # source feeding the two priority tracks — Serper is out of credits and no
    # Ottawa health employer is on Greenhouse — so it runs on scoped runs too,
    # unlike ATS Direct: Workday jobs carry a real category, so the filter below
    # keeps them in scope instead of discarding them. Wrapped like Job Bank.
    try:
        new_tenants = discover_workday_tenants_from_jobs(all_jobs)
        if new_tenants:
            log(f"  Workday: discovered {new_tenants} new tenant(s)")
        workday_jobs = WorkdaySource().fetch_all(skip_ids=skip_ids, categories=only_categories)
        log(f"  Workday Direct: {len(workday_jobs)} jobs")
        all_jobs = all_jobs + workday_jobs
    except Exception as e:
        log(f"  Workday source failed (continuing without it): {e}")

    # Ottawa health employers' own boards (CIHI, City of Ottawa, The Royal) —
    # the second supply line for the health-informatics track, added Sept 2026
    # once every CHEO posting had been seen. Jobs carry a real category, so
    # it runs on scoped runs like Workday does. Wrapped like the others.
    try:
        board_jobs = HealthBoardsSource().fetch_all(skip_ids=skip_ids, categories=only_categories)
        log(f"  Health boards: {len(board_jobs)} jobs")
        all_jobs = all_jobs + board_jobs
    except Exception as e:
        log(f"  Health boards source failed (continuing without it): {e}")

    # Job Bank (real government listings, no bot-block). Wrapped so an outage here
    # never takes down the daily run — web search still carries it.
    try:
        jobbank_jobs = JobBankSource().fetch_all(skip_ids=skip_ids, categories=only_categories)
        log(f"  Job Bank: {len(jobbank_jobs)} jobs")
        all_jobs = all_jobs + jobbank_jobs
    except Exception as e:
        log(f"  Job Bank source failed (continuing without it): {e}")

    # Dedup across sources by id
    seen_ids = set()
    deduped = []
    for j in all_jobs:
        if j["id"] not in seen_ids:
            seen_ids.add(j["id"])
            deduped.append(j)
    all_jobs = deduped

    if only_categories:
        all_jobs = [j for j in all_jobs if j["category"] in only_categories]
    log(f"Found {len(all_jobs)} total jobs across all sources")

    new_jobs = [j for j in all_jobs if j["id"] not in skip_ids]
    reopened = sum(1 for j in new_jobs if j["id"] in retry_ids)
    log(f"New (unseen) jobs: {len(new_jobs) - reopened}"
        + (f" | re-opened for retry: {reopened}" if reopened else ""))

    # Drop expired / closed postings before anything else
    expired = 0
    fresh_jobs = []
    for j in new_jobs:
        if is_expired(j):
            log(f"  EXPIRED — skipping: {j['title']} at {j['company']} (deadline {j.get('deadline')}, status {j.get('status')})")
            seen[j["id"]] = {
                "status": "expired",
                "deadline": j.get("deadline"),
                "date": str(datetime.now().date()),
                "title": j["title"],
                "company": j["company"],
            }
            expired += 1
        else:
            fresh_jobs.append(j)
    log(f"Expired dropped: {expired} | Fresh jobs to evaluate: {len(fresh_jobs)}")

    applied = []
    notify = []
    skipped = 0
    built_microsite = False

    for job in fresh_jobs:
        log(f"Evaluating: {job['title']} at {job['company']} [{job['source']}]")

        # Employer website first. A web-search hit is usually a job-board *mirror*
        # of a posting that also lives on the company's own Greenhouse/Lever/Workday
        # board; the resolver swaps in that real posting when the registry knows the
        # company, and labels where the application actually has to happen. Rebound
        # rather than mutated so `fresh_jobs` keeps the URL the job was discovered at.
        route = resolve_employer_apply_url(job)
        if route["apply_url"] and route["apply_url"] != job.get("url"):
            log(f"  Employer posting found — applying there instead: {route['apply_url']}")
            job = {**job, "discovery_url": job.get("url", ""), "url": route["apply_url"]}
        job = {**job, "apply_target": route["apply_target"]}

        # A job_board target means every attempt would land on a bot-check page, so
        # don't spend one — unless the posting also carried an apply-email, which is
        # still a real, honest way in and is handled further down.
        if job["apply_target"] == "job_board" and not job.get("apply_email"):
            job = {
                **job,
                "no_auto_apply": True,
                "no_apply_reason": job.get(
                    "no_apply_reason",
                    "job board only — no employer application form found for this company",
                ),
            }

        # Hard qualification gate — rule out postings with a real, stated
        # mandatory requirement he can't honestly meet (missing licence, unmet
        # years-of-experience floor, required degree field with no equivalency
        # clause), before spending a scoring/cover-letter/resume LLM call on
        # them. Per his "no need to match my background, any job I can do"
        # instruction this is about hard mismatches only, never theme/fit.
        gate = check_qualification_gate(job.get("description", ""))
        if gate["verdict"] == "ruled_out":
            failed = [r for r in gate["requirements"] if r["verdict"] == "NO"]
            reason = "; ".join(f"{r['requirement']} — {r['reason']}" for r in failed)
            log(f"  RULED OUT (qualification mismatch): {reason}")
            seen[job["id"]] = {
                "status": "ruled_out_qualification",
                "reason": reason,
                "date": str(datetime.now().date()),
                "title": job["title"],
                "company": job["company"],
            }
            save_seen(seen)
            skipped += 1
            continue
        if gate["verdict"] == "uncertain":
            uncertain = [r for r in gate["requirements"] if r["verdict"] == "UNCERTAIN"]
            note = "; ".join(f"{r['requirement']} — {r['reason']}" for r in uncertain)
            log(f"  Qualification uncertain (flagged for your review): {note}")
            job = {**job, "qualification_note": note}

        # Score fit
        score = score_fit(job)
        log(f"  Fit score: {score}/10")

        # Deterministic adjustments on top of the model's score. score_fit already
        # *tells* the model health informatics is top priority, but nothing acted on
        # it downstream, so those postings sank into the same middle of the digest as
        # everything else. Order matters: the health boost lands first (so it applies
        # to the raw fit, including the CHIM cap score_fit deliberately imposes), then
        # commute, then route.
        commute = classify_commute(
            " ".join([job.get("location", ""), job.get("title", ""), job.get("description", "")])
        )
        is_health = is_health_informatics_text(f"{job.get('title', '')} {job.get('description', '')}")
        # health_track rides along on the job so the digest can break score ties in
        # the priority track's favour — a GoodLife 8 shouldn't sit above a health
        # informatics 8.
        job = {**job, "commute": commute, "health_track": is_health}

        adjustments = []
        if is_health:
            adjustments.append(("health informatics — priority track", HEALTH_TRACK_BOOST))
        commute_delta = commute_score_adjustment(commute["mode"])
        if commute_delta:
            adjustments.append((f"commute: {commute['label']}", commute_delta))
        # A job board listing is worth less than the same role on the employer's own
        # site: he has to re-key everything into whatever the board wants, and those
        # forms are the ones that silently drop applications.
        if job["apply_target"] == "job_board":
            adjustments.append(("job board only — no employer form", -1))

        for reason, delta in adjustments:
            adjusted = max(0, min(10, score + delta))
            if adjusted != score:
                log(f"  Score {score} -> {adjusted} ({reason})")
            score = adjusted

        # Always notify for rare/special categories or flagged jobs
        is_special = job["category"] in ALWAYS_NOTIFY_CATEGORIES or job.get("always_notify", False)

        if score < MIN_SCORE and not is_special:
            log(f"  Skipping (score below {MIN_SCORE})")
            seen[job["id"]] = {
                "status": "skipped",
                "score": score,
                "date": str(datetime.now().date()),
                "title": job["title"],
                "company": job["company"],
            }
            save_seen(seen)
            skipped += 1
            continue

        # Some postings can't be auto-applied honestly (aggregator reposts, Job Bank
        # Direct Apply that needs your own sign-in, or in-person/mail/phone only).
        # Job Bank Direct Apply postings ARE attemptable once Sahawat has captured
        # his own session via jobbank_session.py (never his password — see that
        # module's docstring). has_live_session returns instantly with no browser
        # launch when he hasn't opted in yet, so this costs nothing until he does.
        jobbank_attemptable = bool(
            job.get("no_auto_apply")
            and job.get("jobbank_direct_apply")
            and jobbank_session.has_live_session(job["url"])
        )

        # Everything else that can't be auto-applied used to short-circuit right here
        # with no cover letter, no resume and no answers — the reason being that
        # tailoring cost API money and the job wasn't going to be submitted anyway.
        # Generation runs on local Ollama now (free), and these manual-only postings
        # are the majority of what he actually sees, so they get the full package
        # further down instead of a bare link.
        manual_only = bool(job.get("no_auto_apply")) and not jobbank_attemptable
        if manual_only:
            log(f"  Not auto-appliable — {job.get('no_apply_reason', 'manual application required')}")

        # Generate cover letter + resume — but skip the per-job Haiku tailoring
        # for Job Bank Direct Apply jobs. Direct Apply reuses whatever's already
        # on file in the signed-in account and never sees this cover_letter or
        # resume_pdf at all (see jobbank_apply.py's docstring), so tailoring
        # per posting would just be discarded API spend. The plain per-category
        # resume (cached, no Haiku call) is all that's ever needed there.
        if jobbank_attemptable:
            cover_letter = ""
            resume_pdf = build_pdf(job["category"])
            log(f"  Using category resume (Direct Apply can't use tailored content): {resume_pdf}")
        else:
            log("  Generating cover letter...")
            cover_letter = write_cover_letter(job)

            # Bespoke per-job resume PDF only for strong fits — below that,
            # the plain per-category resume (cached, no new file) is applied
            # with just as real, just not a unique PDF for every posting.
            # Health-informatics postings are the one exception to the threshold:
            # it's the track he's actually trying to break into, and the generic
            # resume is what makes a career-changer look unqualified for it.
            if score >= RESUME_TAILOR_MIN_SCORE or is_health:
                log("  Tailoring resume to this posting...")
                tailored = tailor_resume(job)
                resume_pdf = build_pdf(
                    job["category"], summary=tailored["summary"], skills=tailored["skills"], job_id=job["id"]
                )
                log(f"  Resume built: {resume_pdf}")
            else:
                resume_pdf = build_pdf(job["category"])
                log(f"  Using category resume (score {score} below tailoring threshold): {resume_pdf}")

        job_with_content = {
            **job,
            "score": score,
            "cover_letter": cover_letter,
            "resume_pdf": resume_pdf,
        }

        # For high-fit jobs, build a standout microsite + personal video script
        if score >= MICROSITE_MIN_SCORE:
            log("  High fit — building standout microsite + video script...")
            try:
                ms = build_microsite(job)
                job_with_content["microsite_path"] = ms["path"]
                job_with_content["microsite_slug"] = ms["slug"]
                job_with_content["microsite_url"] = f"{LIVE_BASE}/{ms['slug']}"
                job_with_content["video_script"] = ms["video_script"]
                built_microsite = True
                log(f"  Microsite built: {ms['path']}")
            except Exception as e:
                log(f"  Microsite failed: {e}")

        # Rare categories are applied to automatically like everything else,
        # but carry a flag so the digest calls them out prominently.
        job_with_content["rare_category"] = is_special

        # Manual-only postings never reach a form the agent can read, so the package
        # is built from the portal's typical question set rather than the posting's
        # own — build_prefill labels it that way on the sheet.
        if manual_only:
            job_with_content["next_step"] = (
                "Nothing was submitted for this one — "
                f"{job.get('no_apply_reason', 'it needs a manual application')}."
            )
            attach_prefill(job_with_content, cover_letter, resume_pdf)
            notify.append(job_with_content)
            seen[job["id"]] = {
                "status": "manual_only",
                "score": score,
                "date": str(datetime.now().date()),
                "title": job["title"],
                "company": job["company"],
            }
            save_seen(seen)
            tracker.record_pending(job_with_content)
            continue

        # Auto-apply if we have an email address
        dup_jid = tracker.already_emailed(job.get("apply_email", "")) if job.get("apply_email") else None
        if dup_jid:
            log(f"  Skipping send — already emailed {job['apply_email']} for job {dup_jid}; holding for manual review")
            job_with_content["no_apply_reason"] = (
                f"already sent an application to {job['apply_email']} for a previous job "
                "(likely a re-scraped duplicate of the same posting) — review manually if this is genuinely a different role"
            )
            job_with_content["next_step"] = (
                f"If this is really a different opening, copy the cover letter below and email it yourself to "
                f"{job['apply_email']} — resume attached to this email."
            )
            notify.append(job_with_content)
            seen[job["id"]] = {
                "status": "notify_duplicate_recipient",
                "score": score,
                "date": str(datetime.now().date()),
                "title": job["title"],
                "company": job["company"],
            }
            save_seen(seen)
            tracker.record_pending(job_with_content)
        elif job.get("apply_email"):
            # Never sent automatically — an outbound email to a real employer is
            # irreversible once it lands, so this posting's apply-by-email flow
            # goes only as far as a Gmail draft; Sahawat reviews and sends it
            # himself (feedback_no_autonomous_email_send).
            subject = write_email_subject(job)
            drafted = draft_application(job, cover_letter, resume_pdf, subject)
            if drafted:
                log(f"  ✓ Draft ready in Gmail for {job['apply_email']} (not sent — needs your review)")
                job_with_content["no_apply_reason"] = "this posting wants an emailed application — a draft is waiting in your Gmail"
                job_with_content["next_step"] = (
                    f"Open your Gmail Drafts folder, review the message addressed to {job['apply_email']}, "
                    "then hit send yourself."
                )
                notify.append(job_with_content)
                seen[job["id"]] = {
                    "status": "notify_draft_ready",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                    "draft_to": job["apply_email"],
                }
                save_seen(seen)
                tracker.record_draft(job_with_content, job["apply_email"])
            else:
                log(f"  ✗ Failed to create Gmail draft for {job['apply_email']}")
                job_with_content["no_apply_reason"] = "application email draft failed to create"
                job_with_content["next_step"] = (
                    f"Copy the cover letter below and email it yourself to {job['apply_email']} "
                    "— resume attached to this email."
                )
                notify.append(job_with_content)
                seen[job["id"]] = {
                    "status": "notify_draft_failed",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                }
                save_seen(seen)
                tracker.record_pending(job_with_content)
        elif jobbank_attemptable:
            # Direct Apply on Job Bank itself, using the saved session — never
            # Sahawat's password (see jobbank_session.py's docstring).
            log("  Attempting Job Bank Direct Apply (saved session)...")
            result = apply_jobbank_direct(job, cover_letter, resume_pdf)
            job_with_content["web_apply_ats"] = result["ats"]
            job_with_content["web_apply_screenshot"] = result.get("screenshot")

            if result["status"] == "submitted":
                log("  ✓ Submitted via Job Bank Direct Apply")
                seen[job["id"]] = {
                    "status": "applied_web",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                    "applied_via": "jobbank_direct",
                }
                save_seen(seen)
                tracker.record_application(job_with_content, "jobbank_direct")
                applied.append(job_with_content)
            elif result["status"] == "submit_unconfirmed":
                log("  ~ Direct Apply clicked (Job Bank) — no confirmation text appeared")
                job_with_content["no_apply_reason"] = (
                    "Direct Apply was clicked on Job Bank, but the confirmation text didn't "
                    "appear afterward — it may or may not have gone through, check manually"
                )
                job_with_content["next_step"] = (
                    "Check your Job Bank account's Applications tab — if this posting isn't "
                    "listed there, open it and click Direct Apply again."
                )
                attach_prefill(job_with_content, cover_letter, resume_pdf)
                notify.append(job_with_content)
                seen[job["id"]] = {
                    "status": "submit_unconfirmed",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                }
                save_seen(seen)
                tracker.record_pending(job_with_content)
            else:
                # "blocked", "failed", or the session expired mid-run ("no_session") —
                # fall back to the same honest FYI path as any other manual_only job.
                log(f"  ~ Job Bank Direct Apply couldn't be completed ({result['status']}) — falling back to FYI")
                job_with_content["no_apply_reason"] = job.get(
                    "no_apply_reason", "Job Bank Direct Apply — requires your Job Bank sign-in"
                )
                job_with_content["next_step"] = (
                    "Open the posting on Job Bank, sign in, and click Direct Apply yourself."
                )
                attach_prefill(job_with_content, cover_letter, resume_pdf)
                notify.append(job_with_content)
                seen[job["id"]] = {
                    "status": "manual_only",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                }
                save_seen(seen)
                tracker.record_pending(job_with_content)
        else:
            # No apply-email — attempt the company's website application form.
            # Workday needs its own applier: the generic path finds no form at
            # all there, because the wizard only exists behind a signed-in
            # candidate account. Same return contract either way, so every
            # outcome branch below is shared.
            if job.get("ats") == "workday":
                log("  Attempting Workday auto-apply (candidate account)...")
                result = apply_on_workday(job, cover_letter, resume_pdf)
            else:
                log("  Attempting website auto-apply...")
                result = apply_on_website(job, cover_letter, resume_pdf)
            job_with_content["web_apply_ats"] = result["ats"]
            job_with_content["web_apply_screenshot"] = result.get("screenshot")

            if result["status"] == "submitted":
                log(f"  ✓ Submitted via website ({result['ats']})")
                seen[job["id"]] = {
                    "status": "applied_web",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                    "applied_via": result["ats"],
                }
                save_seen(seen)
                tracker.record_application(job_with_content, result["ats"])
                applied.append(job_with_content)
            elif result["status"] == "captcha_gate":
                log(f"  ✋ Captcha gate ({result['ats']}) — needs a human to solve it live")
                job_with_content["no_apply_reason"] = (
                    "the site demands a captcha, which only a human may answer — the "
                    "headless run's fill doesn't survive to reopen, so this needs a live "
                    "session: run `python3 resolve_captcha.py " + job["id"] + "`"
                )
                job_with_content["next_step"] = (
                    "Run `python3 resolve_captcha.py " + job["id"] + "` — it reopens the "
                    "application in a visible browser, auto-fills it fresh, and pauses on "
                    "the captcha for you to solve and click Submit."
                )
                attach_prefill(job_with_content, cover_letter, resume_pdf,
                               result.get("form_fields"), result.get("apply_url", ""))
                notify.append(job_with_content)
                seen[job["id"]] = failure_seen_entry(
                    job, "captcha_gate", score,
                    job_with_content["no_apply_reason"], seen.get(job["id"]))
                save_seen(seen)
                tracker.record_pending(job_with_content)
            elif result["status"] == "submit_unconfirmed":
                log(f"  ~ Form filled + Submit clicked ({result['ats']}) — no confirmation text appeared")
                job_with_content["no_apply_reason"] = (
                    "form filled and Submit clicked, but the site showed no confirmation — "
                    "it may or may not have gone through"
                )
                job_with_content["next_step"] = (
                    "Open the posting and check whether the form still shows your info "
                    "filled in — if so, click Submit again to be sure."
                )
                attach_prefill(job_with_content, cover_letter, resume_pdf,
                               result.get("form_fields"), result.get("apply_url", ""))
                notify.append(job_with_content)
                seen[job["id"]] = failure_seen_entry(
                    job, "submit_unconfirmed", score,
                    job_with_content["no_apply_reason"], seen.get(job["id"]))
                save_seen(seen)
                tracker.record_pending(job_with_content)
            elif result["status"] == "prefilled_pending_review" and result.get("found_email"):
                # The form wasn't submittable, but the posting page names an
                # application inbox — the captcha-free email lane can finish
                # the job fully autonomously instead.
                job["apply_email"] = result["found_email"]
                dup_jid = tracker.already_emailed(result["found_email"])
                if dup_jid:
                    log(f"  Skipping send — already emailed {result['found_email']} for job {dup_jid}; holding for manual review")
                    job_with_content["no_apply_reason"] = (
                        f"already sent an application to {result['found_email']} for a previous job "
                        "(likely a re-scraped duplicate of the same posting) — review manually if this is genuinely a different role"
                    )
                    job_with_content["next_step"] = (
                        f"If this is really a different opening, copy the cover letter below and email it yourself to "
                        f"{result['found_email']} — resume attached to this email."
                    )
                    attach_prefill(job_with_content, cover_letter, resume_pdf,
                                   result.get("form_fields"), result.get("apply_url", ""))
                    notify.append(job_with_content)
                    seen[job["id"]] = {
                        "status": "notify_duplicate_recipient",
                        "score": score,
                        "date": str(datetime.now().date()),
                        "title": job["title"],
                        "company": job["company"],
                    }
                    save_seen(seen)
                    tracker.record_pending(job_with_content)
                    continue

                subject = write_email_subject(job)
                drafted = draft_application(job, cover_letter, resume_pdf, subject)
                if drafted:
                    log(f"  ✓ Draft ready in Gmail for {result['found_email']} (address found on posting page, not sent — needs your review)")
                    job_with_content["no_apply_reason"] = "this posting wants an emailed application — a draft is waiting in your Gmail"
                    job_with_content["next_step"] = (
                        f"Open your Gmail Drafts folder, review the message addressed to {result['found_email']}, "
                        "then hit send yourself."
                    )
                    attach_prefill(job_with_content, cover_letter, resume_pdf,
                                   result.get("form_fields"), result.get("apply_url", ""))
                    notify.append(job_with_content)
                    seen[job["id"]] = {
                        "status": "notify_draft_ready",
                        "score": score,
                        "date": str(datetime.now().date()),
                        "title": job["title"],
                        "company": job["company"],
                        "draft_to": result["found_email"],
                    }
                    save_seen(seen)
                    tracker.record_draft(job_with_content, result["found_email"])
                else:
                    log(f"  ✗ Failed to create Gmail draft for harvested address {result['found_email']}")
                    job_with_content["no_apply_reason"] = (
                        f"posting page names {result['found_email']} but the draft failed to create"
                    )
                    job_with_content["next_step"] = (
                        f"Copy the cover letter below and email it yourself to "
                        f"{result['found_email']} — resume attached to this email."
                    )
                    attach_prefill(job_with_content, cover_letter, resume_pdf,
                                   result.get("form_fields"), result.get("apply_url", ""))
                    notify.append(job_with_content)
                    seen[job["id"]] = {
                        "status": "notify_draft_failed",
                        "score": score,
                        "date": str(datetime.now().date()),
                        "title": job["title"],
                        "company": job["company"],
                    }
                    save_seen(seen)
                    tracker.record_pending(job_with_content)
            elif result["status"] == "prefilled_pending_review":
                # web_applier reaches this after actually filling a form it can't
                # safely submit; workday_applier can reach it before opening a
                # browser at all (no credentials, tenant not approved). Saying
                # "form pre-filled" in that second case would claim work that
                # never happened, so the applier's own reason wins when it gives
                # one — same honesty rule as never calling an unverified submit
                # "submitted".
                reason = result.get("reason") or (
                    "non-standard form — couldn't confirm a name/email field or resume upload "
                    "was actually filled, so auto-submitting couldn't be verified as a real application"
                )
                log(f"  ~ Not auto-submitted ({result['ats']}): {reason}")
                job_with_content["no_apply_reason"] = reason
                job_with_content["next_step"] = (
                    "Open the posting, upload the attached resume, and use the attached "
                    "autofill sheet to copy-paste your info into the form fields."
                )
                attach_prefill(job_with_content, cover_letter, resume_pdf,
                               result.get("form_fields"), result.get("apply_url", ""))
                notify.append(job_with_content)
                seen[job["id"]] = failure_seen_entry(
                    job, "prefilled_pending_review", score, reason, seen.get(job["id"]))
                save_seen(seen)
                tracker.record_pending(job_with_content)
            elif result["status"] == "blocked":
                log(f"  ✗ Posting URL is a job-board bot-check ({result['ats']}) — nothing could be filled")
                job_with_content["web_apply_blocked"] = True
                job_with_content["no_apply_reason"] = (
                    "job-board bot-check page (Glassdoor/ZipRecruiter/Indeed) — "
                    "no real application form reachable by automation"
                )
                job_with_content["next_step"] = (
                    "Open the posting directly in your browser and apply there — the "
                    "attached resume and autofill sheet cover the rest."
                )
                attach_prefill(job_with_content, cover_letter, resume_pdf,
                               result.get("form_fields"), result.get("apply_url", ""))
                notify.append(job_with_content)
                seen[job["id"]] = failure_seen_entry(
                    job, "blocked_manual_only", score,
                    job_with_content["no_apply_reason"], seen.get(job["id"]))
                save_seen(seen)
                tracker.record_pending(job_with_content)
            else:
                log("  ✗ Website auto-apply failed")
                job_with_content["no_apply_reason"] = "page or form automation failed"
                job_with_content["next_step"] = (
                    "Open the posting and apply directly — the attached resume and "
                    "autofill sheet cover the rest."
                )
                attach_prefill(job_with_content, cover_letter, resume_pdf,
                               result.get("form_fields"), result.get("apply_url", ""))
                notify.append(job_with_content)
                # Recorded as "web_apply_failed" rather than the old generic
                # "notified": this branch is the one real automation failure in
                # the notify family, and naming it is what lets retry_policy
                # reconsider it later without also re-opening the by-design
                # hand-offs beside it. Nothing reads these statuses but the
                # retry classifier.
                seen[job["id"]] = failure_seen_entry(
                    job, "web_apply_failed", score,
                    job_with_content["no_apply_reason"], seen.get(job["id"]))
                save_seen(seen)
                tracker.record_pending(job_with_content)

    save_seen(seen)

    # Rebuild the personal pitch hub if any microsites exist
    try:
        index_path = build_index()
        if index_path:
            log(f"Pitch hub updated: {index_path}")
    except Exception as e:
        log(f"Index build failed: {e}")

    # Auto-publish microsites live to Vercel if any were built this run
    if built_microsite:
        log("Publishing microsites to Vercel...")
        try:
            result = subprocess.run(
                ["bash", str(Path(__file__).resolve().parent / "publish.sh")],
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode == 0:
                log(f"  ✓ Microsites published live at {LIVE_BASE}/<slug>")
            else:
                log(f"  ✗ Publish failed (exit {result.returncode}): {result.stderr[-300:]}")
        except Exception as e:
            log(f"  ✗ Publish error: {e}")

    # Refresh the one-click application autofill sheet (kept locally; the web
    # applier's screening answers come from the same source data)
    autofill_html = None
    try:
        autofill = build_autofill_sheet()
        autofill_html = autofill["html"]
        log(f"Autofill sheet refreshed: {autofill_html}")
    except Exception as e:
        log(f"Autofill sheet failed: {e}")

    newly_ghosted = []
    try:
        newly_ghosted = tracker.auto_mark_ghosted()
        if newly_ghosted:
            log(f"Marked {len(newly_ghosted)} application(s) as ghosted (21+ days silent)")
    except Exception as e:
        log(f"Ghost-check failed: {e}")

    tracker_html = None
    try:
        tracker_html = tracker.build_dashboard()
        log(f"Tracker dashboard refreshed: {tracker_html}")
    except Exception as e:
        log(f"Tracker dashboard failed: {e}")

    log(f"Summary — applied: {len(applied)}, couldn't auto-apply: {len(notify)}, skipped: {skipped}, expired: {expired}")

    sent = send_digest(
        applied, notify, len(all_jobs),
        tracker_html=tracker_html, newly_ghosted=newly_ghosted, skipped=skipped,
        alerts=alerts, autofill_html=autofill_html,
    )
    log("Summary sent." if sent else "Quiet run — no email sent.")

    # Refresh the Job-agent dashboard's data files so the UI always reflects
    # today's run without any manual step. SystemExit is caught too: the export
    # raises it when the dashboard repo is missing, and a dashboard problem must
    # never take down the pipeline.
    try:
        import dashboard_export
        dashboard_export.main()
        log("Dashboard data refreshed")
    except (Exception, SystemExit) as e:
        log(f"Dashboard export failed (non-fatal): {e}")

    log("=== Done ===\n")


WATCHDOG_SEC = 90 * 60  # generous: normal runs take 3-50 min


def _arm_watchdog():
    """Hard cap on total run time, mirroring run_verticals.py's fix for the
    same incident class: one hung/glacial network call (SMTP Jul 13, wedged
    Ollama Jul 18) must never be able to eat the schedule — launchd won't
    start the next fire while a previous instance is still alive."""
    import threading

    def _kill():
        log(f"WATCHDOG: run exceeded {WATCHDOG_SEC}s — hard-exiting to protect the schedule")
        sys.stdout.flush()
        os._exit(70)

    t = threading.Timer(WATCHDOG_SEC, _kill)
    t.daemon = True
    t.start()


if __name__ == "__main__":
    import argparse

    _parser = argparse.ArgumentParser(description="Ottawa Job Application Agent")
    _parser.add_argument(
        "--category", action="append", dest="categories",
        help="Scope this run to one category (repeatable). Omit to run all categories.",
    )
    _args = _parser.parse_args()
    _only_categories = set(_args.categories) if _args.categories else None

    _arm_watchdog()
    _start = time.time()
    try:
        run(_only_categories)
        record_run("Job Discovery", "daily fetch", "Success", "Completed successfully",
                   duration_ms=int((time.time() - _start) * 1000))
    except Exception as _e:
        record_run("Job Discovery", "daily fetch", "Failed", str(_e),
                   duration_ms=int((time.time() - _start) * 1000))
        raise
