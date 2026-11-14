"""Assisted apply — one visible browser, a ranked queue, you in the chair.

The daily pipeline runs headless and cannot finish most applications: captchas,
bot-check interstitials and non-standard forms stop it, and they always will.
Its answer so far has been to write a prefilled package to disk. There are over
two hundred of them. Five applications have ever gone out.

This script closes that gap by inverting the model. It opens one visible
browser, walks a ranked queue of live jobs, and for each one fills every field
it can answer honestly from your profile — then stops and hands you the window.
You review what it filled, answer anything it left blank, solve any captcha,
sign anything that needs signing, and click Submit yourself. Close the window to
skip a job and it moves to the next one.

The agent never clicks Submit and never ticks an attestation. That is enforced
by set_assisted_handoff(), not left to configuration.

Usage:
    python3 assisted_apply.py                      # 5 freshest live jobs
    python3 assisted_apply.py --list               # show the queue, open nothing
    python3 assisted_apply.py --limit 10
    python3 assisted_apply.py --category health_informatics
    python3 assisted_apply.py --max-age 14
    python3 assisted_apply.py <job_id> [<job_id> ...]
"""
import argparse
import datetime
import json
from pathlib import Path
from typing import List, Optional

from content_generator import write_cover_letter
from resume_builder import build_pdf
from tracker import record_application, update_status
from web_applier import apply_on_website, set_assisted_handoff

BASE = Path(__file__).resolve().parent
APPLICATIONS_FILE = BASE / "applications.json"
RESUME_DIR = BASE / "resumes"

DEFAULT_LIMIT = 5
# Past this, a posting is usually closed and filling it wastes the one resource
# the whole pipeline is short of: your attention. The backlog is 154 jobs older
# than this, and working them in order is why the queue never gets worked.
DEFAULT_MAX_AGE_DAYS = 30


def _last_seen(record: dict) -> Optional[datetime.date]:
    """Most recent history date, which is as close to 'still live' as we get."""
    for event in reversed(record.get("history") or []):
        stamp = event.get("date")
        if stamp:
            try:
                return datetime.date(*[int(p) for p in str(stamp)[:10].split("-")])
            except (ValueError, TypeError):
                continue
    return None


def build_queue(limit: int, category: Optional[str], max_age_days: int,
                job_ids: Optional[List[str]] = None) -> List[dict]:
    """Freshest-first pending jobs. Explicit ids bypass every filter."""
    data = json.loads(APPLICATIONS_FILE.read_text())

    if job_ids:
        queue = []
        for jid in job_ids:
            record = data.get(jid)
            if not record:
                print("  ! no record for job id '%s' — skipping" % jid)
                continue
            queue.append(dict(record, id=jid))
        return queue

    today = datetime.date.today()
    candidates = []
    for jid, record in data.items():
        if record.get("status") != "pending":
            continue
        if category and record.get("category") != category:
            continue
        seen = _last_seen(record)
        age = (today - seen).days if seen else None
        if age is None or age > max_age_days:
            continue
        candidates.append((age, jid, record))

    candidates.sort(key=lambda row: row[0])
    return [dict(rec, id=jid, _age=age) for age, jid, rec in candidates[:limit]]


def _resume_for(job: dict) -> str:
    path = RESUME_DIR / ("resume_%s_%s.pdf" % (job.get("category"), job["id"]))
    if path.exists():
        return str(path)
    print("  tailored resume not on disk — building category resume...")
    return build_pdf(job.get("category"))


def _describe(job: dict, index: int, total: int) -> None:
    age = job.get("_age")
    print("\n" + "=" * 72)
    print("[%d/%d] %s" % (index, total, job.get("title", "?")))
    print("        %s%s" % (job.get("company", "?"),
                            ("  ·  %dd old" % age) if age is not None else ""))
    print("        %s" % job.get("url", "?"))
    print("=" * 72)


def run_one(job: dict, index: int, total: int) -> str:
    """Fill one application and hand the window over. Returns the outcome key."""
    _describe(job, index, total)
    try:
        resume_pdf = _resume_for(job)
        print("  writing cover letter...")
        cover_letter = write_cover_letter(job)
        print("  opening visible browser...")
        result = apply_on_website(job, cover_letter, resume_pdf,
                                  headless=False, handoff=True)
    except Exception as exc:
        print("  ! failed before handoff: %s" % exc)
        return "error"

    status = result.get("status")
    handoff = result.get("handoff") or ""
    blocked = result.get("needs_input_labels") or []
    if blocked:
        print("  questions left for you: %s" % ", ".join(blocked))

    if status == "submitted" or handoff == "submitted":
        record_application(job, "web:%s (assisted — reviewed and submitted by hand)"
                           % result.get("ats", "?"))
        print("  RECORDED as applied.")
        return "submitted"

    if handoff == "skipped":
        print("  skipped — left pending.")
        return "skipped"

    if handoff == "timeout":
        update_status(job["id"], "pending", "assisted apply: window timed out unsubmitted")
        print("  timed out — left pending.")
        return "timeout"

    print("  no handoff reached (status=%s) — left pending." % status)
    return "no_form"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("job_ids", nargs="*", help="specific job ids; bypasses all filters")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--category")
    parser.add_argument("--max-age", type=int, default=DEFAULT_MAX_AGE_DAYS,
                        dest="max_age")
    parser.add_argument("--list", action="store_true",
                        help="print the queue and exit without opening a browser")
    args = parser.parse_args()

    queue = build_queue(args.limit, args.category, args.max_age, args.job_ids)
    if not queue:
        print("Nothing live to apply to (pending, <= %dd old%s)."
              % (args.max_age, ", category=%s" % args.category if args.category else ""))
        return

    print("Queue (%d):" % len(queue))
    for n, job in enumerate(queue, 1):
        age = job.get("_age")
        print("  %d. %-44s %-22s %s" % (
            n, str(job.get("title"))[:44], str(job.get("company"))[:22],
            ("%dd" % age) if age is not None else "-"))
    if args.list:
        return

    # Interlock: no automatic Submit for the rest of this process, whatever
    # agent_config.json says. You submit; the agent fills.
    set_assisted_handoff(True)

    print("\nThe agent fills each form and stops. You review and Submit.")
    print("Close a window to skip that job.\n")

    tally = {}
    for n, job in enumerate(queue, 1):
        outcome = run_one(job, n, len(queue))
        tally[outcome] = tally.get(outcome, 0) + 1

    print("\n" + "=" * 72)
    print("Done. " + "  ".join("%s=%d" % kv for kv in sorted(tally.items())))
    print("=" * 72)


if __name__ == "__main__":
    main()
