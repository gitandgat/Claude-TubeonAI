#!/usr/bin/env python3
"""
LinkedIn AI Agent CLI

Usage:
  python run_agent.py                    # Full daily pipeline
  python run_agent.py --voice-only       # Rebuild voice profile only
  python run_agent.py --research-only    # Run research scan only
  python run_agent.py --dry-run          # Full pipeline without scheduling
"""

import sys
import argparse
import os

# cron runs with a minimal PATH that omits the Python framework bin, so console
# scripts the pipeline shells out to (shot-scraper) aren't found. Put the dir of
# the running interpreter on PATH — version-independent, fixes it everywhere.
_py_bin = os.path.dirname(os.path.abspath(sys.executable))
if _py_bin not in os.environ.get("PATH", "").split(os.pathsep):
    os.environ["PATH"] = _py_bin + os.pathsep + os.environ.get("PATH", "")

# Load .env from the repo root regardless of working directory
# (cron runs with a minimal environment)
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# Add linkedin_agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "linkedin_agent"))

from agent import LinkedInAgent
from config import ensure_directories

def main():
    parser = argparse.ArgumentParser(
        description="Crosswalk Wisdom LinkedIn AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_agent.py              # Run full daily pipeline
  python run_agent.py --voice-only # Rebuild voice profile
  python run_agent.py --dry-run    # Test without scheduling
"""
    )

    parser.add_argument(
        "--voice-only",
        action="store_true",
        help="Rebuild voice profile from past posts only"
    )
    parser.add_argument(
        "--research-only",
        action="store_true",
        help="Run research scan only (don't write post)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run full pipeline but don't schedule to Zernio"
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Snapshot LinkedIn analytics into the learning time series"
    )
    parser.add_argument(
        "--learn",
        action="store_true",
        help="Rebuild winning_patterns.json from analytics history"
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=0,
        metavar="N",
        help="LinkedIn: snapshot+learn, then generate N posts SPREAD across the "
             "day (laptop-safe single run; replaces 5 separate cron runs)"
    )
    parser.add_argument(
        "--video",
        action="store_true",
        help="Generate + render + cross-post one video to TikTok/IG/FB/YouTube"
    )
    parser.add_argument(
        "--video-batch",
        type=int,
        default=0,
        metavar="N",
        help="Render N videos in one run, scheduled SPREAD across the day "
             "(laptop-safe: Mac only needs to be awake once)"
    )

    args = parser.parse_args()

    # Ensure directories exist
    ensure_directories()

    # LinkedIn daily batch: one run, sleep-safe. Refresh learning, then generate
    # N posts spread across the day-part slots (each a distinct theme + arm).
    if args.batch:
        from linkedin_agent.engine.analytics_engine import snapshot_all_platforms
        from linkedin_agent.engine.learning_engine import LearningEngine
        from linkedin_agent.video_scheduler import next_n_slots
        from linkedin_agent.engine.research_engine import ResearchEngine
        from linkedin_agent.experiment import EXPERIMENTS, ACTIVE_EXPERIMENT

        print("\n📊 Refreshing analytics + learning before the day's batch...\n")
        snapshot_all_platforms()
        LearningEngine().build_patterns()

        pts = ResearchEngine().run_daily_research().get("synthesis", {}).get("top_pain_points", [])
        slots = next_n_slots(args.batch)
        arms = list(EXPERIMENTS[ACTIVE_EXPERIMENT]["arms"].keys())
        agent = LinkedInAgent()

        scheduled = 0
        for i in range(args.batch):
            theme = pts[i % len(pts)]["pain_point"] if pts else "IMG career transition"
            arm = arms[i % len(arms)]
            print(f"\n=== LinkedIn post {i + 1}/{args.batch} — {theme} | arm={arm} | slot={slots[i][11:16]} ===")
            res = agent.run_full_pipeline(pain_point=theme, scheduled_for=slots[i], arm=arm)
            agent.notifier.notify(res)
            if res.get("scheduled"):
                scheduled += 1
        print(f"\n✓ LinkedIn batch done: {scheduled}/{args.batch} scheduled across the day")
        sys.exit(0 if scheduled else 1)

    # Autonomous video run(s): generate → render → cross-post all four surfaces.
    # --video-batch N renders N videos at once and spreads their POST times
    # across the day, so a sleeping laptop only needs to wake once to produce
    # a full day of content (vs 5 separate cron times that mostly miss).
    if args.video or args.video_batch:
        from linkedin_agent.video_agent import make_video
        from linkedin_agent.video_scheduler import cross_post_video, next_n_slots
        from linkedin_agent.engine.research_engine import ResearchEngine

        count = args.video_batch if args.video_batch else 1
        research = ResearchEngine().run_daily_research()
        pts = research.get("synthesis", {}).get("top_pain_points", [])
        slots = next_n_slots(count)

        scheduled = 0
        for i in range(count):
            theme = (pts[i % len(pts)]["pain_point"] if pts else "IMG career transition")
            print(f"\n=== Video {i + 1}/{count} — {theme} ===")
            made = make_video(theme)
            if not made.get("success"):
                print(f"  ✗ skipped: {made.get('error')}")
                continue
            caption = (f"{made['segments'][0]['text']} … "
                       "What did your detour cost you?  #IMG #CaRMS #MedicalCareers")
            title = made["segments"][0]["text"][:90]
            res = cross_post_video(made["video_path"], caption, title,
                                   scheduled_for=slots[i])
            if res.get("success"):
                scheduled += 1
        print(f"\n✓ Video batch done: {scheduled}/{count} scheduled across the day")
        sys.exit(0 if scheduled else 1)

    # Learning-loop modes run standalone (no full agent needed)
    if args.snapshot or args.learn:
        from linkedin_agent.engine.analytics_engine import snapshot_all_platforms
        from linkedin_agent.engine.learning_engine import LearningEngine
        if args.snapshot:
            print("\n📊 Snapshotting analytics (all platforms)...\n")
            snapshot_all_platforms()
        if args.learn:
            print("\n🧠 Learning winning patterns...\n")
            LearningEngine().build_patterns()
        sys.exit(0)

    # Initialize agent
    agent = LinkedInAgent()

    # Execute based on arguments
    print("\n🤖 LinkedIn AI Agent Starting...\n")

    result = agent.execute(
        voice_only=args.voice_only,
        research_only=args.research_only,
        dry_run=args.dry_run
    )

    # Exit with status code
    sys.exit(0 if result.get("success") else 1)

if __name__ == "__main__":
    main()
