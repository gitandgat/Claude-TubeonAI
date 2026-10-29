#!/usr/bin/env python3
"""
Diagnose why posts are showing FAILED status in Zernio
Check error messages and identify common failure patterns
"""

import os
import json
import requests
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY environment variable not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

def get_all_posts_with_status():
    """Fetch all posts and categorize by status"""
    status_map = defaultdict(list)
    page = 1
    per_page = 50

    print("Fetching all posts...\n")

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

            for post in posts:
                status = post.get('status', 'unknown')
                status_map[status].append(post)

            print(f"  Page {page}: {len(posts)} posts")

            if len(posts) < per_page:
                break

            page += 1

        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    return status_map

def diagnose_failed_posts(failed_posts):
    """Examine failed posts to understand why they failed"""
    print("\n" + "=" * 70)
    print("FAILED POSTS ANALYSIS")
    print("=" * 70)
    print(f"\nTotal failed: {len(failed_posts)}\n")

    if not failed_posts:
        print("No failed posts found.")
        return

    # Check first 5 failed posts for error details
    error_patterns = defaultdict(int)
    missing_fields = defaultdict(int)

    for idx, post in enumerate(failed_posts[:5]):
        post_id = post.get('id') or post.get('_id')
        print(f"\nFailed Post #{idx + 1}: {post_id}")
        print(f"  Title: {post.get('title', 'N/A')[:60]}")
        print(f"  Scheduled for: {post.get('scheduledFor', 'N/A')}")
        print(f"  isDraft: {post.get('isDraft', 'N/A')}")
        print(f"  Platforms: {len(post.get('platforms', []))} platforms")

        # Check for missing critical fields
        if not post.get('content'):
            missing_fields['content'] += 1
            print(f"  ⚠️  Missing: content")
        if not post.get('mediaItems') or len(post.get('mediaItems', [])) == 0:
            missing_fields['mediaItems'] += 1
            print(f"  ⚠️  Missing: mediaItems (image)")
        if not post.get('scheduledFor'):
            missing_fields['scheduledFor'] += 1
            print(f"  ⚠️  Missing: scheduledFor")

        platforms = post.get('platforms', [])
        if not platforms:
            missing_fields['platforms'] += 1
            print(f"  ⚠️  Missing: platforms configuration")
        else:
            for platform in platforms:
                if not platform.get('accountId'):
                    missing_fields[f'platforms.{platform.get("platform")}.accountId'] += 1
                    print(f"  ⚠️  Missing: accountId for {platform.get('platform')}")

    # Summary of patterns
    if error_patterns or missing_fields:
        print("\n" + "=" * 70)
        print("Common Issues Found:")
        print("=" * 70)
        if missing_fields:
            for field, count in sorted(missing_fields.items(), key=lambda x: -x[1]):
                print(f"  Missing '{field}': {count} posts")

def main():
    print("=" * 70)
    print("Zernio Post Failure Diagnosis")
    print("=" * 70)

    # Get all posts by status
    status_map = get_all_posts_with_status()

    # Print summary
    print("\n" + "=" * 70)
    print("STATUS SUMMARY")
    print("=" * 70)
    total = 0
    for status in sorted(status_map.keys()):
        count = len(status_map[status])
        total += count
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {status.upper():15} {count:4} posts")

    print(f"\n  TOTAL:          {total:4} posts")

    # Diagnose failed posts
    if 'failed' in status_map:
        diagnose_failed_posts(status_map['failed'])
    else:
        print("\n✓ No failed posts found!")

    # Check scheduled posts that might have issues
    if 'scheduled' in status_map:
        scheduled = status_map['scheduled']
        print("\n" + "=" * 70)
        print("SCHEDULED POSTS CHECK")
        print("=" * 70)
        print(f"Total scheduled: {len(scheduled)}")

        # Sample a few scheduled posts to ensure they're correct
        print("\nSample of scheduled posts (first 3):")
        for idx, post in enumerate(scheduled[:3]):
            post_id = post.get('id') or post.get('_id')
            print(f"\n  Post #{idx + 1}: {post_id}")
            print(f"    Title: {post.get('title', 'N/A')[:50]}")
            print(f"    Scheduled: {post.get('scheduledFor', 'N/A')}")
            print(f"    Platforms: {len(post.get('platforms', []))}")
            print(f"    Has image: {'Yes' if post.get('mediaItems') else 'No'}")

if __name__ == '__main__':
    main()
