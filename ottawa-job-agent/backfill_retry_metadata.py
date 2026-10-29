"""One-shot repair: copy each job's recorded failure reason from
applications.json into seen_jobs.json so retry_policy can classify it.

Why this exists
---------------
`retry_policy` decides whether a previously-seen job may be attempted again by
reading the `no_apply_reason` recorded on its seen_jobs.json entry. job_agent
writes that field from now on, but every entry made before it did has no reason
at all — and an entry with no reason is refused a retry, deliberately, because a
run that cannot tell a bug from a deliberate hand-off must assume the latter.

The result is that the whole existing backlog is frozen, including the 17
GoodLife Workday postings that failed on the Sep 8 combobox-timeout bug and have
never been re-attempted since the fix shipped.

The reason was never lost, only stored elsewhere: applications.json has carried
`no_apply_reason` on every record all along. This script joins the two files on
the job id and writes the reason back where the classifier can see it.

What it does NOT do
-------------------
It does not apply to anything, submit anything, or contact any employer. It only
edits local bookkeeping. Re-opened jobs still go through the whole pipeline on a
later run, still honour `review_only`, and still hit every honesty gate.

It also never invents a classification: `submit_unconfirmed` records, where a
Submit was really clicked and only the confirmation was unreadable, keep their
status and stay permanently refused. Retrying one of those risks a second real
application under his name in an employer's ATS.

Usage
-----
    python3 backfill_retry_metadata.py            # report only, writes nothing
    python3 backfill_retry_metadata.py --apply    # write, after backing up
"""

import json
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import retry_policy

HERE = Path(__file__).parent
SEEN_FILE = HERE / "seen_jobs.json"
APPS_FILE = HERE / "applications.json"

# The generic web-apply failure used to be filed under the catch-all "notified"
# status, which it shares with several by-design hand-offs. job_agent now records
# it as "web_apply_failed"; old records are renamed to match, but only when the
# reason confirms it really was that branch.
_OLD_GENERIC_STATUS = "notified"
_AUTOMATION_FAILURE_REASON = "page or form automation failed"


def load(path: Path) -> dict:
    if not path.exists():
        sys.exit("missing {} — run this from the ottawa-job-agent directory".format(path.name))
    with path.open() as fh:
        return json.load(fh)


def rebuild(seen: dict, apps: dict):
    """Return (updated_seen, reasons_added, statuses_renamed). Pure: builds a new
    dict rather than editing the loaded one, so a failure part-way through can
    never leave seen_jobs.json half-written."""
    updated = dict(seen)
    reasons_added = 0
    statuses_renamed = 0

    for job_id, entry in seen.items():
        if not isinstance(entry, dict) or entry.get("no_apply_reason"):
            continue
        reason = (apps.get(job_id) or {}).get("no_apply_reason")
        if not reason:
            continue

        fresh = dict(entry)
        fresh["no_apply_reason"] = reason
        reasons_added += 1

        if (fresh.get("status") == _OLD_GENERIC_STATUS
                and _AUTOMATION_FAILURE_REASON in reason.lower()):
            fresh["status"] = "web_apply_failed"
            statuses_renamed += 1

        # Start the attempt budget at the one attempt this job has already had,
        # so a re-opened job gets MAX_TRANSIENT_ATTEMPTS - 1 further tries rather
        # than a fresh full allowance.
        fresh.setdefault("attempts", 1)
        updated[job_id] = fresh

    return updated, reasons_added, statuses_renamed


def report(before: dict, after: dict) -> None:
    was = set(retry_policy.select_retries(before))
    now_all = [job_id for job_id, entry in after.items() if retry_policy.should_retry(entry)]
    next_run = retry_policy.select_retries(after)

    print("Retryable jobs before backfill : {}".format(len(was)))
    print("Retryable jobs after backfill  : {}".format(len(now_all)))
    print("Admitted on the next run        : {} (cap is {} per run)".format(
        len(next_run), retry_policy.MAX_RETRIES_PER_RUN))
    print()

    grouped = Counter()
    for job_id in now_all:
        entry = after[job_id]
        grouped[(entry.get("status"), (entry.get("no_apply_reason") or "")[:60])] += 1
    print("Newly retryable, by recorded reason:")
    for (status, reason), count in grouped.most_common():
        print("   {:4d}  {:<26} {}".format(count, status, reason))

    print()
    print("First {} to be re-opened:".format(len(next_run)))
    for job_id in next_run:
        entry = after[job_id]
        print("   {} at {}  [{}]".format(
            entry.get("title", "?"), entry.get("company", "?"), entry.get("date", "?")))


def main() -> None:
    apply_changes = "--apply" in sys.argv[1:]

    seen = load(SEEN_FILE)
    apps = load(APPS_FILE)
    updated, reasons_added, statuses_renamed = rebuild(seen, apps)

    print("seen_jobs.json entries        : {}".format(len(seen)))
    print("applications.json records     : {}".format(len(apps)))
    print("Reasons copied across         : {}".format(reasons_added))
    print("Statuses renamed to web_apply_failed: {}".format(statuses_renamed))
    print()
    report(seen, updated)

    if not apply_changes:
        print()
        print("DRY RUN — nothing written. Re-run with --apply to save.")
        return

    backup = SEEN_FILE.with_suffix(
        ".json.bak-{}".format(datetime.now().strftime("%Y%m%d-%H%M%S")))
    shutil.copy2(SEEN_FILE, backup)
    SEEN_FILE.write_text(json.dumps(updated, indent=2))
    print()
    print("Written. Backup saved to {}".format(backup.name))


if __name__ == "__main__":
    main()
