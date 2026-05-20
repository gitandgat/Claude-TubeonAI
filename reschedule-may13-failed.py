#!/usr/bin/env python3
"""Reschedule the 3 posts that failed on May 12 due to LinkedIn daily limit."""
import os, datetime, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import anthropic
from tubeonai_client import TubeonAIClient
from image_gen_client import generate_health_image
from daily_health_bot import write_post_from_summary, adapt_copy, upload_image, schedule_post, et_to_utc

ZERNIO_KEY = os.getenv("ZERNIO_API_KEY")
TUBEONAI_KEY = os.getenv("TUBEONAI_API_KEY")

# Videos that failed on May 12 — reuse existing TubeonAI summary IDs
FAILED_VIDEOS = [
    {
        "title": "6 Weeks To Fix Their Gut Health!",
        "url": "https://www.youtube.com/watch?v=tPp4FSd6PXc",
        "summary_id": "019e1b7c-32cd-733b-9e9f-5f8328aeb3c9",
        "slot": "11:00",
    },
    {
        "title": "How to Improve Your GUT HEALTH The Holistic Way!",
        "url": "https://www.youtube.com/watch?v=XD8jjQEeSc8",
        "summary_id": "019e1b7d-9c19-73d4-b4fa-91981093339d",
        "slot": "14:00",
    },
    {
        "title": "Will fermented foods improve my gut health? | Sandor Katz and Professor Tim Spector",
        "url": "https://www.youtube.com/watch?v=-rwOqJmMZH4",
        "summary_id": "019e1b7e-a581-722c-9291-ca4f51eebff7",
        "slot": "17:00",
    },
]

tomorrow = datetime.date(2026, 5, 13)
client = TubeonAIClient(TUBEONAI_KEY)

print(f"Rescheduling 3 failed posts for {tomorrow}")
print("=" * 60)

for v in FAILED_VIDEOS:
    print(f"\n[{v['slot']} ET]  {v['title'][:65]}")

    # Get existing summary
    print("  Fetching existing TubeonAI summary...")
    summary_resp = client.get_summary(v["summary_id"])
    summary_text = summary_resp["data"].get("summary", "")

    # Generate post copy
    print("  Writing post (Haiku)...")
    linkedin_copy = write_post_from_summary(summary_text)
    print(f"  Hook: {linkedin_copy.splitlines()[0][:80]}")

    # Generate image
    print("  Generating image (DALL-E 3)...")
    img_path = generate_health_image(v["title"])

    # Upload + schedule for tomorrow
    print(f"  Uploading & scheduling for {v['slot']} ET on {tomorrow}...")
    media_url = upload_image(img_path)
    scheduled_at = et_to_utc(v["slot"], tomorrow)
    ok = schedule_post(linkedin_copy, media_url, scheduled_at)
    os.remove(img_path)

    if ok:
        print(f"  ✓ Scheduled → {scheduled_at} UTC")
    else:
        print(f"  ✗ Failed to schedule")

print("\nDone.")
