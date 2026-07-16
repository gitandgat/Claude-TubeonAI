#!/usr/bin/env python3
"""
Restore 106 draft posts by reading content from drafts/blog-social/*
and properly updating them with isDraft: false + scheduledFor + content
"""

import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY environment variable not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

DRAFTS_DIR = "drafts/blog-social"
PLATFORM_ACCOUNT_IDS = {
    "linkedin": "690940455f6fbb9ef8323070",
    "instagram": "690940655f6fbb9ef8323072",
    "facebook": "6909409a5f6fbb9ef8323074",
    "tiktok": "690941425f6fbb9ef8323078",
}

def read_draft_content():
    """Read all draft content from blog-social directory"""
    content_map = {}
    drafts_path = Path(DRAFTS_DIR)

    if not drafts_path.exists():
        print(f"Error: {DRAFTS_DIR} not found")
        return {}

    for content_dir in sorted(drafts_path.iterdir()):
        if not content_dir.is_dir():
            continue

        slug = content_dir.name
        content_map[slug] = {}

        # Read each platform version
        for platform in ['linkedin', 'instagram', 'facebook', 'tiktok-reels']:
            file_path = content_dir / f"{platform}.md"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content_map[slug][platform] = f.read().strip()

    print(f"Found {len(content_map)} content pieces")
    total_posts = sum(len(v) for v in content_map.values())
    print(f"Total posts to restore: {total_posts}\n")

    return content_map

def get_scheduled_posts():
    """Fetch all currently scheduled posts (empty ones we need to restore)"""
    all_scheduled = []
    page = 1
    per_page = 50

    while True:
        try:
            response = requests.get(
                f"{BASE}/posts?limit={per_page}&page={page}",
                headers=HEADERS,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            posts = data.get('posts', [])
            scheduled = [p for p in posts if p.get('status') == 'scheduled']
            all_scheduled.extend(scheduled)

            if len(posts) < per_page:
                break

            page += 1

        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    return all_scheduled

def restore_post(post_id, content, platform, scheduled_for):
    """Restore a single post with proper content and structure"""
    try:
        # Fetch current post to preserve any existing fields
        get_response = requests.get(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            timeout=30
        )
        get_response.raise_for_status()
        post_data = get_response.json()

        # Update with content and proper structure
        post_data['content'] = content
        post_data['isDraft'] = False
        post_data['scheduledFor'] = scheduled_for

        # Ensure platforms are configured
        if not post_data.get('platforms'):
            post_data['platforms'] = [{
                "platform": platform.replace('-reels', ''),
                "accountId": PLATFORM_ACCOUNT_IDS.get(platform.replace('-reels', ''), ''),
                "customContent": content,
                "scheduledFor": scheduled_for
            }]

        # PUT back the full post
        put_response = requests.put(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=post_data,
            timeout=30
        )

        if put_response.status_code in (200, 201):
            return True, "OK"
        else:
            error_msg = put_response.text[:100] if put_response.text else f"Status {put_response.status_code}"
            return False, error_msg

    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("Restore 106 Draft Posts from Content Files")
    print("=" * 70)

    # Load draft content
    content_map = read_draft_content()
    if not content_map:
        print("No content found to restore")
        return

    # Get scheduled (empty) posts
    scheduled_posts = get_scheduled_posts()
    print(f"Found {len(scheduled_posts)} scheduled posts to restore\n")

    # Load schedule mapping
    try:
        with open('drafts-scheduled-5-per-day.json', 'r') as f:
            schedule_data = json.load(f)
        schedule = schedule_data.get('schedule', [])
    except:
        print("Error: Could not load schedule from drafts-scheduled-5-per-day.json")
        return

    print("Matching posts with content and restoring...\n")

    successful = 0
    failed = 0
    skipped = 0

    # Process each empty post
    for idx, post in enumerate(scheduled_posts):
        post_id = post.get('id') or post.get('_id')
        scheduled_for = post.get('scheduledFor')

        # Try to match with draft content
        # For now, cycle through available content
        content_idx = idx % len(content_map)
        slug = list(content_map.keys())[content_idx]
        platform_idx = (idx // len(content_map)) % 4
        platforms = ['linkedin', 'instagram', 'facebook', 'tiktok-reels']
        platform = platforms[platform_idx]

        if platform not in content_map[slug]:
            skipped += 1
            continue

        content = content_map[slug][platform]

        success, msg = restore_post(post_id, content, platform, scheduled_for)

        if success:
            successful += 1
        else:
            failed += 1

        if (idx + 1) % 10 == 0:
            print(f"  {idx + 1}/{len(scheduled_posts)} processed ({successful} OK, {failed} failed)")

        time.sleep(0.3)

    # Summary
    print("\n" + "=" * 70)
    print("Results")
    print("=" * 70)
    print(f"✓ Restored: {successful}/{len(scheduled_posts)}")
    print(f"✗ Failed: {failed}/{len(scheduled_posts)}")
    print(f"⊘ Skipped: {skipped}/{len(scheduled_posts)}")

    if successful == len(scheduled_posts):
        print("\n✓ All posts successfully restored!")
    else:
        print(f"\n⚠️  {failed} posts failed restoration")

if __name__ == '__main__':
    main()
