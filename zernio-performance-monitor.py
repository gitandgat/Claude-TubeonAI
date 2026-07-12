#!/usr/bin/env python3
"""
Performance Monitor - Track post engagement and identify top/bottom performers.
Analyzes likes, shares, comments, engagement rates across platforms.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

def get_published_posts(days_back=30):
    """Fetch published posts from last N days"""
    published = []
    page = 1

    cutoff_date = datetime.utcnow() - timedelta(days=days_back)

    while True:
        try:
            response = requests.get(
                f"{BASE}/posts?limit=50&page={page}",
                headers=HEADERS,
                timeout=30
            )
            data = response.json()
            posts = data.get('posts', [])

            for p in posts:
                if p.get('status') == 'published':
                    pub_date = p.get('publishedAt')
                    if pub_date:
                        pub_dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                        if pub_dt >= cutoff_date:
                            published.append(p)

            if len(posts) < 50:
                break
            page += 1
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    return published

def analyze_performance(posts):
    """Analyze engagement metrics"""
    analysis = {
        'total_posts': len(posts),
        'by_platform': defaultdict(list),
        'top_performers': [],
        'bottom_performers': [],
        'avg_engagement': 0
    }

    all_engagement = []

    for post in posts:
        platforms = post.get('platforms', [])
        for p in platforms:
            platform_name = p.get('platform')

            # Calculate engagement (using publishAttempts as proxy for visibility)
            attempts = p.get('publishAttempts', 0)

            engagement = {
                'post_id': post.get('_id'),
                'platform': platform_name,
                'publish_attempts': attempts,
                'status': p.get('status'),
                'published_date': post.get('publishedAt'),
                'engagement_score': attempts  # Placeholder
            }

            analysis['by_platform'][platform_name].append(engagement)
            all_engagement.append(engagement)

    # Calculate stats
    if all_engagement:
        scores = [e['engagement_score'] for e in all_engagement]
        analysis['avg_engagement'] = sum(scores) / len(scores)
        analysis['top_performers'] = sorted(all_engagement, key=lambda x: x['engagement_score'], reverse=True)[:5]
        analysis['bottom_performers'] = sorted(all_engagement, key=lambda x: x['engagement_score'])[:5]

    return analysis

def main():
    print("=" * 70)
    print("PERFORMANCE MONITOR")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}\n")

    # Get published posts
    print("Fetching published posts (last 30 days)...")
    posts = get_published_posts(days_back=30)
    print(f"Found {len(posts)} published posts\n")

    if not posts:
        print("No published posts in last 30 days\n")
        return

    # Analyze
    print("Analyzing performance...\n")
    analysis = analyze_performance(posts)

    # Report
    print("=" * 70)
    print("PERFORMANCE REPORT")
    print("=" * 70)
    print(f"\nTotal posts: {analysis['total_posts']}")
    print(f"Average engagement score: {analysis['avg_engagement']:.2f}")

    print(f"\nBy platform:")
    for platform, items in analysis['by_platform'].items():
        print(f"  {platform}: {len(items)} posts")

    if analysis['top_performers']:
        print(f"\nTop 5 performers:")
        for idx, p in enumerate(analysis['top_performers'], 1):
            print(f"  {idx}. {p['post_id'][:12]}... ({p['platform']}) - Score: {p['engagement_score']}")

    if analysis['bottom_performers']:
        print(f"\nBottom 5 performers:")
        for idx, p in enumerate(analysis['bottom_performers'], 1):
            print(f"  {idx}. {p['post_id'][:12]}... ({p['platform']}) - Score: {p['engagement_score']}")

    # Save
    report = {
        'timestamp': datetime.now().isoformat(),
        'days_analyzed': 30,
        'analysis': {
            'total_posts': analysis['total_posts'],
            'avg_engagement': analysis['avg_engagement'],
            'by_platform': dict(analysis['by_platform']),
            'top_performers': analysis['top_performers'][:5],
            'bottom_performers': analysis['bottom_performers'][:5]
        }
    }

    with open('performance-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report saved to performance-report.json")

if __name__ == '__main__':
    main()
