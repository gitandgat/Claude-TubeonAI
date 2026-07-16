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

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Validate required env vars
required = ["SERPER_API_KEY", "GMAIL_APP_PASSWORD", "OUTLOOK_APP_PASSWORD"]
missing = [k for k in required if not os.environ.get(k)]
if missing:
    print(f"[job_agent] Missing env vars: {', '.join(missing)}")
    sys.exit(1)

from autofill_sheet import build_autofill_sheet
from content_generator import score_fit, tailor_resume, write_cover_letter, write_email_subject
from email_sender import send_application, send_digest
from job_sources import JobSources
from jobbank_apply import apply_jobbank_direct
from jobbank_source import JobBankSource
import jobbank_session
from microsite_builder import build_index, build_microsite
from resume_builder import build_pdf
from web_applier import apply_on_website
import tracker
from run_history import record_run

SEEN_FILE = Path(__file__).parent / "seen_jobs.json"
LOG_FILE = Path(__file__).parent / "job_agent.log"

# Minimum fit score to act on a job (0–10)
MIN_SCORE = 5

# Minimum fit score to build a standout microsite + video script
MICROSITE_MIN_SCORE = 8

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
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_seen() -> dict:
    if SEEN_FILE.exists():
        try:
            return json.loads(SEEN_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_seen(seen: dict):
    SEEN_FILE.write_text(json.dumps(seen, indent=2))


def run():
    log("=== Ottawa Job Agent starting ===")

    seen = load_seen()

    alerts = []

    log("Fetching jobs from all sources...")
    sources = JobSources()
    all_jobs = sources.fetch_all()
    log(f"  Web search: {len(all_jobs)} jobs")
    if sources.credits_exhausted:
        msg = "Serper search credits ran out mid-run — some categories were skipped today. Top up at serper.dev or wait for next month's allotment."
        log(f"  ⚠ {msg}")
        alerts.append(msg)

    # Job Bank (real government listings, no bot-block). Wrapped so an outage here
    # never takes down the daily run — web search still carries it.
    try:
        jobbank_jobs = JobBankSource().fetch_all(skip_ids=set(seen))
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
    log(f"Found {len(all_jobs)} total jobs across all sources")

    new_jobs = [j for j in all_jobs if j["id"] not in seen]
    log(f"New (unseen) jobs: {len(new_jobs)}")

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

        # Score fit
        score = score_fit(job)
        log(f"  Fit score: {score}/10")

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

        # Surface everything else FYI with the link — don't burn tailoring API
        # calls or fake an application. Short-circuit before any content generation.
        if job.get("no_auto_apply") and not jobbank_attemptable:
            reason = job.get("no_apply_reason", "manual application required")
            log(f"  Not auto-appliable — {reason}")
            notify.append({**job, "score": score, "rare_category": is_special})
            seen[job["id"]] = {
                "status": "manual_only",
                "score": score,
                "date": str(datetime.now().date()),
                "title": job["title"],
                "company": job["company"],
            }
            continue

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

            log("  Tailoring resume to this posting...")
            tailored = tailor_resume(job)

            resume_pdf = build_pdf(
                job["category"], summary=tailored["summary"], skills=tailored["skills"], job_id=job["id"]
            )
            log(f"  Resume built: {resume_pdf}")

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

        # Auto-apply if we have an email address
        if job.get("apply_email"):
            subject = write_email_subject(job)
            sent = send_application(job, cover_letter, resume_pdf, subject)
            if sent:
                log(f"  ✓ Application sent to {job['apply_email']}")
                seen[job["id"]] = {
                    "status": "applied",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                    "applied_to": job["apply_email"],
                }
                tracker.record_application(job_with_content, job["apply_email"])
                applied.append(job_with_content)
            else:
                log(f"  ✗ Failed to send to {job['apply_email']}")
                job_with_content["no_apply_reason"] = "application email failed to send"
                notify.append(job_with_content)
                seen[job["id"]] = {
                    "status": "notify_send_failed",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                }
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
                tracker.record_application(job_with_content, "jobbank_direct")
                applied.append(job_with_content)
            elif result["status"] == "submit_unconfirmed":
                log("  ~ Direct Apply clicked (Job Bank) — no confirmation text appeared")
                job_with_content["no_apply_reason"] = (
                    "Direct Apply was clicked on Job Bank, but the confirmation text didn't "
                    "appear afterward — it may or may not have gone through, check manually"
                )
                notify.append(job_with_content)
                seen[job["id"]] = {
                    "status": "submit_unconfirmed",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                }
            else:
                # "blocked", "failed", or the session expired mid-run ("no_session") —
                # fall back to the same honest FYI path as any other manual_only job.
                log(f"  ~ Job Bank Direct Apply couldn't be completed ({result['status']}) — falling back to FYI")
                job_with_content["no_apply_reason"] = job.get(
                    "no_apply_reason", "Job Bank Direct Apply — requires your Job Bank sign-in"
                )
                notify.append(job_with_content)
                seen[job["id"]] = {
                    "status": "manual_only",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                }
        else:
            # No apply-email — attempt the company's website application form
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
                tracker.record_application(job_with_content, result["ats"])
                applied.append(job_with_content)
            elif result["status"] == "submit_unconfirmed":
                log(f"  ~ Form filled + Submit clicked ({result['ats']}) — no confirmation text appeared")
                job_with_content["no_apply_reason"] = (
                    "form filled and Submit clicked, but the site showed no confirmation — "
                    "it may or may not have gone through"
                )
                notify.append(job_with_content)
                seen[job["id"]] = {
                    "status": "submit_unconfirmed",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                }
            elif result["status"] == "prefilled_pending_review":
                log(f"  ~ Form pre-filled ({result['ats']}) — no resume-upload field, not safe to auto-submit")
                job_with_content["no_apply_reason"] = (
                    "non-standard form without a resume-upload field — auto-submitting "
                    "couldn't be verified as a real application"
                )
                notify.append(job_with_content)
                seen[job["id"]] = {
                    "status": "prefilled_pending_review",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                }
            elif result["status"] == "blocked":
                log(f"  ✗ Posting URL is a job-board bot-check ({result['ats']}) — nothing could be filled")
                job_with_content["web_apply_blocked"] = True
                job_with_content["no_apply_reason"] = (
                    "job-board bot-check page (Glassdoor/ZipRecruiter/Indeed) — "
                    "no real application form reachable by automation"
                )
                notify.append(job_with_content)
                seen[job["id"]] = {
                    "status": "blocked_manual_only",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                }
            else:
                log("  ✗ Website auto-apply failed")
                job_with_content["no_apply_reason"] = "page or form automation failed"
                notify.append(job_with_content)
                seen[job["id"]] = {
                    "status": "notified",
                    "score": score,
                    "date": str(datetime.now().date()),
                    "title": job["title"],
                    "company": job["company"],
                }

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
    try:
        autofill = build_autofill_sheet()
        log(f"Autofill sheet refreshed: {autofill['html']}")
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

    log("Sending daily summary email...")
    send_digest(
        applied, notify, len(all_jobs),
        tracker_html=tracker_html, newly_ghosted=newly_ghosted, skipped=skipped,
        alerts=alerts,
    )
    log("Summary sent.")

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


if __name__ == "__main__":
    _start = time.time()
    try:
        run()
        record_run("Job Discovery", "daily fetch", "Success", "Completed successfully",
                   duration_ms=int((time.time() - _start) * 1000))
    except Exception as _e:
        record_run("Job Discovery", "daily fetch", "Failed", str(_e),
                   duration_ms=int((time.time() - _start) * 1000))
        raise
