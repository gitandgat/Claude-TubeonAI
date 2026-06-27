#!/usr/bin/env python3
"""Multi-vertical LinkedIn driver — one post per vertical per day, cross-posted.

The 5/day LinkedIn cap is the design: five content verticals, one day-part slot
each (08:00 / 11:00 / 14:00 / 17:00 / 20:00 ET), all to the one LinkedIn profile
and cross-posted to the shared IG/FB accounts. Each vertical keeps its own
learning loop (winning_patterns.json), so what wins for fitness is learned
separately from what wins for IMG-career content.

This REPLACES the old `run_agent.py --batch 5` (which filled all 5 LinkedIn
slots with Crosswalk-only content).

Usage:
  python run_verticals.py                     # snapshot + learn + post all 5
  python run_verticals.py --dry-run           # generate + print all 5, no posting
  python run_verticals.py --vertical fitness  # just one vertical
  python run_verticals.py --vertical trainer --dry-run
  python run_verticals.py --learn-only        # snapshot + per-vertical learn, no posting
"""

import argparse
import os
import socket
import sys
from datetime import datetime, timedelta

# Bound EVERY network call. A single un-timed-out HTTPS request hung this process
# for 9 DAYS (Jun 17-26 2026) — launchd saw it "running" so it never re-ran, and
# the 5/day cadence silently died. setdefaulttimeout makes any request without an
# explicit timeout fail after 300s instead; the per-vertical try/except then keeps
# the remaining verticals posting.
socket.setdefaulttimeout(300)

from pytz import timezone

# cron runs with a minimal PATH that omits the Python framework bin; make sure
# console scripts the pipeline shells out to (shot-scraper) are findable.
_py_bin = os.path.dirname(os.path.abspath(sys.executable))
if _py_bin not in os.environ.get("PATH", "").split(os.pathsep):
    os.environ["PATH"] = _py_bin + os.pathsep + os.environ.get("PATH", "")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "linkedin_agent"))

from linkedin_agent.config import LINKEDIN_SCHEDULE_TZ, ensure_directories
from linkedin_agent.verticals import all_verticals, get as get_vertical
from linkedin_agent.engine.voice_engine import VoiceEngine
from linkedin_agent.engine.post_writer import PostWriter
from linkedin_agent.engine.infographic import InfographicEngine
from linkedin_agent.scheduler import Scheduler
from linkedin_agent.notifier import Notifier
from linkedin_agent.experiment import EXPERIMENTS, ACTIVE_EXPERIMENT, arm_instruction

_ARMS = list(EXPERIMENTS[ACTIVE_EXPERIMENT]["arms"].keys())

# Single-draft generation is stochastic — a draft can miss one gate (e.g. no
# closing "?"). Each vertical owns exactly one daily slot, so we regenerate a few
# times rather than leave the slot empty.
MAX_TRIES = 3

# When a direct-API "philosophy" post publishes to LinkedIn on a given day it
# eats one of the 5 LinkedIn slots. To keep the day at exactly 5 (no collision,
# no bump), the verticals yield a slot in this order. health yields first; mind
# is protected ahead of health/fitness; crosswalk (revenue) and trainer (hiring)
# are protected and never yield. Self-clears once the queue is exhausted, so no
# rotting hardcoded dates.
YIELD_ORDER = ["health", "fitness", "mind", "trainer", "crosswalk"]


def _direct_posts_due_today() -> int:
    """How many direct-API (philosophy-queue) posts are scheduled for TODAY.

    The queue dates one philosophy post per chosen day, so this is the number
    of LinkedIn slots to yield today. We match the date EXACTLY (not <=today) on
    purpose: a stalled scheduler must not let pending past-due posts pile up and
    progressively starve the verticals. The rare "scheduler missed a day then
    flushes a backlog" case degrades to a graceful bump, not starvation.
    Returns 0 when the queue is missing or has nothing dated today.
    """
    import json
    from datetime import date
    qfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "linkedin_post_queue.json")
    if not os.path.exists(qfile):
        return 0
    try:
        with open(qfile) as f:
            data = json.load(f)
    except Exception:
        return 0
    today = date.today().isoformat()
    return sum(1 for p in data
               if p.get("status") == "pending" and p.get("date") == today)


def slot_for(slot_time: str, tz_name: str = LINKEDIN_SCHEDULE_TZ) -> str:
    """Today's `HH:MM` slot in ET, or tomorrow's if it's already passed."""
    tz = timezone(tz_name)
    now = datetime.now(tz)
    hh, mm = (int(x) for x in slot_time.split(":"))
    slot = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if slot <= now:
        slot += timedelta(days=1)
    return slot.isoformat()


def run_vertical(vertical, voice_profile: dict, scheduler: Scheduler,
                 infographic: InfographicEngine, dry_run: bool) -> dict:
    """Generate one post for a vertical and schedule it at its slot."""
    ordinal = datetime.now().date().toordinal()
    theme = vertical.theme_for(ordinal)
    # Spread experiment arms across verticals AND days (index keeps the 5 daily
    # posts on different arms within the same run).
    arm = _ARMS[(ordinal + list(all_verticals()).index(vertical)) % len(_ARMS)]
    slot = slot_for(vertical.slot_time)

    print("\n" + "=" * 64)
    print(f"VERTICAL: {vertical.key} — {vertical.name}")
    print(f"  theme: {theme}")
    print(f"  slot:  {slot[:16]} ET   arm: {arm}")
    print("=" * 64)

    writer = PostWriter(voice_profile, vertical=vertical)
    # The theme doubles as the "starting image" — the system prompt turns it into
    # a first-person scene; no IMG-specific research dependency for non-Crosswalk.
    result = None
    for attempt in range(1, MAX_TRIES + 1):
        result = writer.write_with_3_qa_rounds(
            theme, theme, experiment_instruction=arm_instruction(arm)
        )
        if result.get("success"):
            break
        print(f"  ↻ [{vertical.key}] attempt {attempt}/{MAX_TRIES} failed validation"
              + (" — retrying" if attempt < MAX_TRIES else ""))

    if not result or not result.get("success"):
        print(f"✗ [{vertical.key}] no valid post after {MAX_TRIES} tries — skipping slot")
        return {"vertical": vertical.key, "success": False, "reason": "validation"}

    post_content = result["post"]

    # Infographic gives IG/FB the image they require to receive the cross-post.
    image_path = infographic.generate_infographic(theme, theme)
    if not image_path:
        print("⚠ No infographic (shot-scraper unavailable) — LinkedIn only, no cross-post")

    if dry_run:
        print(f"\n[DRY RUN] Would schedule [{vertical.key}] at {slot[:16]} ET")
        print(f"  cross-post: {', '.join(vertical.crosspost) if image_path else 'none (no image)'}")
        print("-" * 64)
        print(post_content)
        print("-" * 64)
        print(f"  first comment: {vertical.first_comment[:90]}...")
        return {"vertical": vertical.key, "success": True, "dry_run": True,
                "post": post_content, "slot": slot}

    sched = scheduler.schedule_post(post_content, image_path=image_path,
                                    scheduled_for=slot, vertical=vertical)
    if sched.get("success"):
        scheduler.log_scheduled_post(
            sched, theme, theme, post_content,
            experiment=ACTIVE_EXPERIMENT, arm=arm, vertical=vertical,
        )
    return {"vertical": vertical.key, "success": sched.get("success", False),
            "scheduled": sched}


def main():
    parser = argparse.ArgumentParser(description="Multi-vertical LinkedIn driver")
    parser.add_argument("--vertical", help="Run a single vertical by key "
                        "(crosswalk|trainer|fitness|mind|health)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate + print, but don't schedule or learn")
    parser.add_argument("--learn-only", action="store_true",
                        help="Snapshot analytics + rebuild per-vertical patterns, no posting")
    args = parser.parse_args()

    ensure_directories()

    # Refresh the learning loop before writing (skipped on dry-run so a test
    # never touches the network or the pattern files).
    if not args.dry_run:
        from linkedin_agent.engine.analytics_engine import snapshot_all_platforms
        from linkedin_agent.engine.learning_engine import build_all_verticals
        print("\n📊 Snapshotting analytics (all platforms)...")
        snapshot_all_platforms()
        print("\n🧠 Rebuilding per-vertical winning patterns...")
        build_all_verticals()
        if args.learn_only:
            print("\n✓ Learn-only run complete.")
            sys.exit(0)

    if args.vertical:
        targets = [get_vertical(args.vertical)]
    else:
        targets = list(all_verticals())
        # Yield a slot per direct-API post publishing today, so a philosophy
        # post never collides with / bumps a vertical (cap stays at 5).
        n_yield = _direct_posts_due_today()
        if n_yield:
            skip, order = set(), [k for k in YIELD_ORDER]
            for key in order:
                if len(skip) >= n_yield:
                    break
                skip.add(key)
            targets = [v for v in targets if v.key not in skip]
            print(f"\n⚠ {n_yield} direct/philosophy post(s) publish to LinkedIn today "
                  f"— yielding slot(s) to stay at 5/day: {', '.join(sorted(skip))}")

    voice_profile = VoiceEngine().load_voice_profile()
    scheduler = Scheduler()
    infographic = InfographicEngine()
    notifier = Notifier()

    results = []
    for v in targets:
        try:
            results.append(run_vertical(v, voice_profile, scheduler, infographic,
                                        dry_run=args.dry_run))
        except Exception as e:
            print(f"\n✗ [{v.key}] errored: {e}")
            import traceback
            traceback.print_exc()
            results.append({"vertical": v.key, "success": False, "error": str(e)})

    ok = sum(1 for r in results if r.get("success"))
    print("\n" + "=" * 64)
    print(f"DONE — {ok}/{len(targets)} verticals "
          f"{'generated (dry run)' if args.dry_run else 'scheduled'}")
    for r in results:
        flag = "✓" if r.get("success") else "✗"
        print(f"  {flag} {r['vertical']}")
    print("=" * 64)

    if not args.dry_run:
        notifier.notify({"success": ok > 0,
                         "summary": f"{ok}/{len(targets)} verticals scheduled"})

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
