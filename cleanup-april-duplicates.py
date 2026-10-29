"""
For each of the 14 April dates:
1. Find the post with real content (customContent on LinkedIn platform)
2. Grab the newest apr-XX.mp4 video URL
3. Delete all duplicate posts for that date
4. Create one clean post: real content + new video
"""
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

APRIL_DATES = [
    "2026-04-02","2026-04-03","2026-04-04","2026-04-07","2026-04-09",
    "2026-04-13","2026-04-14","2026-04-16","2026-04-18","2026-04-21",
    "2026-04-23","2026-04-25","2026-04-28","2026-04-30",
]

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


def get_full_post(post_id):
    r = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS)
    if r.status_code == 200:
        return r.json().get("post", r.json())
    return None


def delete_post(post_id):
    r = requests.delete(f"{BASE}/posts/{post_id}", headers=HEADERS)
    if r.status_code not in (200, 204, 404):
        print(f"    [WARN DELETE {r.status_code}]")


def create_post(scheduled_for, video_url, content_map, yt_title):
    li = content_map.get("linkedin", "")
    ig = content_map.get("instagram", li)
    fb = content_map.get("facebook", li)
    yt = li + "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition"

    platforms = [
        {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": li, "scheduledFor": scheduled_for},
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": ig, "scheduledFor": scheduled_for},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": fb, "scheduledFor": scheduled_for},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": ig, "scheduledFor": scheduled_for},
        {"platform": "youtube",   "accountId": YOUTUBE_ID,   "customContent": yt, "title": yt_title, "scheduledFor": scheduled_for},
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
    # Fetch all posts once
    r = requests.get(f"{BASE}/posts?limit=100", headers=HEADERS)
    all_posts = r.json().get("posts", [])

    from collections import defaultdict
    by_date = defaultdict(list)
    for p in all_posts:
        sched = p.get("scheduledFor", "")[:10]
        if sched in APRIL_DATES:
            by_date[sched].append(p)

    print(f"Cleaning up duplicates for {len(by_date)} dates...\n")

    for date in sorted(by_date.keys()):
        posts = by_date[date]
        yt_title = YOUTUBE_TITLES[date]
        print(f"  {date}: {len(posts)} posts found")

        # Fetch full details for all posts to find content + new video
        full_posts = []
        for p in posts:
            full = get_full_post(p["_id"])
            if full:
                full_posts.append(full)

        # Find the post with real content (check LinkedIn customContent)
        content_map = {}
        for fp in full_posts:
            li_content = next(
                (pl.get("customContent", "") for pl in fp.get("platforms", []) if pl.get("platform") == "linkedin"),
                fp.get("content", "")
            )
            if li_content and len(li_content) > 50:
                content_map = {
                    "linkedin": li_content,
                    "instagram": next((pl.get("customContent","") for pl in fp.get("platforms",[]) if pl.get("platform")=="instagram"), li_content),
                    "facebook":  next((pl.get("customContent","") for pl in fp.get("platforms",[]) if pl.get("platform")=="facebook"),  li_content),
                }
                print(f"    Content found: {len(li_content)} chars")
                break

        if not content_map:
            print(f"    [WARN] No content found for {date} — skipping")
            continue

        # Find the newest apr-XX.mp4 video URL (most recently created post with new video)
        new_video_url = None
        for fp in sorted(full_posts, key=lambda x: x.get("createdAt",""), reverse=True):
            media = fp.get("mediaItems", [])
            if media:
                url = media[0].get("url", "")
                slug = date.replace("2026-0", "apr-0").replace("2026-", "apr-")
                # apr-02 from 2026-04-02
                slug = "apr-" + date[8:10].lstrip("0").zfill(2)
                if slug in url:
                    new_video_url = url
                    print(f"    New video: ...{url[-35:]}")
                    break

        if not new_video_url:
            print(f"    [WARN] No new apr-XX.mp4 video found for {date} — skipping")
            continue

        # Get scheduled time from original post
        scheduled_for = full_posts[0].get("scheduledFor", f"{date}T13:00:00")[:19]

        # Delete all posts for this date
        for fp in full_posts:
            delete_post(fp["_id"])
        print(f"    Deleted {len(full_posts)} posts")

        # Create one clean post
        status = create_post(scheduled_for, new_video_url, content_map, yt_title)
        if status in (200, 201):
            print(f"    ✓ Created clean post at {scheduled_for}")
        else:
            print(f"    ✗ Create failed with status {status}")

    print("\nDone.")


if __name__ == "__main__":
    main()
