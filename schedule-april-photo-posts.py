"""
Add a photo-only post for every April date (skip Apr 1, 8, 17 — already have image posts).
- Pulls content from existing Zernio posts (safe — not deleting anything)
- Uploads the mapped Freepik image via presigned URL
- Schedules at 11am ET (15:00 UTC) — between the 9am overlay and 1pm cinematic
- Posts to LI / IG / FB / TT only (no YouTube — image posts reject YouTube)
"""
import os, requests, time

BASE    = "https://zernio.com/api/v1"
API_KEY = "***REMOVED-ZERNIO-KEY***"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TIMEZONE     = "America/New_York"

ASSETS = "/Users/toto/Claude TubeonAI/crosswalk-remotion/public/assets/april"

# ── Image map: date → filename ────────────────────────────────────────────────
# Specific branded images for the 15 cinematic dates (+Apr 6)
# Thematic Freepik generics for the remaining 12 dates
IMAGE_MAP = {
    "2026-04-02": "apr-02.jpeg",
    "2026-04-03": "apr-03.jpeg",
    "2026-04-04": "apr-04.jpeg",
    "2026-04-05": "freepik__a-person-sitting-alone-in-a-softly-lit-hospital-co__52553.jpeg",  # grief/hospital corridor
    "2026-04-06": "apr-06.jpeg",
    "2026-04-07": "apr-07.jpeg",
    "2026-04-09": "apr-09.jpeg",
    "2026-04-10": "freepik__cinematic-portrait-of-a-south-asian-man-in-his-40s__52542.jpeg",  # fear of judgment / personal
    "2026-04-11": "freepik__overhead-flatlay-of-a-warm-wooden-table-with-an-op__52558.jpeg",  # Adler / philosophy / reflection
    "2026-04-12": "freepik__closeup-of-a-persons-hands-resting-on-an-open-lapt__52544.jpeg",  # ICU nurse story / writing
    "2026-04-13": "apr-13.jpeg",
    "2026-04-14": "apr-14.jpeg",
    "2026-04-15": "freepik__a-persons-hands-typing-on-a-laptop-at-a-cozy-woode__52557.jpeg",  # AI prompts / laptop
    "2026-04-16": "apr-16.jpeg",
    "2026-04-18": "apr-18.jpeg",
    "2026-04-19": "freepik__a-pair-of-folded-blue-hospital-scrubs-resting-neat__52543.jpeg",  # wellness gaslighting / scrubs
    "2026-04-20": "freepik__cinematic-shot-of-a-person-walking-across-a-wet-ci__52554.jpeg",  # Fear Audit launch / crossing
    "2026-04-21": "apr-21.jpeg",
    "2026-04-22": "freepik__soft-cream-paper-texture-on-a-warm-white-backgroun__52551.jpeg",  # in-between phase / minimalist
    "2026-04-23": "apr-23.jpeg",
    "2026-04-24": "freepik__a-handwritten-letter-on-cream-textured-paper-lying__52555.jpeg",  # letter to struggling HCWs
    "2026-04-25": "apr-25.jpeg",
    "2026-04-26": "freepik__a-city-pedestrian-traffic-signal-light-changing-fr__52547.jpeg",  # Sunday thought / crosswalk
    "2026-04-27": "freepik__a-clean-warm-flatlay-of-a-clipboard-with-a-white-n__52549.jpeg",  # AI use case / organised
    "2026-04-28": "apr-28.jpeg",
    "2026-04-29": "freepik__closeup-of-a-pair-of-hands-gently-placing-a-hospit__52545.jpeg",  # month 1 reflection / badge
    "2026-04-30": "apr-30.jpeg",
}

PHOTO_TIME = "11:00:00"  # 11am ET = 15:00 UTC, between overlay (5am) and cinematic (1pm)


def get_all_posts():
    r = requests.get(f"{BASE}/posts?limit=200", headers={"Authorization": f"Bearer {API_KEY}"})
    r.raise_for_status()
    return r.json().get("posts", [])


def get_full_post(post_id):
    r = requests.get(f"{BASE}/posts/{post_id}", headers={"Authorization": f"Bearer {API_KEY}"})
    if r.status_code == 200:
        data = r.json()
        return data.get("post", data)
    return None


def extract_content(full_post):
    """Pull per-platform customContent, fall back to top-level content."""
    platforms = full_post.get("platforms", [])
    def plat(name):
        return next((p.get("customContent", "") for p in platforms if p.get("platform") == name), "")

    li = plat("linkedin") or full_post.get("content", "")
    ig = plat("instagram") or li
    fb = plat("facebook") or li
    tt = plat("tiktok") or ig
    return li, ig, fb, tt


def upload_image(filename):
    filepath = os.path.join(ASSETS, filename)
    filesize = os.path.getsize(filepath)
    r = requests.post(f"{BASE}/media/presign", headers=HEADERS,
        json={"filename": filename, "contentType": "image/jpeg", "fileSize": filesize})
    r.raise_for_status()
    data = r.json()
    with open(filepath, "rb") as f:
        requests.put(data["uploadUrl"], data=f,
            headers={"Content-Type": "image/jpeg"}).raise_for_status()
    return data["publicUrl"]


def create_photo_post(scheduled_for, image_url, li, ig, fb, tt):
    body = {
        "content": li,
        "mediaItems": [{"url": image_url, "type": "image"}],
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
        "platforms": [
            {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": li, "scheduledFor": scheduled_for},
            {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": ig, "scheduledFor": scheduled_for},
            {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": fb, "scheduledFor": scheduled_for},
            {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": tt, "scheduledFor": scheduled_for},
        ],
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    return r.status_code, r.text[:300]


def main():
    print("Fetching existing posts from Zernio...")
    all_posts = get_all_posts()

    # Group by date, prefer posts with most platforms (cinematic/WAVE1 over overlays)
    from collections import defaultdict
    by_date = defaultdict(list)
    for p in all_posts:
        d = p.get("scheduledFor", "")[:10]
        if d in IMAGE_MAP:
            by_date[d].append(p)

    dates = sorted(IMAGE_MAP.keys())
    print(f"Scheduling photo posts for {len(dates)} dates at {PHOTO_TIME} ET...\n")

    success = 0
    for date in dates:
        img_file = IMAGE_MAP[date]
        scheduled_for = f"{date}T{PHOTO_TIME}"

        # Find the best existing post to source content from
        # Prefer the cinematic post (17:00 UTC) or WAVE1 post (13:00 UTC), not overlay (09:00)
        posts_for_date = by_date.get(date, [])
        source_post = None
        for p in sorted(posts_for_date, key=lambda x: len(x.get("platforms", [])), reverse=True):
            t = p.get("scheduledFor", "")[11:13]
            if t in ("13", "17"):  # 13:00 UTC (9am ET) or 17:00 UTC (1pm ET)
                source_post = p
                break
        if not source_post and posts_for_date:
            source_post = posts_for_date[0]

        if not source_post:
            print(f"  {date}  ✗ No source post found — skipping")
            continue

        print(f"  {date}  [{img_file[:30]}...]")

        # Fetch full post for per-platform content
        full = get_full_post(source_post["_id"])
        if not full:
            print(f"    ✗ Could not fetch full post")
            continue

        li, ig, fb, tt = extract_content(full)
        if not li:
            print(f"    ✗ No content found")
            continue

        # Upload image
        try:
            image_url = upload_image(img_file)
        except Exception as e:
            print(f"    ✗ Upload failed: {e}")
            continue

        # Create photo post
        status, resp = create_photo_post(scheduled_for, image_url, li, ig, fb, tt)
        if status in (200, 201):
            print(f"    ✓ Scheduled at {scheduled_for} ET")
            success += 1
        else:
            print(f"    ✗ Create failed {status}: {resp}")

        time.sleep(1)

    print(f"\nDone. {success}/{len(dates)} photo posts created.")


if __name__ == "__main__":
    main()
