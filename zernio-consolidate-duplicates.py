#!/usr/bin/env python3
"""
Consolidate duplicates - Keep first, archive rest.
Removes 170 redundant posts, keeps original scheduled date.
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

def delete_post(post_id):
    """Delete a post from Zernio"""
    try:
        response = requests.delete(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            timeout=30
        )
        return response.status_code in (200, 204)
    except Exception as e:
        return False

def consolidate_duplicates():
    """Load duplicates from report and delete duplicates"""

    # Load duplicate report
    with open('duplicate-report.json', 'r') as f:
        report = json.load(f)

    duplicates = report.get('duplicates', [])

    print("=" * 70)
    print("CONSOLIDATING DUPLICATES")
    print("=" * 70)
    print(f"\nFound {len(duplicates)} duplicate pairs\n")

    # Track which posts to delete
    to_delete = set()
    kept_posts = set()

    for dup in duplicates:
        post1 = dup['post1_id']
        post2 = dup['post2_id']
        scheduled1 = dup['post1_scheduled']
        scheduled2 = dup['post2_scheduled']

        # Keep the one scheduled first (earlier date)
        if scheduled1 < scheduled2:
            kept = post1
            delete = post2
        else:
            kept = post2
            delete = post1

        kept_posts.add(kept)
        to_delete.add(delete)

    print(f"Posts to keep: {len(kept_posts)}")
    print(f"Posts to delete: {len(to_delete)}\n")

    # Delete duplicates
    deleted = 0
    failed = 0

    for idx, post_id in enumerate(sorted(to_delete), 1):
        print(f"  [{idx}/{len(to_delete)}] Deleting {post_id[:12]}...", end=" ")

        if delete_post(post_id):
            deleted += 1
            print("✓")
        else:
            failed += 1
            print("✗")

    print("\n" + "=" * 70)
    print("CONSOLIDATION COMPLETE")
    print("=" * 70)
    print(f"\n✓ Deleted: {deleted}/{len(to_delete)}")
    print(f"✗ Failed: {failed}/{len(to_delete)}")
    print(f"✓ Kept originals: {len(kept_posts)}")

    print(f"\nResult:")
    print(f"  Posts before: {report['total_posts']}")
    print(f"  Posts removed: {deleted}")
    print(f"  Posts after: {report['total_posts'] - deleted}")
    print(f"  Efficiency gain: {deleted} fewer posts = less posting overhead")

    # Save consolidation report
    consolidation_report = {
        'timestamp': datetime.now().isoformat(),
        'action': 'consolidate_duplicates',
        'total_duplicates': len(duplicates),
        'posts_deleted': deleted,
        'posts_failed': failed,
        'posts_kept': len(kept_posts),
        'final_post_count': report['total_posts'] - deleted,
        'efficiency': f"{(deleted / report['total_posts'] * 100):.1f}% reduction"
    }

    with open('consolidation-report.json', 'w') as f:
        json.dump(consolidation_report, f, indent=2)

    print(f"\n✓ Report saved to consolidation-report.json")

    return {
        'deleted': deleted,
        'failed': failed,
        'kept': len(kept_posts)
    }

if __name__ == '__main__':
    result = consolidate_duplicates()
