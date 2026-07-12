#!/usr/bin/env python3
"""
Alternative approach: Try different methods to change draft → scheduled
1. Check if there's a /posts/{id}/publish endpoint
2. Try PATCH instead of PUT
3. Try full body update with more fields
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

def get_draft_posts_sample():
    """Get first draft post to examine its structure"""
    # Try fetching all posts and find a draft one
    response = requests.get(
        f"{BASE}/posts?limit=100",
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()

    print(f"  Raw response type: {type(data)}")

    if isinstance(data, dict):
        if 'data' in data:
            posts = data['data']
            print(f"  Found 'data' key with {len(posts)} posts")
        elif 'posts' in data:
            posts = data['posts']
            print(f"  Found 'posts' key with {len(posts)} posts")
        else:
            print(f"  Dict keys: {list(data.keys())}")
            return None
    elif isinstance(data, list):
        posts = data
        print(f"  Got list with {len(posts)} posts")
    else:
        print(f"  Unexpected type: {type(data)}")
        return None

    # Find first draft post
    draft_count = 0
    for post in posts:
        if post.get('status') == 'draft':
            draft_count += 1
            if draft_count == 1:
                print(f"  Found draft post: {post.get('id')}")
                return post

    print(f"  Found {draft_count} draft posts in this batch")
    return None

def try_publish_endpoint(post_id):
    """Try /posts/{id}/publish endpoint"""
    try:
        response = requests.post(
            f"{BASE}/posts/{post_id}/publish",
            headers=HEADERS,
            json={},
            timeout=30
        )
        return response.status_code, response.text[:200]
    except Exception as e:
        return None, str(e)

def try_patch_request(post_id, post_data):
    """Try PATCH instead of PUT"""
    try:
        update_body = {
            "status": "scheduled",
            "publishStatus": "scheduled"  # Try alternative field name
        }
        response = requests.patch(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=update_body,
            timeout=30
        )
        return response.status_code, response.text[:200]
    except Exception as e:
        return None, str(e)

def try_full_body_update(post_id, post_data):
    """Try updating with complete post body"""
    try:
        update_body = post_data.copy()
        update_body['status'] = 'scheduled'

        response = requests.put(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=update_body,
            timeout=30
        )
        return response.status_code, response.text[:200]
    except Exception as e:
        return None, str(e)

def main():
    print("=" * 70)
    print("Exploring Zernio API for Status Change Options")
    print("=" * 70)

    # Get a sample draft post
    print("\nFetching sample draft post...")
    sample_post = get_draft_posts_sample()

    if not sample_post:
        print("❌ Could not fetch sample draft post")
        return

    post_id = sample_post.get('id') or sample_post.get('_id')
    print(f"✓ Got sample post: {post_id}")
    print(f"  Current status: {sample_post.get('status')}")
    print(f"  Has fields: {list(sample_post.keys())}")

    print("\n" + "=" * 70)
    print("Testing Different Update Methods")
    print("=" * 70)

    # Test 1: Try /publish endpoint
    print("\n1. Testing POST /posts/{id}/publish endpoint...")
    status, text = try_publish_endpoint(post_id)
    print(f"   Response: {status}")
    if text and status not in (200, 201):
        print(f"   Body: {text}")

    time.sleep(1)

    # Test 2: Try PATCH
    print("\n2. Testing PATCH /posts/{id}...")
    status, text = try_patch_request(post_id, sample_post)
    print(f"   Response: {status}")
    if text and status not in (200, 201):
        print(f"   Body: {text}")

    time.sleep(1)

    # Test 3: Try full body PUT
    print("\n3. Testing PUT /posts/{id} with full body...")
    status, text = try_full_body_update(post_id, sample_post)
    print(f"   Response: {status}")
    if text and status not in (200, 201):
        print(f"   Body: {text}")

    print("\n" + "=" * 70)
    print("Checking if any method worked...")
    print("=" * 70)

    # Verify current status
    time.sleep(2)
    response = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS, timeout=30)
    current_post = response.json()
    current_status = current_post.get('status')

    print(f"\nSample post current status: {current_status}")
    if current_status == 'scheduled':
        print("✓ STATUS CHANGE WORKED! We can now fix all 106 posts.")
    else:
        print("✗ STATUS CHANGE DIDN'T WORK via API")
        print("\nRecommendation: Use manual dashboard fix")
        print("  1. Go to Zernio Dashboard")
        print("  2. Filter by Status: Draft")
        print("  3. Select all 106 posts")
        print("  4. Bulk action → Change Status to Scheduled")

if __name__ == '__main__':
    main()
