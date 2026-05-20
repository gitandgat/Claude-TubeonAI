"""
Replace Zernio posts for 14 April dates with newly rendered videos (with real images).
Fetches existing post content, deletes old post, creates new post with new video.
"""
import os
import requests

BASE    = "https://zernio.com/api/v1"
API_KEY = "sk_d1c977cc304ec9685c24f22c7e3b868abd5a10b9db8f7648b2b74384ab1ca399"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"
TIMEZONE     = "America/New_York"

VIDEOS_DIR = "/Users/toto/Claude TubeonAI/crosswalk-remotion/out/april"

# Existing Zernio post IDs for the 14 dates being replaced
DATE_TO_POST = {
    "2026-04-02": "69c201292a25487fc64b4fbf",
    "2026-04-03": "69aa3b89f54fd854c9f716ca",
    "2026-04-04": "69c2012fec62440017e6d23e",
    "2026-04-07": "69c201362a25487fc64b507f",
    "2026-04-09": "69c2013c2a25487fc64b5122",
    "2026-04-13": "69aa391240da3d8c7bf05bb5",
    "2026-04-14": "69c204b72d7aa26fe2ea7306",
    "2026-04-16": "69c204bb2d7aa26fe2ea7367",
    "2026-04-18": "69c204bf2d7aa26fe2ea73bf",
    "2026-04-21": "69c204c38efed57897fc6b1b",
    "2026-04-23": "69c204c78efed57897fc6b58",
    "2026-04-25": "69c204cb2d7aa26fe2ea7506",
    "2026-04-28": "69c204cf2d7aa26fe2ea7577",
    "2026-04-30": "69c204d32d7aa26fe2ea75f0",
}

YOUTUBE_TITLES = {
    "2026-04-02": "You didn't fail nursing. Nursing failed you.",
    "2026-04-03": "Healthcare burnout comes down to 3 fears. Here they are.",
    "2026-04-04": "Every morning at the crosswalk, I watched people hesitate.",
    "2026-04-07": "Fill in the blank: I became a healthcare worker because ___.",
    "2026-04-09": "5 things I'd tell the version of me in the hospital parking lot.",
    "2026-04-13": "'I have no skills outside nursing.' AI proves that wrong in 60s.",
    "2026-04-14": "The real reason financial fear keeps healthcare workers stuck.",
    "2026-04-16": "Leaving isn't quitting. It's choosing. Let's reclaim that word.",
    "2026-04-18": "Viktor Frankl was a physician first. What that means for burnout.",
    "2026-04-21": "Where are you right now? No wrong answers.",
    "2026-04-23": "How I'd use AI to plan a career transition from scratch.",
    "2026-04-25": "The 3 fears aren't separate. They feed each other.",
    "2026-04-28": "If you've made it this far — you are closer than you think.",
    "2026-04-30": "Not with a pitch. With a truth. How April ends.",
}

SLUG_MAP = {
    "2026-04-02": "apr-02",
    "2026-04-03": "apr-03",
    "2026-04-04": "apr-04",
    "2026-04-07": "apr-07",
    "2026-04-09": "apr-09",
    "2026-04-13": "apr-13",
    "2026-04-14": "apr-14",
    "2026-04-16": "apr-16",
    "2026-04-18": "apr-18",
    "2026-04-21": "apr-21",
    "2026-04-23": "apr-23",
    "2026-04-25": "apr-25",
    "2026-04-28": "apr-28",
    "2026-04-30": "apr-30",
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
    with open(filepath, "rb") as f:
        requests.put(data["uploadUrl"], data=f, headers={"Content-Type": "video/mp4"}).raise_for_status()
    return data["publicUrl"]


def fetch_post(post_id):
    r = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS)
    if r.status_code == 200:
        d = r.json()
        return d.get("post", d)
    return None


def delete_post(post_id):
    r = requests.delete(f"{BASE}/posts/{post_id}", headers=HEADERS)
    if r.status_code not in (200, 204, 404):
        print(f"    [WARN DELETE {r.status_code}]")


def create_post(scheduled_for, video_url, content_map, yt_title):
    li = content_map.get("linkedin", content_map.get("content", ""))
    ig = content_map.get("instagram", li)
    fb = content_map.get("facebook", li)
    yt_desc = li + "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition"

    platforms = [
        {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": li, "scheduledFor": scheduled_for},
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": ig, "scheduledFor": scheduled_for},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": fb, "scheduledFor": scheduled_for},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": ig, "scheduledFor": scheduled_for},
        {"platform": "youtube",   "accountId": YOUTUBE_ID,   "customContent": yt_desc, "title": yt_title, "scheduledFor": scheduled_for},
    ]

    body = {
        "content": li,
        "mediaItems": [{"url": video_url, "type": "video"}],
        "platforms": platforms,
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    return r.status_code


def main():
    dates = sorted(DATE_TO_POST.keys())
    print(f"Re-scheduling {len(dates)} posts with new images...\n")

    success = 0
    for date in dates:
        post_id = DATE_TO_POST[date]
        slug = SLUG_MAP[date]
        video_path = os.path.join(VIDEOS_DIR, f"{slug}.mp4")
        yt_title = YOUTUBE_TITLES[date]

        print(f"  {date} ({slug})")

        if not os.path.exists(video_path):
            print(f"    [SKIP] Video not found: {video_path}")
            continue

        # Fetch existing post for copy
        existing = fetch_post(post_id)
        if existing:
            content_map = {
                "content": existing.get("content", ""),
                "linkedin": next((p.get("customContent") for p in existing.get("platforms", []) if p.get("platform") == "linkedin"), existing.get("content", "")),
                "instagram": next((p.get("customContent") for p in existing.get("platforms", []) if p.get("platform") == "instagram"), existing.get("content", "")),
                "facebook": next((p.get("customContent") for p in existing.get("platforms", []) if p.get("platform") == "facebook"), existing.get("content", "")),
            }
            scheduled_for = existing.get("scheduledFor", f"{date}T09:00:00")[:19]
        else:
            content_map = {"content": ""}
            scheduled_for = f"{date}T09:00:00"

        # Upload new video
        video_url = upload_video(video_path)

        # Delete old post
        delete_post(post_id)

        # Create new post with video
        status = create_post(scheduled_for, video_url, content_map, yt_title)

        if status in (200, 201):
            print(f"    ✓ Rescheduled at {scheduled_for}")
            success += 1
        else:
            print(f"    ✗ Failed with status {status}")

    print(f"\nDone: {success}/{len(dates)} posts updated.")


if __name__ == "__main__":
    main()
