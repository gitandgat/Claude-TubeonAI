"""
Replace all 30 April 2026 posts with video versions across 5 platforms:
LinkedIn, Instagram, Facebook, TikTok, YouTube Shorts

Workflow for each post:
1. Fetch existing post content from Zernio (preserves all copy + scheduled time)
2. Upload Remotion MP4 via presigned URL
3. Delete the existing post
4. Create new post with video + all 5 platforms
"""
import os
import requests
import json

BASE    = "https://zernio.com/api/v1"
API_KEY = "***REMOVED-ZERNIO-KEY***"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"
TIMEZONE     = "America/New_York"

VIDEOS_DIR = "/Users/toto/Claude TubeonAI/crosswalk-remotion/out/april"

# Current Zernio post IDs — one per April date
DATE_TO_POST = {
    "2026-04-01": "69c3387336de3c648b7958c4",
    "2026-04-02": "69c201292a25487fc64b4fbf",
    "2026-04-03": "69aa3b89f54fd854c9f716ca",
    "2026-04-04": "69c2012fec62440017e6d23e",
    "2026-04-05": "69c3387d36de3c648b795add",
    "2026-04-06": "69c3388736de3c648b795c59",
    "2026-04-07": "69c201362a25487fc64b507f",
    "2026-04-08": "69c338905462ca74d6aa4fe8",
    "2026-04-09": "69c2013c2a25487fc64b5122",
    "2026-04-10": "69c338ad92bc1aa5ab9f3337",
    "2026-04-11": "69c338b692bc1aa5ab9f3413",
    "2026-04-12": "69c338c092bc1aa5ab9f34b5",
    "2026-04-13": "69aa391240da3d8c7bf05bb5",
    "2026-04-14": "69c204b72d7aa26fe2ea7306",
    "2026-04-15": "69c338cb36de3c648b795d10",
    "2026-04-16": "69c204bb2d7aa26fe2ea7367",
    "2026-04-17": "69c338d536de3c648b795db7",
    "2026-04-18": "69c204bf2d7aa26fe2ea73bf",
    "2026-04-19": "69c338df92bc1aa5ab9f361c",
    "2026-04-20": "69c338e992bc1aa5ab9f3695",
    "2026-04-21": "69c204c38efed57897fc6b1b",
    "2026-04-22": "69c338f292bc1aa5ab9f3780",
    "2026-04-23": "69c204c78efed57897fc6b58",
    "2026-04-24": "69c338fd36de3c648b795fa1",
    "2026-04-25": "69c204cb2d7aa26fe2ea7506",
    "2026-04-26": "69c339075462ca74d6aa51dd",
    "2026-04-27": "69c339115462ca74d6aa52aa",
    "2026-04-28": "69c204cf2d7aa26fe2ea7577",
    "2026-04-29": "69c3391b36de3c648b796266",
    "2026-04-30": "69c204d32d7aa26fe2ea75f0",
}

# YouTube hooks per date — used as the video title (≤100 chars)
YOUTUBE_TITLES = {
    "2026-04-01": "I used to introduce myself as 'Doctor.' Then I left.",
    "2026-04-02": "You didn't fail nursing. Nursing failed you.",
    "2026-04-03": "Healthcare burnout comes down to 3 fears. Here they are.",
    "2026-04-04": "Every morning at the crosswalk, I watched people hesitate.",
    "2026-04-05": "Nobody warns you about the grief of leaving healthcare.",
    "2026-04-06": "I used AI to rewrite my professional story after leaving medicine.",
    "2026-04-07": "Fill in the blank: I became a healthcare worker because ___.",
    "2026-04-08": "'Who are you without the title?' That question haunted me.",
    "2026-04-09": "5 things I'd tell the version of me in the hospital parking lot.",
    "2026-04-10": "'But you worked so hard to get here.' That sentence traps people.",
    "2026-04-11": "START → STOP → ELDER → HUMAN: The Crosswalk Method explained.",
    "2026-04-12": "Things nobody tells you about leaving healthcare.",
    "2026-04-13": "'I have no skills outside nursing.' AI proves that wrong in 60s.",
    "2026-04-14": "The real reason financial fear keeps healthcare workers stuck.",
    "2026-04-15": "5 AI prompts for healthcare professionals in career transition.",
    "2026-04-16": "Leaving isn't quitting. It's choosing. Let's reclaim that word.",
    "2026-04-17": "Parking lot criers: before-shift, after-shift, or both?",
    "2026-04-18": "Viktor Frankl was a physician first. What he'd say about burnout.",
    "2026-04-19": "Hot take: the wellness industry is gaslighting healthcare workers.",
    "2026-04-20": "6 signs you're not just burned out — you're at a crosswalk.",
    "2026-04-21": "Where are you in the crossing? A, B, C, or D?",
    "2026-04-22": "The hardest part of leaving medicine wasn't the leaving.",
    "2026-04-23": "How I'd use AI to plan a career transition if starting from scratch.",
    "2026-04-24": "Dear Nurse: I don't know your name. But I know your story.",
    "2026-04-25": "The 3 fears of burnout aren't separate — they feed each other.",
    "2026-04-26": "Hold your healthcare career gently. Like something that still matters.",
    "2026-04-27": "I used to journal alone. Now I journal with AI. Here's why it works.",
    "2026-04-28": "If you've made it this far in April — you are closer than you think.",
    "2026-04-29": "We're almost at the end of April. I want to mark this with you.",
    "2026-04-30": "This is how I end April. Not with a pitch. With a truth.",
}


def upload_video(filepath):
    """Presign → PUT → return publicUrl."""
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


def first_line(text, max_chars=100):
    """First non-empty line of text, truncated."""
    for line in text.split("\n"):
        line = line.strip()
        if line:
            return line[:max_chars - 3] + "..." if len(line) > max_chars else line
    return "Crosswalk Wisdom"


def create_post(date, scheduled_for, video_url, content_map, yt_title):
    li  = content_map.get("linkedin", content_map.get("facebook", ""))
    ig  = content_map.get("instagram", content_map.get("facebook", li))
    fb  = content_map.get("facebook", li)
    tt  = ig  # TikTok uses the Instagram copy
    yt_desc = li + "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition"

    media_item = {"url": video_url, "type": "video"}

    platforms = [
        {
            "platform": "linkedin",
            "accountId": LINKEDIN_ID,
            "customContent": li,
            "scheduledFor": scheduled_for,
        },
        {
            "platform": "instagram",
            "accountId": INSTAGRAM_ID,
            "customContent": ig,
            "scheduledFor": scheduled_for,
        },
        {
            "platform": "facebook",
            "accountId": FACEBOOK_ID,
            "customContent": fb,
            "scheduledFor": scheduled_for,
        },
        {
            "platform": "tiktok",
            "accountId": TIKTOK_ID,
            "customContent": tt,
            "scheduledFor": scheduled_for,
        },
        {
            "platform": "youtube",
            "accountId": YOUTUBE_ID,
            "customContent": yt_desc,
            "title": yt_title,
            "scheduledFor": scheduled_for,
        },
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
        slug    = f"apr-{date[8:10]}"
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

        # Build content map from per-platform customContent; fall back to top-level content
        fallback  = existing.get("content", "")
        content_map = {fallback: fallback}  # bootstrap
        content_map = {}
        scheduled_for = f"{date}T13:00:00.000Z"  # default 9am ET

        for pl in existing.get("platforms", []):
            platform = pl.get("platform", "")
            cc = pl.get("customContent") or fallback
            if platform:
                content_map[platform] = cc
            # Use the first platform's scheduledFor as the canonical time
            sf = pl.get("scheduledFor")
            if sf and scheduled_for == f"{date}T13:00:00.000Z":
                scheduled_for = sf

        if not content_map:
            print(f"    [WARN] No content — skipping\n")
            continue

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
