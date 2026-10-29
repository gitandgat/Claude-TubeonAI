#!/usr/bin/env python3
"""
Remove platform labels from post content (e.g., "# LinkedIn Post", "# TikTok Reel")
These should not appear in the body content.
"""

import os
import re
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

PLATFORM_LABELS = [
    r'#\s*(LinkedIn|Instagram|Facebook|TikTok|YouTube|Twitter|X)\s*P(ost|romo|ull|hoto|romo)',
    r'#\s*(LinkedIn|Instagram|Facebook|TikTok|YouTube|Twitter|X)\s*(Post|Content|Reel|Video|Copy)',
    r'^(LinkedIn Post|Instagram Post|Facebook Post|TikTok Post|YouTube Post)',
    r'^(LinkedIn Reels?|Instagram Reels?|TikTok Reels?)',
]

def strip_platform_labels(content):
    """Remove platform headers from content"""
    original = content

    # Remove markdown headers with platform names
    for pattern in PLATFORM_LABELS:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)

    # Clean up extra whitespace/newlines created by removal
    content = re.sub(r'^[\s\n]+', '', content)  # Leading whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)  # Multiple blank lines

    changed = content != original
    return content, changed

def get_all_posts():
    """Fetch all posts from Zernio"""
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
            posts = data.get('posts', [])
            all_posts.extend(posts)

            if len(posts) < per_page:
                break
            page += 1
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    return all_posts

def update_post(post_id, post_data):
    """Update post to Zernio"""
    try:
        # Fix accountIds
        if 'platforms' in post_data:
            for platform in post_data['platforms']:
                if isinstance(platform.get('accountId'), dict):
                    platform['accountId'] = platform['accountId'].get('_id')

        put_response = requests.put(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=post_data,
            timeout=30
        )
        return put_response.status_code in (200, 201)
    except Exception as e:
        return False

def main():
    print("=" * 70)
    print("REMOVE PLATFORM LABELS FROM POST CONTENT")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}\n")

    # Get all posts
    print("Fetching all posts...")
    posts = get_all_posts()
    print(f"Found {len(posts)} posts\n")

    # Find posts with platform labels
    to_update = []
    for post in posts:
        content = post.get('content', '')
        cleaned, changed = strip_platform_labels(content)

        if changed:
            to_update.append({
                'post_id': post.get('_id'),
                'original_content': content,
                'cleaned_content': cleaned,
                'full_post': post
            })

    print(f"Posts with platform labels: {len(to_update)}\n")

    if not to_update:
        print("✓ No posts need updating. All clean!\n")
        return

    # Update posts
    print(f"Updating {len(to_update)} posts...")
    successful = 0
    failed = 0

    for idx, item in enumerate(to_update):
        post_id = item['post_id']
        post = item['full_post']

        # Update content
        post['content'] = item['cleaned_content']

        if update_post(post_id, post):
            successful += 1
            print(f"  {idx+1}/{len(to_update)}: {post_id[:12]}... ✓")
        else:
            failed += 1
            print(f"  {idx+1}/{len(to_update)}: {post_id[:12]}... ✗")

        time.sleep(0.3)

    # Summary
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"✓ Updated: {successful}/{len(to_update)}")
    print(f"✗ Failed: {failed}/{len(to_update)}")

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_posts': len(posts),
        'posts_with_labels': len(to_update),
        'successful': successful,
        'failed': failed,
        'cleaned_posts': [
            {
                'post_id': item['post_id'],
                'original_length': len(item['original_content']),
                'cleaned_length': len(item['cleaned_content']),
                'bytes_removed': len(item['original_content']) - len(item['cleaned_content'])
            }
            for item in to_update
        ]
    }

    with open('strip-labels-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report saved to strip-labels-report.json")

    if successful == len(to_update):
        print(f"\n✓ All platform labels removed successfully!")

if __name__ == '__main__':
    main()
