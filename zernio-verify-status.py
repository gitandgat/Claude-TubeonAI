#!/usr/bin/env python3
"""
Verify actual status of posts we supposedly fixed
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY environment variable not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

def check_all_post_statuses():
    """Check status distribution of all posts"""
    print("Checking all posts status distribution...\n")

    status_counts = {}
    page = 1
    per_page = 50
    total_posts = 0

    while True:
        try:
            response = requests.get(
                f"{BASE}/posts?page={page}&limit={per_page}",
                headers=HEADERS,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and 'data' in data:
                posts = data['data']
            elif isinstance(data, dict) and 'posts' in data:
                posts = data['posts']
            elif isinstance(data, list):
                posts = data
            else:
                break

            if not posts:
                break

            for post in posts:
                status = post.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                total_posts += 1

            print(f"  Page {page}: scanned {len(posts)} posts")

            if len(posts) < per_page:
                break

            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            break

    print(f"\n{'='*70}")
    print(f"Total Posts Scanned: {total_posts}")
    print(f"{'='*70}")

    for status, count in sorted(status_counts.items()):
        pct = (count / total_posts * 100) if total_posts > 0 else 0
        print(f"  {status.upper():15} {count:4} posts ({pct:5.1f}%)")

def check_single_post(post_id):
    """Check a specific post's status"""
    try:
        response = requests.get(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            timeout=30
        )
        if response.status_code == 200:
            post = response.json()
            return post.get('status', 'unknown')
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    check_all_post_statuses()
