#!/usr/bin/env python3
"""
Schedule the Pivot Map promo as one cross-post (LinkedIn + Instagram + Facebook)
via Zernio, with the 1080x1080 card and the /pivot-map link in the first comment.

YouTube/TikTok are skipped (image posts need a video cut).

    python schedule_pivot_map.py --dry-run     # show the payload, post nothing
    python schedule_pivot_map.py               # live schedule
"""

import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv("/Users/toto/Claude TubeonAI/.env")

ZERNIO_KEY = os.getenv("ZERNIO_API_KEY")
if not ZERNIO_KEY:
    sys.exit("ZERNIO_API_KEY not set in .env")

BASE = "https://zernio.com/api/v1"
HDR = {"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"}
TIMEZONE = "America/New_York"

LINKEDIN_ID = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID = "6909409a5f6fbb9ef8323074"

HERE = Path(__file__).resolve().parent
CARD = HERE / "crosswalk-img-pivot-map-social.png"

SCHEDULED_FOR = "2026-06-20T08:00:00"  # tomorrow 08:00 ET (safely in the future)
LINK = "https://www.crosswalkwisdom.com/pivot-map"

LINKEDIN_COPY = """A doctor told me last week she's applied to CaRMS four times.

Four.

When I asked what she'd do if she stopped, she went quiet. She'd never let herself imagine it.

Nobody warns unmatched international medical graduates about that part. The trap isn't the match rate. It's the question you keep asking: "How do I finally match?"

It feels responsible. It feels like grit. But it hands your whole future to a lottery you don't control, and it assumes a residency seat is the only proof your training was worth anything.

There's a better question: "What is my medical training worth right now, outside the match?"

Ask that one and the math changes. The training you think is trapped is worth more than you've been told:

- Clinical judgment. You make decisions with incomplete information while someone's health is on the line. That's rare in health tech, in research, in any company that sells to clinicians and keeps guessing what they need.
- Fluency in medicine. You translate a guideline for a patient and a study for a sales team. The business world pays for that, because almost no one can do it.
- Earned trust. Patients handed you their bodies. That credibility carries into medical education, advocacy, and consulting.

None of it expires because an algorithm didn't place you.

I'm not telling you to quit medicine. I'm telling you that "match or nothing" is a story, not a law. And believing it costs good doctors their best years.

If you're an unmatched IMG, ask the better question this week. You're holding more than you've been allowed to see.

What's one skill from your training you've been told doesn't count outside the hospital?"""

SHORT_COPY = """You didn't waste those years in medicine. You just haven't been shown what they're worth.

If you're an unmatched IMG, the trap isn't the match rate. It's the question you keep asking. "How do I finally match?" hands your future to a lottery. The better question: what is your training worth right now, outside the match?

Clinical judgment. Fluency in medicine. Earned trust. None of it expires because an algorithm didn't place you.

Free guide: 5 paths that use your medical degree without a residency seat, plus a 90-day plan. Link in bio."""

FIRST_COMMENT = (
    "I put the whole thing in a free guide, The Unmatched Doctor's Pivot Map: "
    "5 paths that use your medical degree without a residency seat, plus a 90-day "
    f"plan to start tonight. Grab it here: {LINK}"
)


def upload_image(path: Path) -> str:
    r = requests.post(f"{BASE}/media/presign", headers=HDR,
                      json={"filename": path.name, "contentType": "image/png",
                            "fileSize": path.stat().st_size}, timeout=30)
    r.raise_for_status()
    d = r.json()
    with open(path, "rb") as f:
        requests.put(d["uploadUrl"], data=f, headers={"Content-Type": "image/png"}, timeout=60).raise_for_status()
    return d["publicUrl"]


def build_body(image_url: str) -> dict:
    return {
        "content": LINKEDIN_COPY,
        "mediaItems": [{"url": image_url, "type": "image"}],
        "isDraft": False,
        "scheduledFor": SCHEDULED_FOR,
        "timezone": TIMEZONE,
        "platforms": [
            {"platform": "linkedin", "accountId": LINKEDIN_ID, "customContent": LINKEDIN_COPY,
             "scheduledFor": SCHEDULED_FOR, "platformSpecificData": {"firstComment": FIRST_COMMENT}},
            {"platform": "facebook", "accountId": FACEBOOK_ID, "customContent": LINKEDIN_COPY,
             "scheduledFor": SCHEDULED_FOR, "platformSpecificData": {"firstComment": FIRST_COMMENT}},
            {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": SHORT_COPY,
             "scheduledFor": SCHEDULED_FOR},
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not CARD.exists():
        sys.exit(f"Card image missing: {CARD}")

    if args.dry_run:
        print(f"DRY RUN — would schedule LinkedIn + Facebook + Instagram for {SCHEDULED_FOR} {TIMEZONE}")
        print(f"  card: {CARD.name}")
        print(f"  first comment: {FIRST_COMMENT}")
        return

    print("Uploading card image...")
    image_url = upload_image(CARD)
    print(f"  -> {image_url}")

    print("Creating scheduled cross-post...")
    r = requests.post(f"{BASE}/posts", headers=HDR, json=build_body(image_url), timeout=60)
    print("HTTP", r.status_code)
    try:
        data = r.json()
    except Exception:
        print(r.text[:400]); sys.exit(1)
    post = data.get("post", data)
    pid = post.get("_id", "?")
    print(f"  post _id: {pid}")
    print(f"  isDraft: {post.get('isDraft')}  scheduledFor: {post.get('scheduledFor')}")
    print(f"  platforms: {[p.get('platform') for p in post.get('platforms', [])]}")
    print(f"\nVerify in Zernio. Link goes out in the first comment: {LINK}")


if __name__ == "__main__":
    main()
