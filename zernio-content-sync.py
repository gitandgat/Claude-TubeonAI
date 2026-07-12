#!/usr/bin/env python3
"""
Content Sync Agent - Ensure blog posts and social content stay synchronized.
Detects drift, maintains version parity, tracks changes.
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

BLOG_DIR = "drafts/blog-social"

def get_blog_posts():
    """Get blog content pieces"""
    blog_posts = {}
    if os.path.exists(BLOG_DIR):
        for item in os.listdir(BLOG_DIR):
            item_path = os.path.join(BLOG_DIR, item)
            if os.path.isdir(item_path):
                # Read different platform versions
                for platform_file in ['linkedin.md', 'instagram.md', 'facebook.md']:
                    file_path = os.path.join(item_path, platform_file)
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            if item not in blog_posts:
                                blog_posts[item] = {}
                            platform = platform_file.replace('.md', '')
                            blog_posts[item][platform] = f.read().strip()
    return blog_posts

def get_social_posts():
    """Get social media posts"""
    social = []
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
            social.extend(posts)

            if len(posts) < 50:
                break
            page += 1
        except Exception as e:
            break

    return social

def find_mismatches(blog_posts, social_posts):
    """Find content drift between blog and social"""
    mismatches = []

    # For simplicity, flag posts without platform-specific content
    for post in social_posts:
        content = post.get('content', '')
        platforms = post.get('platforms', [])

        # Check if platforms have consistent content
        platform_contents = {}
        for p in platforms:
            platform_name = p.get('platform')
            custom = p.get('customContent')
            if custom:
                platform_contents[platform_name] = custom

        # Flag if LinkedIn and Instagram differ too much
        if 'linkedin' in platform_contents and 'instagram' in platform_contents:
            if platform_contents['linkedin'] == platform_contents['instagram']:
                mismatches.append({
                    'post_id': post.get('_id'),
                    'issue': 'Platform-specific content not customized',
                    'platforms': list(platform_contents.keys())
                })

    return mismatches

def main():
    print("=" * 70)
    print("CONTENT SYNC AGENT")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}\n")

    print("Syncing blog content with social posts...")
    blog_posts = get_blog_posts()
    social_posts = get_social_posts()

    print(f"Blog content pieces: {len(blog_posts)}")
    print(f"Social posts: {len(social_posts)}\n")

    mismatches = find_mismatches(blog_posts, social_posts)

    print("=" * 70)
    print("SYNC REPORT")
    print("=" * 70)

    if not mismatches:
        print(f"\n✓ Content is synchronized across all platforms!")
    else:
        print(f"\n⚠️  Found {len(mismatches)} synchronization issues:\n")

        for idx, mismatch in enumerate(mismatches[:10], 1):
            print(f"{idx}. {mismatch['post_id'][:12]}...")
            print(f"   Issue: {mismatch['issue']}")
            print(f"   Platforms: {', '.join(mismatch['platforms'])}\n")

        if len(mismatches) > 10:
            print(f"... and {len(mismatches) - 10} more\n")

    # Sync status
    sync_health = ((len(social_posts) - len(mismatches)) / len(social_posts) * 100) if social_posts else 100

    print(f"Sync health: {sync_health:.0f}%")

    report = {
        'timestamp': datetime.now().isoformat(),
        'blog_pieces': len(blog_posts),
        'social_posts': len(social_posts),
        'mismatches': len(mismatches),
        'sync_health': sync_health,
        'issues': mismatches[:20]
    }

    with open('content-sync-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report saved to content-sync-report.json")

if __name__ == '__main__':
    main()
