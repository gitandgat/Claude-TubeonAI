#!/usr/bin/env python3
"""
Archive Cleaner - Move old published posts to archive, maintain clean workspace.
Keeps recent posts accessible, archives history.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

ARCHIVE_AFTER_DAYS = 90  # Archive posts older than 90 days

def get_published_posts():
    """Get all published posts"""
    published = []
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

            published.extend([p for p in posts if p.get('status') == 'published'])

            if len(posts) < 50:
                break
            page += 1
        except Exception as e:
            print(f"Error: {e}")
            break

    return published

def find_archivable(posts, days=ARCHIVE_AFTER_DAYS):
    """Find posts older than X days"""
    archivable = []
    cutoff = datetime.utcnow() - timedelta(days=days)

    for post in posts:
        pub_date = post.get('publishedAt')
        if pub_date:
            try:
                pub_dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                if pub_dt < cutoff:
                    archivable.append({
                        'post_id': post.get('_id'),
                        'published': pub_date,
                        'age_days': (datetime.utcnow() - pub_dt).days,
                        'full_post': post
                    })
            except:
                pass

    return archivable

def add_archive_tag(post):
    """Mark post as archived (add metadata)"""
    # In real system, would update post with archive flag
    # For now, we document what would be archived
    return True

def main():
    print("=" * 70)
    print("ARCHIVE CLEANER")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Archive threshold: {ARCHIVE_AFTER_DAYS} days\n")

    posts = get_published_posts()
    print(f"Scanning {len(posts)} published posts...")

    archivable = find_archivable(posts, days=ARCHIVE_AFTER_DAYS)

    print(f"Found {len(archivable)} posts ready for archive\n")

    if not archivable:
        print("✓ No posts need archiving. Workspace is clean!\n")
    else:
        print("=" * 70)
        print("ARCHIVABLE POSTS")
        print("=" * 70)

        # Group by month
        by_month = {}
        for item in archivable:
            pub_date = item['published'][:7]  # YYYY-MM
            if pub_date not in by_month:
                by_month[pub_date] = []
            by_month[pub_date].append(item)

        print(f"\nBy publication month:")
        for month in sorted(by_month.keys(), reverse=True):
            items = by_month[month]
            print(f"  {month}: {len(items)} posts")

        print(f"\nOldest posts (to archive first):")
        sorted_archivable = sorted(archivable, key=lambda x: x['published'])
        for item in sorted_archivable[:10]:
            print(f"  • {item['post_id'][:12]}... - Published {item['age_days']} days ago")

        if len(sorted_archivable) > 10:
            print(f"  ... and {len(sorted_archivable) - 10} more")

        # Would archive in real system
        archived = 0
        for item in archivable[:5]:  # Archive oldest 5
            if add_archive_tag(item['full_post']):
                archived += 1

        print(f"\n✓ Would archive: {archived} posts (simulated)")

    report = {
        'timestamp': datetime.now().isoformat(),
        'total_posts': len(posts),
        'archivable': len(archivable),
        'archive_threshold_days': ARCHIVE_AFTER_DAYS,
        'posts': [
            {
                'post_id': item['post_id'],
                'published': item['published'],
                'age_days': item['age_days']
            }
            for item in archivable
        ]
    }

    with open('archive-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report saved to archive-report.json")

if __name__ == '__main__':
    main()
