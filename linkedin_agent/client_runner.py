"""Per-client live scheduler for the managed ghostwriting service.

Runs ONE post for a saved client tenant and schedules it to THAT client's
LinkedIn account via Zernio — never the in-house account. Generation reuses the
proven PostWriter; the client duck-types as a Vertical so its persona, voice,
first-comment CTA, and per-client learning log all flow through unchanged.

Cadence is owned by cron/launchd (e.g. fire Mon–Fri for 5 posts/week), not by
this script — each invocation produces one post for the chosen slot.

Usage:
  python -m linkedin_agent.client_runner --client jane-doe              # next 8am ET
  python -m linkedin_agent.client_runner --client jane-doe --at 2026-06-20T11:00:00
  python -m linkedin_agent.client_runner --client jane-doe --dry-run    # generate only
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_agent.client_manager import load_client, load_voice_profile
from linkedin_agent.engine.post_writer import PostWriter
from linkedin_agent.scheduler import Scheduler

FALLBACK_THEMES = (
    "a specific moment that changed how you see your work",
    "a mistake that taught you something you still use",
    "the day you decided to do things differently",
)


def pick_theme(client) -> str:
    """Deterministic daily theme rotation so repeated runs vary by date."""
    themes = client.themes or FALLBACK_THEMES
    return themes[date.today().toordinal() % len(themes)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Schedule one post for a client tenant")
    parser.add_argument("--client", required=True, help="Client slug (see data/clients/)")
    parser.add_argument("--at", default=None, help="ISO slot datetime (default: next 8am ET)")
    parser.add_argument("--dry-run", action="store_true", help="Generate + print only")
    args = parser.parse_args()

    try:
        client = load_client(args.client)
    except FileNotFoundError:
        print(f"✗ No client '{args.client}'. Onboard them first with onboard_client.")
        return 1

    voice = load_voice_profile(client)
    if not voice:
        print(f"✗ No voice profile for '{client.slug}'. Re-run onboarding.")
        return 1

    # SAFETY GATE: never post live without the client's OWN account id. Without
    # it the Scheduler falls back to the in-house account — i.e. the client's
    # post would publish on the wrong profile. Dry-run is always allowed.
    if not args.dry_run and not client.zernio_account_id:
        print(f"✗ '{client.slug}' has no zernio_account_id — refusing to post live.")
        print("  Connect their LinkedIn in Zernio, set the id on the client, then")
        print("  re-run. (Use --dry-run to preview content without an account.)")
        return 1

    theme = pick_theme(client)
    print(f"→ {client.name}: generating post on theme: {theme}")
    writer = PostWriter(voice_profile=voice, vertical=client)
    result = writer.write_with_3_qa_rounds(hook=theme, pain_point=theme)
    post = (result or {}).get("post", "").strip()
    if not post:
        print("✗ Generation failed.")
        return 1

    if args.dry_run:
        print("\n----- DRY RUN (not scheduled) -----\n" + post + "\n")
        return 0

    scheduler = Scheduler(linkedin_account_id=client.zernio_account_id)
    sched = scheduler.schedule_post(post, scheduled_for=args.at, vertical=client)
    if not sched.get("success"):
        print(f"✗ Scheduling failed: {sched.get('error')}")
        return 1

    scheduler.log_scheduled_post(
        sched, hook=theme, pain_point=theme, post_content=post, vertical=client
    )
    print(f"\n✓ Scheduled for {client.name} → "
          f"post {sched.get('post_id')} @ {sched.get('scheduled_for')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
