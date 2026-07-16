"""
Schedule March 26–31 + May 1 posts with video across all 5 platforms.
Workflow: fetch existing post → upload video → delete old post → create new 5-platform post.
"""
import os
import requests

BASE    = "https://zernio.com/api/v1"
from zernio_key import ZERNIO_API_KEY as API_KEY
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"
TIMEZONE     = "America/New_York"

VIDEOS_DIR = "/Users/toto/Claude TubeonAI/crosswalk-remotion/out/march"

# Existing post IDs to replace + their scheduled times
DATE_TO_POST = {
    "2026-03-26": "69c20115ec62440017e6d18c",
    "2026-03-27": "69aa36c2ce1b4e2fa008a7b3",
    "2026-03-28": "69c2011b2a25487fc64b4f52",
    "2026-03-30": "69aa33378321dcdb862283a6",
    "2026-03-31": "69c20122ec62440017e6d1ec",
    "2026-05-01": "69c204d72d7aa26fe2ea7652",  # currently on LI+FB only, scheduled 2026-05-02
}

VIDEO_SLUGS = {
    "2026-03-26": "mar-26",
    "2026-03-27": "mar-27",
    "2026-03-28": "mar-28",
    "2026-03-30": "mar-30",
    "2026-03-31": "mar-31",
    "2026-05-01": "may-01",
}

YOUTUBE_TITLES = {
    "2026-03-26": "When I told my mother I was leaving medicine, she cried.",
    "2026-03-27": "The metabolic cost of staying stuck is real.",
    "2026-03-28": "Quitting is not the opposite of success.",
    "2026-03-30": "Nobody told me that leaving medicine would feel like a death.",
    "2026-03-31": "Most people don't leave bad careers because of logistics.",
    "2026-05-01": "I wrote everything I wish someone had told me about the gap.",
}


def upload_video(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "video/mp4", "fileSize": filesize},
    )
    r.raise_for_status()
    data = r.json()
    upload_url = data["uploadUrl"]
    public_url = data["publicUrl"]
    with open(filepath, "rb") as f:
        put_r = requests.put(upload_url, data=f, headers={"Content-Type": "video/mp4"})
        put_r.raise_for_status()
    return public_url


def delete_post(post_id):
    r = requests.delete(f"{BASE}/posts/{post_id}", headers=HEADERS)
    if r.status_code not in (200, 204, 404):
        print(f"    [WARN DELETE {r.status_code}]")


def fetch_post(post_id):
    r = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS)
    if r.status_code == 200:
        d = r.json()
        return d.get("post", d)
    return None


def create_post(date, scheduled_for, video_url, content_map, yt_title):
    li  = content_map.get("linkedin") or content_map.get("facebook", "")
    ig  = content_map.get("instagram") or content_map.get("facebook") or li
    fb  = content_map.get("facebook") or li
    tt  = content_map.get("tiktok") or ig
    yt_desc = li + "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition"

    media_item = {"url": video_url, "type": "video"}

    platforms = [
        {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": li,      "scheduledFor": scheduled_for},
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": ig,      "scheduledFor": scheduled_for},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": fb,      "scheduledFor": scheduled_for},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": tt,      "scheduledFor": scheduled_for},
        {"platform": "youtube",   "accountId": YOUTUBE_ID,   "customContent": yt_desc, "title": yt_title, "scheduledFor": scheduled_for},
    ]

    body = {
        "content": li,
        "mediaItems": [media_item],
        "platforms": platforms,
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
    }

    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    return r.status_code, r.text[:300]


def main():
    dates = sorted(DATE_TO_POST.keys())
    print(f"Scheduling {len(dates)} posts across LinkedIn / Instagram / Facebook / TikTok / YouTube...\n")

    success = 0
    for date in dates:
        post_id = DATE_TO_POST[date]
        slug    = VIDEO_SLUGS[date]
        video_path = os.path.join(VIDEOS_DIR, f"{slug}.mp4")
        yt_title   = YOUTUBE_TITLES.get(date, "Crosswalk Wisdom")

        print(f"  [{date}]")

        if not os.path.exists(video_path):
            print(f"    [SKIP] {video_path} not found\n")
            continue

        # 1. Fetch existing post content
        existing = fetch_post(post_id)
        if not existing:
            print(f"    [WARN] Could not fetch post {post_id} — skipping\n")
            continue

        fallback = existing.get("content", "")
        content_map = {}
        scheduled_for = f"{date}T13:00:00.000Z"

        for pl in existing.get("platforms", []):
            platform = pl.get("platform", "")
            cc = pl.get("customContent") or fallback
            if platform:
                content_map[platform] = cc
            sf = pl.get("scheduledFor")
            if sf and scheduled_for == f"{date}T13:00:00.000Z":
                scheduled_for = sf

        if not content_map:
            content_map = {"linkedin": fallback, "facebook": fallback}

        # 2. Upload video
        try:
            video_url = upload_video(video_path)
            print(f"    [UPLOAD OK]")
        except Exception as e:
            print(f"    [UPLOAD FAIL] {e}\n")
            continue

        # 3. Delete old post
        delete_post(post_id)
        print(f"    [DELETE OK]")

        # 4. Create new post on all 5 platforms
        status, body = create_post(date, scheduled_for, video_url, content_map, yt_title)
        if status in (200, 201):
            print(f"    [POST OK {status}] LinkedIn + Instagram + Facebook + TikTok + YouTube\n")
            success += 1
        else:
            print(f"    [POST FAIL {status}] {body}\n")

    print(f"Done. {success}/{len(dates)} posts scheduled across all 5 platforms.")


if __name__ == "__main__":
    main()
