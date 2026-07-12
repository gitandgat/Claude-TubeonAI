"""Cross-post one rendered video to TikTok + IG Reels + FB Reels + YouTube Shorts.

The whole point of the video strategy: generate ONE clean (watermark-free)
vertical video and put it on all four video surfaces. The learning loop then
measures which platform amplifies the same video best — a clean natural
experiment. IG/YouTube get the winning format (video) instead of the dead one
(carousels); FB tags along but is audience-starved.
"""

import os
import sys
from datetime import datetime, timedelta
from pytz import timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_agent.config import VIDEO_PLATFORM_ACCOUNTS, LINKEDIN_SCHEDULE_TZ
from zernio_client import ZernioClient


# Spread up to 5 videos/day across the day — TikTok/IG/YouTube reward spacing,
# not dumping. Each cron run lands on the soonest future slot.
VIDEO_POST_TIMES_ET = ["08:00", "11:00", "14:00", "17:00", "20:00"]


def next_n_slots(n: int, tz_name: str = LINKEDIN_SCHEDULE_TZ) -> list:
    """The next N day-part slots from now (today's remaining, then tomorrow…).

    Lets one batch run schedule N videos SPREAD across the day, so the Mac only
    needs to be awake once — not at 5 separate (often-asleep) times.
    """
    tz = timezone(tz_name)
    now = datetime.now(tz)
    slots, day = [], 0
    while len(slots) < n:
        for t in VIDEO_POST_TIMES_ET:
            hh, mm = (int(x) for x in t.split(":"))
            slot = (now + timedelta(days=day)).replace(
                hour=hh, minute=mm, second=0, microsecond=0)
            if slot > now and len(slots) < n:
                slots.append(slot.isoformat())
        day += 1
    return slots


def _next_slot(tz_name: str = LINKEDIN_SCHEDULE_TZ) -> str:
    """Soonest upcoming day-part slot (single-video convenience)."""
    return next_n_slots(1, tz_name)[0]


def cross_post_video(video_path: str, caption: str, title: str,
                     scheduled_for: str = None) -> dict:
    """Upload the mp4 once and schedule it to all four video platforms.

    scheduled_for: explicit ISO slot (for batch spreading); defaults to the
    soonest day-part slot.

    Returns {success, post_id, platforms_scheduled, error}.
    """
    zernio = ZernioClient()

    if not os.path.exists(video_path):
        return {"success": False, "error": f"video not found: {video_path}"}

    print("Uploading video to Zernio CDN...")
    video_url = zernio.upload_video(video_path)
    print(f"  ✓ {video_url}")

    scheduled_for = scheduled_for or _next_slot()
    platforms = []
    for name, account_id in VIDEO_PLATFORM_ACCOUNTS.items():
        entry = {
            "platform": name,
            "accountId": account_id,
            "customContent": caption,
            "scheduledFor": scheduled_for,
        }
        if name == "youtube":                     # YouTube requires a title
            entry["platformSpecificData"] = {"title": title}
        platforms.append(entry)

    media_items = [{"url": video_url, "type": "video"}]

    try:
        resp = zernio.schedule_post(
            content=caption,
            scheduled_for=scheduled_for,
            timezone=LINKEDIN_SCHEDULE_TZ,
            platforms=platforms,
            media_items=media_items,
            title=title,
        )
        post_id = resp.get("_id") or resp.get("id") or resp.get("post", {}).get("_id")
        if post_id:
            print(f"✓ Video scheduled to {', '.join(VIDEO_PLATFORM_ACCOUNTS)} for {scheduled_for}")
            return {"success": True, "post_id": post_id,
                    "platforms_scheduled": list(VIDEO_PLATFORM_ACCOUNTS.keys()),
                    "scheduled_for": scheduled_for, "video_url": video_url}
        return {"success": False, "error": "no post id returned"}
    except Exception as e:
        body = getattr(getattr(e, "response", None), "text", "") or ""
        if "daily limit" in body.lower():
            print("⏭ A video platform is at its daily limit — skipping")
            return {"success": False, "skipped": True, "error": "daily_limit_reached"}
        print(f"✗ Error scheduling video: {e}")
        return {"success": False, "error": str(e)}
