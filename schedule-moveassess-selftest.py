#!/usr/bin/env python3
"""Schedule the 8 MoveAssess "case of the day" self-test posts to Zernio.

One video post per day, Jul 5-12 2026 at 11:00 ET, across all 5 platforms
(LinkedIn / Instagram / Facebook / TikTok / YouTube). Each post carries its
rendered demo video, the stop-slop'd body, and the link in the FIRST COMMENT.

Safe to re-run: created post ids are logged to scheduled_log.json and skipped.
Run one first to verify, then the rest:

    python3 schedule-moveassess-selftest.py --only cod-01-hip-drop
    python3 schedule-moveassess-selftest.py                # all remaining
"""
import argparse
import json
import sys
from pathlib import Path

import requests

from zernio_key import ZERNIO_API_KEY
from zernio_client import ZernioClient

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}
TIMEZONE = "America/New_York"

ACCOUNTS = {
    "linkedin": "690940455f6fbb9ef8323070",
    "instagram": "690940655f6fbb9ef8323072",
    "facebook": "6909409a5f6fbb9ef8323074",
    "tiktok": "690941425f6fbb9ef8323078",
    "youtube": "690940d35f6fbb9ef8323077",
}

HERE = Path(__file__).resolve().parent
CONTENT = HERE / "moveassess-content"
VIDEOS = HERE / "crosswalk-remotion" / "out" / "moveassess"
LOG = CONTENT / "scheduled_log.json"
YT_TAGS = "#Shorts #MoveAssess #Mobility #Longevity #MovementScreen"

# Hardcoded schedule map: post id -> (date, video file, YouTube title).
# Body + first comment come from the batch JSON (source of truth).
PLAN = {
    "cod-01-hip-drop":       ("2026-07-05", "single-leg.mp4",  "Your knee pain isn't a knee problem (10-second test)"),
    "cod-02-knee-cave":      ("2026-07-06", "knee-cave.mp4",   "Why 'strengthen your knees' is bad advice"),
    "cod-03-forward-head":   ("2026-07-07", "forward-head.mp4","The wall test for tech neck"),
    "cod-04-chair-rise":     ("2026-07-08", "chair-rise.mp4",  "Can you stand up without your hands?"),
    "cod-05-tight-hamstrings":("2026-07-09","hamstrings.mp4",  "Your hamstrings aren't tight, they're stretched"),
    "cod-06-arch-collapse":  ("2026-07-10", "arch.mp4",        "Your knee pain might start at your feet"),
    "cod-07-wall-reach":     ("2026-07-11", "wall-reach.mp4",  "The shoulder test most people fail"),
    "cod-08-do-all-seven":   ("2026-07-12", "hub.mp4",         "The 60-second movement self-test"),
}
TIME_OF_DAY = "T11:00:00"


def load_posts() -> dict:
    posts = {}
    for f in ("case-of-day-batch1.json", "case-of-day-batch2.json"):
        data = json.loads((CONTENT / f).read_text())
        for p in data["posts"]:
            posts[p["id"]] = p
    return posts


def load_log() -> dict:
    if LOG.exists():
        return json.loads(LOG.read_text())
    return {}


def save_log(log: dict) -> None:
    LOG.write_text(json.dumps(log, indent=2))


def schedule_one(client: ZernioClient, post: dict, date: str, video: str, yt_title: str) -> str:
    body = post["body"]
    first_comment = post["first_comment"]
    when = f"{date}{TIME_OF_DAY}"

    video_path = VIDEOS / video
    if not video_path.exists():
        raise FileNotFoundError(video_path)
    print(f"    uploading {video} ...")
    video_url = client.upload_video(str(video_path))

    yt_desc = f"{body}\n\n{YT_TAGS}"

    def psd(extra: dict = None) -> dict:
        # firstComment + YT title live in per-platform platformSpecificData.
        # Top-level firstComment / per-platform title are silently ignored by Zernio.
        d = {"firstComment": first_comment}
        if extra:
            d.update(extra)
        return d

    platforms = [
        {"platform": "linkedin",  "accountId": ACCOUNTS["linkedin"],  "customContent": body,    "scheduledFor": when, "platformSpecificData": psd()},
        {"platform": "instagram", "accountId": ACCOUNTS["instagram"], "customContent": body,    "scheduledFor": when, "platformSpecificData": psd()},
        {"platform": "facebook",  "accountId": ACCOUNTS["facebook"],  "customContent": body,    "scheduledFor": when, "platformSpecificData": psd()},
        {"platform": "tiktok",    "accountId": ACCOUNTS["tiktok"],    "customContent": body,    "scheduledFor": when, "platformSpecificData": psd()},
        {"platform": "youtube",   "accountId": ACCOUNTS["youtube"],   "customContent": yt_desc, "scheduledFor": when, "platformSpecificData": psd({"title": yt_title})},
    ]
    payload = {
        "content": body,
        "mediaItems": [{"url": video_url, "type": "video"}],
        "platforms": platforms,
        "scheduledFor": when,
        "timezone": TIMEZONE,
        "isDraft": False,
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=payload, timeout=120)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"schedule failed {r.status_code}: {r.text[:300]}")
    new = r.json()
    pid = new.get("_id") or (new.get("data") or {}).get("_id") or new.get("id")
    return pid


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="schedule just this post id")
    args = ap.parse_args()

    posts = load_posts()
    log = load_log()
    client = ZernioClient(ZERNIO_API_KEY)

    ids = [args.only] if args.only else list(PLAN.keys())
    done = 0
    for pid in ids:
        if pid not in PLAN:
            print(f"  ! unknown id {pid}")
            continue
        if pid in log:
            print(f"  ✓ {pid} already scheduled ({log[pid]}) — skipping")
            continue
        date, video, yt_title = PLAN[pid]
        print(f"  {date}  {pid}")
        try:
            zid = schedule_one(client, posts[pid], date, video, yt_title)
        except Exception as e:  # noqa: BLE001
            print(f"    ✗ {e}")
            print("    stopping so nothing double-posts; fix and re-run.")
            return 1
        log[pid] = zid
        save_log(log)
        print(f"    ✓ scheduled {date} 11:00 ET · 5 platforms · video · first comment  [{zid}]")
        done += 1

    print(f"\nDone. {done} newly scheduled. Log: {LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
