#!/usr/bin/env python3
"""Ship the crosswalk avatar-intro test video to TikTok + Instagram + YouTube.

Experiment: same Pivot Map animation as the Jun 22 baseline, but with a 15s
talking-head opener (Sahawat's face). Measures whether the human-face hook lifts
retention vs the animation-only version already live on TikTok.

Video: avatar-engine/ship/crosswalk-avatar-final.mp4 (1080x1920, 48s)
"""
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
from zernio_key import ZERNIO_API_KEY

BASE = "https://zernio.com/api/v1"
HDR = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}
TIMEZONE = "America/New_York"

TIKTOK_ID = "690941425f6fbb9ef8323078"
YOUTUBE_ID = "690940d35f6fbb9ef8323077"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"

VIDEO = REPO / "avatar-engine" / "ship" / "crosswalk-avatar-final.mp4"
WHEN = "2026-06-26T16:00:00"   # Jun 26, 4pm ET (next 4pm slot; baseline posted at 4pm ET)

CAPTION = (
    "A doctor I know applied to the match four times.\n\n"
    "Nobody asked her the question that actually mattered: what is your training "
    "worth if you never match?\n\n"
    "If you're an unmatched IMG, you already hold more than the system measures. "
    "Clinical judgment under pressure. The ability to translate medicine for people "
    "who need it. Trust that patients handed you. None of it expires because an "
    "algorithm didn't place you.\n\n"
    "The Pivot Map shows you where it transfers. Free.\n\n"
    "#IMG #internationalmedicalgraduate #CaRMS #medicaleducation #careerpivot"
)
YT_TITLE = "What your medical training is worth if you never match"
YT_DESC = CAPTION + "\n\n#Shorts #CrosswalkWisdom"
FIRST_COMMENT = "The Pivot Map (free): www.crosswalkwisdom.com/pivot-map"


def upload_video(path: Path) -> str:
    r = requests.post(f"{BASE}/media/presign", headers=HDR,
                      json={"filename": path.name, "contentType": "video/mp4",
                            "fileSize": path.stat().st_size})
    r.raise_for_status()
    d = r.json()
    with open(path, "rb") as f:
        requests.put(d["uploadUrl"], data=f,
                     headers={"Content-Type": "video/mp4"}).raise_for_status()
    return d["publicUrl"]


def main() -> None:
    if not VIDEO.exists():
        raise SystemExit(f"video not found: {VIDEO}")
    print(f"Uploading {VIDEO.name} ({VIDEO.stat().st_size // 1024} KB)...")
    url = upload_video(VIDEO)
    print(f"  uploaded -> {url}")

    body = {
        "content": CAPTION,
        "mediaItems": [{"url": url, "type": "video"}],
        "isDraft": False,
        "scheduledFor": WHEN,
        "timezone": TIMEZONE,
        "platforms": [
            {"platform": "tiktok", "accountId": TIKTOK_ID,
             "customContent": CAPTION, "scheduledFor": WHEN,
             "platformSpecificData": {"firstComment": FIRST_COMMENT}},
            {"platform": "instagram", "accountId": INSTAGRAM_ID,
             "customContent": CAPTION, "scheduledFor": WHEN,
             "platformSpecificData": {"firstComment": FIRST_COMMENT}},
            {"platform": "youtube", "accountId": YOUTUBE_ID,
             "customContent": YT_DESC, "scheduledFor": WHEN,
             "platformSpecificData": {"title": YT_TITLE,
                                      "firstComment": FIRST_COMMENT}},
        ],
    }
    r = requests.post(f"{BASE}/posts", headers=HDR, json=body)
    print(f"\nPOST /posts -> {r.status_code}")
    if r.status_code not in (200, 201):
        raise SystemExit(f"create failed: {r.text[:400]}")
    post = r.json().get("post", r.json())
    pid = post.get("_id")
    print(f"  post _id: {pid}")
    print(f"  status:   {post.get('status')}")
    print(f"  when:     {post.get('scheduledFor')}")
    print(f"  platforms: {[p.get('platform') for p in post.get('platforms', [])]}")

    # verify
    g = requests.get(f"{BASE}/posts/{pid}", headers=HDR)
    if g.status_code == 200:
        gp = g.json().get("post", g.json())
        print("\nverify:")
        for p in gp.get("platforms", []):
            psd = p.get("platformSpecificData", {}) or {}
            print(f"  {p.get('platform'):10} status={p.get('status')} "
                  f"title={psd.get('title')!r} firstComment={'set' if psd.get('firstComment') else 'MISSING'}")


if __name__ == "__main__":
    main()
