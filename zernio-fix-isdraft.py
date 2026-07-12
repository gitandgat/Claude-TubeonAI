#!/usr/bin/env python3
"""
Fix all 106 draft posts by setting isDraft: false
This is the correct way to change posts from draft → scheduled in Zernio API
"""

import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY environment variable not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

def get_all_draft_posts():
    """Fetch all draft posts"""
    all_posts = []
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

            if isinstance(data, dict) and 'posts' in data:
                posts = data['posts']
            elif isinstance(data, dict) and 'data' in data:
                posts = data['data']
            else:
                break

            draft_posts = [p for p in posts if p.get('status') == 'draft']
            all_posts.extend(draft_posts)

            if len(posts) < per_page:
                break

            page += 1

        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    return all_posts

def fix_post_draft_status(post_id, scheduled_for):
    """
    Fix post by setting isDraft: false (the correct way)
    """
    try:
        update_body = {
            "isDraft": False,
            "scheduledFor": scheduled_for
        }

        response = requests.put(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=update_body,
            timeout=30
        )

        if response.status_code in (200, 201):
            return True, "OK"
        else:
            error_msg = response.text[:100] if response.text else f"Status {response.status_code}"
            return False, error_msg

    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("Fix Draft Posts - Set isDraft: false (Correct Method)")
    print("=" * 70)

    # Fetch draft posts
    draft_posts = get_all_draft_posts()
    print(f"\nFound {len(draft_posts)} draft posts\n")

    if not draft_posts:
        print("No draft posts to fix")
        return

    successful = 0
    failed = 0
    failed_posts = []

    print("Fixing draft posts...\n")

    for idx, post in enumerate(draft_posts):
        post_id = post.get('id') or post.get('_id')
        scheduled_for = post.get('scheduledFor')

        if not scheduled_for:
            print(f"  ✗ {post_id}: No scheduledFor date found")
            failed += 1
            continue

        success, msg = fix_post_draft_status(post_id, scheduled_for)

        if success:
            successful += 1
        else:
            failed += 1
            failed_posts.append((post_id, msg))

        # Progress indicator
        if (idx + 1) % 10 == 0:
            print(f"  {idx + 1}/{len(draft_posts)} posts processed ({successful} OK, {failed} failed)")

        # Rate limiting
        time.sleep(0.3)

    # Summary
    print("\n" + "=" * 70)
    print("Results")
    print("=" * 70)
    print(f"✓ Fixed (isDraft: false): {successful}/{len(draft_posts)}")
    print(f"✗ Failed: {failed}/{len(draft_posts)}")

    if failed > 0:
        print(f"\nFirst 10 failures:")
        for post_id, msg in failed_posts[:10]:
            print(f"  {post_id}: {msg}")

    print("\n" + "=" * 70)
    if successful == len(draft_posts):
        print("✓ All 106 posts successfully set to scheduled!")
        print("✓ 5-posts-per-day schedule is now active (June 6-27)")
    else:
        print(f"⚠️  {failed} posts still need fixing")

if __name__ == '__main__':
    main()
