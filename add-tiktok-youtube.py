"""
Add TikTok and YouTube to every future Zernio post that is missing them.

Strategy for each eligible post:
  1. Fetch full post details
  2. Build new platforms list = existing platforms + missing TT/YT
  3. Delete old post
  4. Recreate with all platforms

Skips:
  - Posts with scheduledFor in the past (before today: 2026-03-28)
  - Posts whose only media is 'document' (not supported on TT/YT)
  - Posts that already have both TikTok AND YouTube
"""
import requests
import json
import sys

BASE    = "https://zernio.com/api/v1"
from zernio_key import ZERNIO_API_KEY as API_KEY
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

TIKTOK_ID  = "690941425f6fbb9ef8323078"
YOUTUBE_ID = "690940d35f6fbb9ef8323077"

CUTOFF_DATE = "2026-03-28"  # only process posts on or after this date

DRY_RUN = "--dry-run" in sys.argv  # pass --dry-run to preview without making changes


# ── helpers ──────────────────────────────────────────────────────────────────

def fetch_all_posts():
    """Fetch all posts, handling pagination."""
    all_posts = []
    page = 1
    while True:
        r = requests.get(f"{BASE}/posts", headers=HEADERS,
                         params={"limit": 100, "page": page})
        r.raise_for_status()
        data = r.json()
        batch = data.get("posts", [])
        all_posts.extend(batch)
        # Stop if we got fewer than 100 (last page) or no pagination info
        if len(batch) < 100:
            break
        page += 1
    return all_posts


def fetch_post_full(post_id):
    r = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS)
    if r.status_code == 200:
        d = r.json()
        return d.get("post", d)
    return None


def delete_post(post_id):
    r = requests.delete(f"{BASE}/posts/{post_id}", headers=HEADERS)
    if r.status_code not in (200, 204, 404):
        print(f"    [WARN] DELETE returned {r.status_code}: {r.text[:200]}")


def first_line(text, max_chars=100):
    for line in text.split("\n"):
        line = line.strip()
        if line:
            return line[:max_chars - 3] + "..." if len(line) > max_chars else line
    return "Crosswalk Wisdom"


def build_platform_object(platform, account_id, content, scheduled_for, yt_title=None):
    obj = {
        "platform": platform,
        "accountId": account_id,
        "customContent": content,
        "scheduledFor": scheduled_for,
    }
    if platform == "youtube" and yt_title:
        obj["title"] = yt_title
    return obj


def create_post(content, media_items, platforms, scheduled_for, timezone):
    body = {
        "content": content,
        "mediaItems": media_items,
        "platforms": platforms,
        "scheduledFor": scheduled_for,
        "timezone": timezone,
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    return r.status_code, r.text[:400]


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"{'[DRY RUN] ' if DRY_RUN else ''}Fetching all Zernio posts...")
    posts = fetch_all_posts()
    print(f"  Total posts: {len(posts)}\n")

    to_fix = []
    for p in posts:
        post_id = p["_id"]
        platforms = p.get("platforms", [])
        platform_names = [pl["platform"] for pl in platforms]
        media_types = [m["type"] for m in p.get("mediaItems", [])]

        # Get scheduled date from first platform
        scheduled_for = None
        for pl in platforms:
            sf = pl.get("scheduledFor")
            if sf:
                scheduled_for = sf
                break

        # Skip posts with no future scheduled date
        if not scheduled_for:
            continue
        date_part = scheduled_for[:10]  # "YYYY-MM-DD"
        if date_part < CUTOFF_DATE:
            continue

        # Skip document-only posts (not supported on TikTok/YouTube)
        if media_types and all(t == "document" for t in media_types):
            continue

        has_tiktok  = "tiktok"  in platform_names
        has_youtube = "youtube" in platform_names

        if has_tiktok and has_youtube:
            continue  # already has both

        to_fix.append({
            "id": post_id,
            "scheduled_for": scheduled_for,
            "platform_names": platform_names,
            "media_types": media_types,
            "content_preview": p.get("content", "")[:60],
            "missing_tiktok": not has_tiktok,
            "missing_youtube": not has_youtube,
        })

    print(f"Posts to fix (missing TikTok or YouTube): {len(to_fix)}")
    for t in to_fix:
        missing = []
        if t["missing_tiktok"]:  missing.append("TikTok")
        if t["missing_youtube"]: missing.append("YouTube")
        print(f"  {t['scheduled_for'][:10]}  [{', '.join(missing)}]  {t['content_preview']}")

    if not to_fix:
        print("\nAll future posts already have TikTok and YouTube!")
        return

    if DRY_RUN:
        print("\n[DRY RUN] No changes made. Remove --dry-run to apply.")
        return

    print(f"\nProcessing {len(to_fix)} posts...\n")
    success = 0
    failed  = 0

    for item in to_fix:
        post_id      = item["id"]
        scheduled_for = item["scheduled_for"]
        print(f"  [{scheduled_for[:10]}] {item['content_preview']}")

        # Fetch full post details
        post = fetch_post_full(post_id)
        if not post:
            print(f"    [SKIP] Could not fetch post {post_id}\n")
            failed += 1
            continue

        main_content = post.get("content", "")
        media_items  = [{"url": m["url"], "type": m["type"]}
                        for m in post.get("mediaItems", [])]
        timezone     = post.get("timezone", "America/New_York")

        # Build content map from existing platforms
        content_map = {}
        existing_platforms = []
        for pl in post.get("platforms", []):
            platform = pl.get("platform", "")
            cc = pl.get("customContent") or main_content
            if platform:
                content_map[platform] = cc

            # Rebuild clean platform object (strip populated accountId back to ID string)
            account_id = pl.get("accountId")
            if isinstance(account_id, dict):
                account_id = account_id.get("_id", account_id)

            clean_pl = {
                "platform": platform,
                "accountId": account_id,
                "customContent": cc,
                "scheduledFor": pl.get("scheduledFor", scheduled_for),
            }
            if platform == "youtube":
                if pl.get("title"):
                    clean_pl["title"] = pl["title"]
            existing_platforms.append(clean_pl)

        # Determine TikTok content: prefer Instagram, else main content
        tt_content = content_map.get("instagram",
                     content_map.get("facebook",
                     content_map.get("linkedin", main_content)))

        # Determine YouTube content: LinkedIn copy + hashtags
        li_content = content_map.get("linkedin",
                     content_map.get("facebook", main_content))
        yt_content = li_content + "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition"
        yt_title   = first_line(main_content, max_chars=100)

        # Append missing platforms
        new_platforms = list(existing_platforms)
        if item["missing_tiktok"]:
            new_platforms.append(build_platform_object(
                "tiktok", TIKTOK_ID, tt_content, scheduled_for))
        if item["missing_youtube"]:
            new_platforms.append(build_platform_object(
                "youtube", YOUTUBE_ID, yt_content, scheduled_for, yt_title=yt_title))

        # Delete old post, recreate with all platforms
        delete_post(post_id)
        status, resp = create_post(
            main_content, media_items, new_platforms, scheduled_for, timezone)

        if status in (200, 201):
            added = []
            if item["missing_tiktok"]:  added.append("TikTok")
            if item["missing_youtube"]: added.append("YouTube")
            print(f"    [OK] Added {', '.join(added)}\n")
            success += 1
        else:
            print(f"    [FAIL] {status}: {resp}\n")
            failed += 1

    print(f"\nDone. Success: {success}  Failed: {failed}")


if __name__ == "__main__":
    main()
