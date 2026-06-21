#!/usr/bin/env python3
"""
Pivot Map TikTok / YouTube Shorts video — the video cut of the IMG lead-magnet promo.

The image promo already covered LinkedIn + Instagram + Facebook (Jun 20). This
unlocks the two highest-reach channels the image post was dark on: TikTok and
YouTube Shorts. Reuses the proven TikTokReel-Dynamic Remotion composition
(kinetic captions, $0 render) + the Zernio presign→PUT→create video path.

  python3 pivot_map_video.py --render-only     # render the MP4, schedule nothing
  python3 pivot_map_video.py --dry-run         # render + show the schedule payload
  python3 pivot_map_video.py                    # render + LIVE schedule TikTok + YouTube
  python3 pivot_map_video.py --schedule-only    # skip render (MP4 already exists), schedule

Link path: TikTok = link in bio (linke.ro/crosswalkwisdom); YouTube = link in the
description. Landing page: https://www.crosswalkwisdom.com/pivot-map
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
load_dotenv(REPO / ".env")

# ── Zernio ───────────────────────────────────────────────────────────────────
sys.path.insert(0, str(REPO))
from zernio_key import ZERNIO_API_KEY  # centralized key (never hardcode)

BASE = "https://zernio.com/api/v1"
HDR = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}
TIMEZONE = "America/New_York"

TIKTOK_ID = "690941425f6fbb9ef8323078"
YOUTUBE_ID = "690940d35f6fbb9ef8323077"

# ── Render ───────────────────────────────────────────────────────────────────
REMOTION_DIR = REPO / "crosswalk-remotion"
COMPOSITION = "TikTokReel-Dynamic"
OUT_MP4 = REMOTION_DIR / "out" / "pivot-map.mp4"
PROPS_FILE = REMOTION_DIR / "out" / "pivot-map.props.json"
# Doctor-on-the-crossing background — already shipped with the project.
BACKGROUND = "assets/bg-tiktok-pov-doctor-crossing-guard.jpg"

LANDING = "https://www.crosswalkwisdom.com/pivot-map"
LINKERO = "linke.ro/crosswalkwisdom"

# ── Script (kinetic captions @ 30fps) ────────────────────────────────────────
# Adapted from the Pivot Map LinkedIn promo. First-person, concrete, anti-slop.
SEGMENTS = [
    {"text": "She applied to CaRMS four times.", "type": "hook", "durationFrames": 45},
    {"text": "Four.", "type": "hook", "durationFrames": 35},
    {"text": "", "type": "pause", "durationFrames": 12},
    {"text": "I asked what she'd do if she stopped.", "type": "body", "durationFrames": 50},
    {"text": "She went quiet.", "type": "body", "durationFrames": 40},
    {"text": "She had never let herself imagine it.", "type": "body", "durationFrames": 52},
    {"text": "", "type": "pause", "durationFrames": 15},
    {"text": "Nobody warns unmatched IMGs about this part.", "type": "body", "durationFrames": 55},
    {"text": "The trap isn't the match rate.", "type": "body", "durationFrames": 48},
    {"text": "It's the question you keep asking.", "type": "body", "durationFrames": 48},
    {"text": "", "type": "pause", "durationFrames": 12},
    {"text": "\"How do I finally match?\"", "type": "body", "durationFrames": 50},
    {"text": "That hands your future to a lottery.", "type": "body", "durationFrames": 50},
    {"text": "", "type": "pause", "durationFrames": 12},
    {"text": "There is a better question.", "type": "body", "durationFrames": 45},
    {"text": "What is my training worth right now,", "type": "body", "durationFrames": 50},
    {"text": "outside the match?", "type": "body", "durationFrames": 45},
    {"text": "", "type": "pause", "durationFrames": 15},
    {"text": "Clinical judgment under pressure.", "type": "body", "durationFrames": 48},
    {"text": "Turning medicine into plain words.", "type": "body", "durationFrames": 52},
    {"text": "Trust your patients handed you.", "type": "body", "durationFrames": 48},
    {"text": "", "type": "pause", "durationFrames": 12},
    {"text": "None of it expires because an algorithm didn't place you.", "type": "body", "durationFrames": 62},
    {"text": "", "type": "pause", "durationFrames": 18},
    {"text": "The Unmatched Doctor's Pivot Map. Free. Link in bio.", "type": "cta", "durationFrames": 78},
]

# ── Captions / descriptions (anti-slop, no URL in TikTok caption) ────────────
TIKTOK_CAPTION = (
    "You didn't waste those years in medicine. You just haven't been shown what "
    "they're worth.\n\n"
    "If you're an unmatched IMG, the trap isn't the match rate. It's the question "
    "you keep asking. The better one: what is your training worth right now, "
    "outside the match?\n\n"
    "Free guide in bio: 5 paths that use your medical degree without a residency "
    "seat, plus a 90-day plan.\n\n"
    "#IMG #InternationalMedicalGraduate #CaRMS #MedicalCareers #CareerChange"
)

YOUTUBE_TITLE = "Unmatched IMG? You're asking the wrong question."

YOUTUBE_DESC = (
    "A doctor I spoke with applied to CaRMS four times. When I asked what she'd do "
    "if she stopped, she went quiet. She had never let herself imagine it.\n\n"
    "The trap for unmatched international medical graduates isn't the match rate. "
    "It's the question you keep asking: \"How do I finally match?\" The better "
    "question is what your training is worth right now, outside the match. Clinical "
    "judgment. Fluency in medicine. Earned trust. None of it expires because an "
    "algorithm didn't place you.\n\n"
    f"Free guide, The Unmatched Doctor's Pivot Map: 5 paths that use your medical "
    f"degree without a residency seat, plus a 90-day plan to start tonight.\n"
    f"{LANDING}\n\n"
    "#Shorts #IMG #CaRMS #MedicalCareers #CareerChange #InternationalMedicalGraduate"
)

FIRST_COMMENT = (
    "The whole guide is free, The Unmatched Doctor's Pivot Map: 5 paths that use "
    f"your medical degree without a residency seat, plus a 90-day plan. {LANDING}"
)


def total_frames() -> int:
    return sum(s["durationFrames"] for s in SEGMENTS)


def render() -> None:
    OUT_MP4.parent.mkdir(parents=True, exist_ok=True)
    props = {"segments": SEGMENTS, "background": BACKGROUND, "handle": "@crosswalkwisdom"}
    PROPS_FILE.write_text(json.dumps(props))
    secs = total_frames() / 30
    print(f"Rendering {COMPOSITION} → {OUT_MP4.name}  ({total_frames()} frames, {secs:.1f}s)")
    cmd = [
        "npx", "remotion", "render", "src/index.tsx", COMPOSITION,
        str(OUT_MP4), f"--props={PROPS_FILE}",
    ]
    subprocess.run(cmd, cwd=str(REMOTION_DIR), check=True)
    print(f"  -> {OUT_MP4}  ({OUT_MP4.stat().st_size // 1024} KB)")


def upload_video(path: Path) -> str:
    r = requests.post(f"{BASE}/media/presign", headers=HDR,
                      json={"filename": path.name, "contentType": "video/mp4",
                            "fileSize": path.stat().st_size}, timeout=30)
    r.raise_for_status()
    d = r.json()
    with open(path, "rb") as f:
        requests.put(d["uploadUrl"], data=f,
                     headers={"Content-Type": "video/mp4"}, timeout=300).raise_for_status()
    return d["publicUrl"]


def build_body(video_url: str, scheduled_for: str) -> dict:
    media = [{"url": video_url, "type": "video"}]
    return {
        "content": TIKTOK_CAPTION,
        "mediaItems": media,
        "isDraft": False,
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
        "platforms": [
            {"platform": "tiktok", "accountId": TIKTOK_ID, "customContent": TIKTOK_CAPTION,
             "scheduledFor": scheduled_for},
            # YouTube title MUST live in platformSpecificData.title — a top-level
            # "title" is silently dropped by Zernio on create (verified Jun 21).
            {"platform": "youtube", "accountId": YOUTUBE_ID, "customContent": YOUTUBE_DESC,
             "scheduledFor": scheduled_for,
             "platformSpecificData": {"title": YOUTUBE_TITLE, "firstComment": FIRST_COMMENT}},
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render-only", action="store_true", help="render the MP4, schedule nothing")
    ap.add_argument("--schedule-only", action="store_true", help="skip render, schedule existing MP4")
    ap.add_argument("--dry-run", action="store_true", help="render + show payload, post nothing")
    ap.add_argument("--when", default="2026-06-23T16:00:00",
                    help="scheduledFor (ET). Default Jun 23 4pm ET (TikTok prime).")
    args = ap.parse_args()

    if not args.schedule_only:
        render()
    if args.render_only:
        print("\nRender complete. Preview the MP4, then run --dry-run to check the schedule.")
        return

    if not OUT_MP4.exists():
        sys.exit(f"MP4 missing: {OUT_MP4} (run without --schedule-only first)")

    if args.dry_run:
        print(f"\nDRY RUN — would schedule TikTok + YouTube for {args.when} {TIMEZONE}")
        print(f"  video: {OUT_MP4.name} ({OUT_MP4.stat().st_size // 1024} KB)")
        print(f"  YouTube title: {YOUTUBE_TITLE}")
        print(f"  YouTube first comment: {FIRST_COMMENT}")
        print(f"  TikTok link path: bio ({LINKERO})")
        return

    print("\nUploading video to Zernio...")
    video_url = upload_video(OUT_MP4)
    print(f"  -> {video_url}")

    print("Creating scheduled cross-post (TikTok + YouTube)...")
    r = requests.post(f"{BASE}/posts", headers=HDR, json=build_body(video_url, args.when), timeout=60)
    print("HTTP", r.status_code)
    try:
        data = r.json()
    except Exception:
        print(r.text[:400]); sys.exit(1)
    post = data.get("post", data)
    pid = post.get("_id", "?")
    print(f"  post _id: {pid}")
    print(f"  scheduledFor: {post.get('scheduledFor')}  status: {post.get('status')}")
    print(f"  platforms: {[p.get('platform') for p in post.get('platforms', [])]}")
    print(f"\nVerify in Zernio that status=scheduled. TikTok link is in bio: {LINKERO}")
    print("Reminder: confirm the YouTube first-comment link posts after publish.")


if __name__ == "__main__":
    main()
