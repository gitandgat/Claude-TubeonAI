#!/usr/bin/env python3
"""
Change status of 106 posts from draft → scheduled, one-by-one
Uses a smarter update approach: fetch current post, update only status field, then PUT back
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

def change_post_status(post_id):
    """
    Change single post status from draft to scheduled.
    Strategy: Fetch current post, modify status field, PUT back.
    """
    try:
        # Fetch current post data
        get_response = requests.get(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            timeout=30
        )
        get_response.raise_for_status()
        post_data = get_response.json()

        # Modify status
        post_data['status'] = 'scheduled'

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

    except requests.exceptions.RequestException as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("Change Draft Posts Status → Scheduled (One-by-One)")
    print("=" * 70)

    # Fetch draft posts
    draft_posts = get_all_draft_posts()
    print(f"\nFound {len(draft_posts)} draft posts\n")

    if not draft_posts:
        print("No draft posts to update")
        return

    successful = 0
    failed = 0
    failed_posts = []

    print("Changing status (this will take ~2-3 minutes)...\n")

    for idx, post in enumerate(draft_posts):
        post_id = post.get('id') or post.get('_id')

        success, msg = change_post_status(post_id)

        if success:
            successful += 1
        else:
            failed += 1
            failed_posts.append((post_id, msg))

        # Progress indicator
        if (idx + 1) % 10 == 0:
            print(f"  {idx + 1}/{len(draft_posts)} posts processed ({successful} OK, {failed} failed)")

        # Rate limiting - be conservative
        time.sleep(0.3)

    # Summary
    print("\n" + "=" * 70)
    print("Results")
    print("=" * 70)
    print(f"✓ Status changed: {successful}/{len(draft_posts)}")
    print(f"✗ Failed: {failed}/{len(draft_posts)}")

    if failed > 0:
        print(f"\nFirst 10 failures:")
        for post_id, msg in failed_posts[:10]:
            print(f"  {post_id}: {msg}")

        # Save failed list
        with open('failed-posts.json', 'w') as f:
            json.dump(failed_posts, f, indent=2)
        print(f"\n  Failed post list saved to failed-posts.json")

    print("\n" + "=" * 70)
    if successful == len(draft_posts):
        print("✓ All posts successfully changed to scheduled status!")
        print("✓ Your 5-posts-per-day schedule is now active (June 6-27)")
    else:
        print(f"⚠️  {failed} posts still in draft status - may need manual fix")

if __name__ == '__main__':
    main()
