"""Read-only liveness sweep of the tracker backlog. Changes nothing, ever.

Postings in this market live about a week, and the gap between a swipe and the run
that acts on it has been as long as ten days. Discovery was never the bottleneck --
latency is. So the backlog needs re-checking on a schedule, not once: the Sep 29
2026 sweep of 643 entries found 435 of them already closed, and every one had been
sitting at `pending` waiting to be applied to.

Three deliberate safety properties, because this runs over the whole tracker:

  * It never writes. The tracker is loaded, never saved; retiring what this finds is
    a separate, human-approved step. `audit.json` is the only output.
  * It cannot open a browser. `_render_visible_text` is stubbed off, so a 600-entry
    sweep can't spawn 600 Chromium windows. The cost is that bot-walled pages can't
    be settled here -- they are reported `unknown` rather than guessed at, and a
    headed re-check of just those is a much smaller job.
  * It cannot submit. Nothing in this module touches web_applier or workday_applier.

`unknown` is a real verdict, not a failure. Njoyn (CIHI) answers both `requests` and
headless Chromium with a Radware CAPTCHA at HTTP 200 while a *headed* browser loads
the posting fine -- headlessness is what it detects. Calling those closed would throw
away live jobs, which is the same fail-open convention as
job_sources._greenhouse_board_is_live.

Usage:
    python3 audit_pending.py                 # sweep `pending`, write audit.json
    python3 audit_pending.py --status ghosted --out /tmp/ghosted.json
"""

import argparse
import json
import threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import apply_interested as ai
import tracker

DEFAULT_OUT = Path(__file__).parent / "audit.json"

# Health-informatics is the priority track, so the sweep calls it out separately
# rather than leaving it to be found in a 200-line list. Deliberately broader than
# job_agent.is_health_informatics_text, which matches HIM/EMR/clinical-informatics
# *wording* only: that misses a data role at a health employer (CIHI's "Architect,
# Enterprise Architecture" scored 8 and fell outside it), so employers are matched too.
_PRIORITY_TERMS = (
    "health inform", "clinical inform", "health data", "data analyst", "health record",
    "informatics", "decision support", "business intelligence", "abstracting",
    "cheo", "ottawa hospital", "cihi", "bruyere", "montfort", "ontario health",
)


def _bucket_jobs(jobs, workers):
    """Sort every job into live / closed / unknown / junk. Fetches, never writes."""
    walled = set()
    lock = threading.Lock()
    real_get = ai.requests.get

    def recording_get(url, **kwargs):
        """A bot wall answers HTTP 200 with a page that has no job content on it, so
        the gate's own probe would read it as "title is gone" -- i.e. closed. Record
        which URLs did that, so they land in `unknown` instead."""
        resp = real_get(url, **kwargs)
        try:
            if ai._BOT_WALL_PATTERN.search(ai._visible_text(resp.text)):
                with lock:
                    walled.add(url)
        except Exception:
            pass
        return resp

    ai.requests.get = recording_get
    ai._render_visible_text = lambda url: None

    buckets = defaultdict(list)
    candidates = []
    for job in jobs:
        reason = ai._unactionable_reason(job)
        if reason:
            buckets["junk"].append((job, reason))
        else:
            candidates.append(job)
    print("%d unactionable, %d to check" % (len(buckets["junk"]), len(candidates)), flush=True)

    # Warm the Workday tenant caches serially first. Workday is the one ATS whose
    # liveness answer comes from enumerating the tenant's whole req list (HTTP 200 +
    # an empty JS shell is all a dead req returns), and that list is per-tenant, so
    # twelve threads hitting one tenant would fetch the same list twelve times.
    for job in candidates:
        m = ai._WORKDAY_URL.search(job.get("apply_url") or job.get("url") or "")
        if m and (m.group("tenant"), m.group("host"), m.group("site")) not in ai._workday_list_cache:
            ai._workday_live_reqs(m.group("tenant"), m.group("host"), m.group("site"))
    print("workday tenants cached: %d" % len(ai._workday_list_cache), flush=True)

    done = [0]

    def check(job):
        url = job.get("apply_url") or job.get("url") or ""
        try:
            live, why = ai._posting_is_live(job, url)
        except Exception as exc:
            # Fail open: a crashed check is not evidence a job closed.
            live, why = True, "check errored: %s" % exc.__class__.__name__
        with lock:
            done[0] += 1
            if done[0] % 50 == 0:
                print("  ...%d/%d" % (done[0], len(candidates)), flush=True)
        if url in walled:
            return "unknown", job, "bot-walled — inconclusive, needs a headed re-check"
        return ("live" if live else "closed"), job, why

    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for verdict, job, why in pool.map(check, candidates):
                buckets[verdict].append((job, why))
    finally:
        ai.requests.get = real_get
    return buckets


def _report_shared_urls(live):
    """Entries that share one URL under different titles -- the count-inflating shape.

    A careers index page genuinely lists the role, so the gate's title probe passes
    and every entry pointing at it is reported live. URL-shape rules in job_sources
    catch the ones whose address says "index"; this catches the rest by a signal no
    per-job check can see, because it only exists across entries. In the Sep 29 sweep
    it was also how the title-variant duplicates surfaced -- one real Lever posting
    tracked four times under four phrasings of its title -- so a group here means
    "look once", not "discard".
    """
    groups = defaultdict(set)
    for job, _ in live:
        groups[job.get("url") or ""].add((job.get("title") or "").strip().lower())
    shared = {u: t for u, t in groups.items() if len(t) > 1}
    if not shared:
        return
    inflated = sum(len(t) for t in shared.values())
    print("\n=== %d URLs carry more than one tracked title (%d entries) ===" % (len(shared), inflated))
    print("    an index page, or the same posting tracked under title variants — check once, not once each")
    for url, titles in sorted(shared.items(), key=lambda kv: -len(kv[1])):
        print("  %2d  %s" % (len(titles), url))
        for t in sorted(titles):
            print("        - %s" % t[:72])


def main():
    ap = argparse.ArgumentParser(description="Read-only liveness sweep of the tracker backlog.")
    ap.add_argument("--status", default="pending", help="tracker status to sweep (default: pending)")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="where to write the results JSON")
    ap.add_argument("--workers", type=int, default=12, help="parallel fetches (default: 12)")
    args = ap.parse_args()

    ai._LIVENESS_TIMEOUT = 15
    jobs = [dict(rec, id=jid) for jid, rec in tracker._load().items()
            if rec.get("status") == args.status]
    print("%d entries with status %r" % (len(jobs), args.status), flush=True)
    if not jobs:
        return

    buckets = _bucket_jobs(jobs, args.workers)

    print("\n=== verdict ===")
    for name in ("live", "closed", "unknown", "junk"):
        print("%-8s %d" % (name, len(buckets[name])))

    print("\n=== live, by company ===")
    for company, n in Counter(j.get("company") or "?" for j, _ in buckets["live"]).most_common(15):
        print("  %4d  %s" % (n, company))

    print("\n=== live on the priority track ===")
    for job, _ in sorted(buckets["live"], key=lambda t: -(t[0].get("score") or 0)):
        blob = ("%s %s" % (job.get("title") or "", job.get("company") or "")).lower()
        if any(k in blob for k in _PRIORITY_TERMS):
            print("  [%s] %s — %s" % (job.get("score"), job.get("company"), (job.get("title") or "")[:70]))

    _report_shared_urls(buckets["live"])

    out = {name: [{"id": j["id"], "company": j.get("company"), "title": j.get("title"),
                   "score": j.get("score"), "url": j.get("url"), "why": why}
                  for j, why in items] for name, items in buckets.items()}
    Path(args.out).write_text(json.dumps(out, indent=1))
    print("\nfull results: %s" % args.out)
    print("nothing was modified — retiring what this found is a separate, approved step")


if __name__ == "__main__":
    main()
