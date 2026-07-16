#!/usr/bin/env python3
"""
Duplicate Detector - Find identical or similar content already scheduled.
Prevents accidental reposts and wasted posting slots.
"""

import os
import json
import requests
from difflib import SequenceMatcher
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

def get_all_posts():
    """Fetch all posts"""
    all_posts = []
    page = 1

    while True:
        try:
            response = requests.get(
                f"{BASE}/posts?limit=50&page={page}",
                headers=HEADERS,
                timeout=30
            )
            data = response.json()
            posts = data.get('posts', [])
            all_posts.extend(posts)

            if len(posts) < 50:
                break
            page += 1
        except Exception as e:
            print(f"Error: {e}")
            break

    return all_posts

def similarity_ratio(a, b):
    """Calculate content similarity (0-1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_duplicates(posts, threshold=0.85):
    """Find duplicate/similar content"""
    duplicates = []
    checked = set()

    for i, post1 in enumerate(posts):
        if post1.get('_id') in checked:
            continue

        content1 = post1.get('content', '').strip()
        if not content1 or len(content1) < 50:
            continue

        for j, post2 in enumerate(posts[i+1:], i+1):
            if post2.get('_id') in checked:
                continue

            content2 = post2.get('content', '').strip()
            if not content2 or len(content2) < 50:
                continue

            ratio = similarity_ratio(content1, content2)
            if ratio >= threshold:
                duplicates.append({
                    'post1_id': post1.get('_id'),
                    'post1_status': post1.get('status'),
                    'post1_scheduled': post1.get('scheduledFor'),
                    'post2_id': post2.get('_id'),
                    'post2_status': post2.get('status'),
                    'post2_scheduled': post2.get('scheduledFor'),
                    'similarity': ratio
                })
                checked.add(post2.get('_id'))

    return duplicates

def main():
    print("=" * 70)
    print("DUPLICATE DETECTOR")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}\n")

    posts = get_all_posts()
    print(f"Scanning {len(posts)} posts...")
    print(f"Threshold: 85% similarity\n")

    duplicates = find_duplicates(posts, threshold=0.85)

    print("=" * 70)
    print("DUPLICATE REPORT")
    print("=" * 70)

    if not duplicates:
        print(f"\n✓ No duplicates found. Content library is clean!\n")
    else:
        print(f"\nFound {len(duplicates)} duplicate pairs:\n")

        for idx, dup in enumerate(duplicates[:10], 1):
            print(f"{idx}. Match: {dup['similarity']:.1%}")
            print(f"   Post 1: {dup['post1_id'][:12]}... ({dup['post1_status']})")
            if dup['post1_scheduled']:
                print(f"           Scheduled: {dup['post1_scheduled']}")
            print(f"   Post 2: {dup['post2_id'][:12]}... ({dup['post2_status']})")
            if dup['post2_scheduled']:
                print(f"           Scheduled: {dup['post2_scheduled']}")
            print()

        if len(duplicates) > 10:
            print(f"   ... and {len(duplicates) - 10} more duplicates")

    report = {
        'timestamp': datetime.now().isoformat(),
        'total_posts': len(posts),
        'duplicates_found': len(duplicates),
        'threshold': 0.85,
        'duplicates': duplicates[:20]
    }

    with open('duplicate-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✓ Report saved to duplicate-report.json")

if __name__ == '__main__':
    main()
