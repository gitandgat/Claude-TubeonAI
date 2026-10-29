#!/usr/bin/env python3
"""
Fix Zernio draft posts: restore status from draft → scheduled
Without modifying any other fields (content, firstComment, platforms, etc.)
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY environment variable not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

def list_draft_posts():
    """Fetch all draft posts from Zernio (with pagination)"""
    print("Fetching all draft posts from Zernio...")
    all_posts = []
    page = 1
    per_page = 50

    while True:
        try:
            response = requests.get(
                f"{BASE}/posts?status=draft&page={page}&limit={per_page}",
                headers=HEADERS,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Handle both list and dict responses
            if isinstance(data, dict) and 'data' in data:
                posts = data['data']
            elif isinstance(data, dict) and 'posts' in data:
                posts = data['posts']
            elif isinstance(data, list):
                posts = data
            else:
                print(f"Unexpected response format on page {page}: {type(data)}")
                break

            if not posts:
                break  # No more posts

            all_posts.extend(posts)
            print(f"  Page {page}: fetched {len(posts)} posts (total: {len(all_posts)})")

            # Check if this is the last page
            if len(posts) < per_page:
                break

            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

    return all_posts

def fix_post_status(post_id, post_data):
    """
    Update post status from draft to scheduled.
    Only updates status field, preserves everything else.
    """
    # Extract the scheduledFor date from the post data
    scheduled_for = post_data.get('scheduledFor')
    if not scheduled_for:
        print(f"  Skipping {post_id}: no scheduledFor date found")
        return False

    # Minimal payload: only status, preserves all other fields
    update_body = {
        "status": "scheduled"
    }

    try:
        response = requests.put(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=update_body,
            timeout=30
        )

        if response.status_code in (200, 201):
            print(f"  ✓ {post_id}: draft → scheduled")
            return True
        elif response.status_code == 403:
            print(f"  ✗ {post_id}: 403 Forbidden (may need special permissions)")
            return False
        elif response.status_code == 404:
            print(f"  ✗ {post_id}: 404 Not Found")
            return False
        else:
            print(f"  ✗ {post_id}: {response.status_code} — {response.text[:150]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ {post_id}: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("Zernio Draft Status Fix — Restore to Scheduled")
    print("=" * 70)

    # Fetch all draft posts
    draft_posts = list_draft_posts()

    if not draft_posts:
        print("\n⚠️  No draft posts found (or API returned no data)")
        return

    print(f"\nFound {len(draft_posts)} draft posts")
    print("\nAttempting to restore status to 'scheduled'...\n")

    successful = 0
    failed = 0

    for idx, post in enumerate(draft_posts):
        post_id = post.get('id') or post.get('_id')
        if not post_id:
            print(f"  ✗ Post {idx}: No ID found")
            failed += 1
            continue

        if fix_post_status(post_id, post):
            successful += 1
        else:
            failed += 1

        # Small delay to avoid rate limiting
        if idx < len(draft_posts) - 1:
            import time
            time.sleep(0.5)

    # Summary
    print("\n" + "=" * 70)
    print(f"Results: {successful} fixed, {failed} failed")
    print("=" * 70)

    if successful > 0:
        print(f"\n✓ {successful} posts restored to scheduled status")

    if failed > 0:
        print(f"\n⚠️  {failed} posts failed to update")
        print("   Check Zernio dashboard or contact support for manual fix")

if __name__ == '__main__':
    main()
