#!/usr/bin/env python3
"""
LinkedIn Post Scheduler
Runs daily (via cron). Publishes any queued post whose date is due.

Queue file: linkedin_post_queue.json
  [
    {
      "id": "post_2",
      "date": "2026-06-13",
      "text": "full post text...",
      "image": "/path/to/image.png",
      "status": "pending"        # pending | published | failed
    },
    ...
  ]

Usage:
  python linkedin_scheduler.py            # publish everything due today or earlier
  python linkedin_scheduler.py --dry-run  # show what would be published
"""

import os
import sys
import json
from datetime import date, datetime
from pathlib import Path
from dotenv import load_dotenv

# Always run relative to this script's directory (cron-safe)
SCRIPT_DIR = Path(__file__).parent
os.chdir(SCRIPT_DIR)

load_dotenv(SCRIPT_DIR / ".env")

from linkedin_full_automation import LinkedInFullAutomation

QUEUE_FILE = SCRIPT_DIR / "linkedin_post_queue.json"
LOG_FILE = SCRIPT_DIR / "logs" / "linkedin_scheduler.log"


def log(message: str):
    """Print and append to log file (cron output is easy to lose)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_queue() -> list:
    if not QUEUE_FILE.exists():
        log(f"No queue file at {QUEUE_FILE} — nothing to do")
        return []
    with open(QUEUE_FILE) as f:
        return json.load(f)


def save_queue(queue: list):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)


def main():
    dry_run = "--dry-run" in sys.argv
    today = date.today()

    queue = load_queue()
    if not queue:
        return True

    due = [
        p for p in queue
        if p.get("status") == "pending"
        and date.fromisoformat(p["date"]) <= today
    ]

    if not due:
        log(f"Checked queue: nothing due today ({today}). "
            f"{sum(1 for p in queue if p.get('status') == 'pending')} pending.")
        return True

    log(f"{len(due)} post(s) due: {[p['id'] for p in due]}")

    if dry_run:
        for p in due:
            log(f"DRY RUN — would publish {p['id']} ({p['date']}): "
                f"{p['text'][:60]}... [image: {p['image']}]")
        return True

    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    if not access_token:
        log("ERROR: no LINKEDIN_ACCESS_TOKEN in .env")
        return False

    automation = LinkedInFullAutomation(access_token)
    if not automation.author_urn:
        log("ERROR: could not get author URN — token may have expired. "
            "Re-run: python linkedin_oauth.py")
        return False

    all_ok = True
    for post in due:
        image_path = Path(post["image"])
        if not image_path.exists():
            log(f"ERROR: {post['id']} image missing: {image_path}")
            post["status"] = "failed"
            post["error"] = "image not found"
            all_ok = False
            continue

        asset_urn = automation.upload_image(image_path)
        if not asset_urn:
            log(f"ERROR: {post['id']} image upload failed")
            post["status"] = "failed"
            post["error"] = "image upload failed"
            all_ok = False
            continue

        if automation.create_post_with_image(post["text"], asset_urn):
            post["status"] = "published"
            post["published_at"] = datetime.now().isoformat()
            log(f"PUBLISHED: {post['id']}")
        else:
            post["status"] = "failed"
            post["error"] = "post creation failed"
            log(f"ERROR: {post['id']} post creation failed")
            all_ok = False

        save_queue(queue)  # save after each post so progress isn't lost

    save_queue(queue)
    log(f"Done. {sum(1 for p in due if p['status'] == 'published')}/{len(due)} published.")
    return all_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
