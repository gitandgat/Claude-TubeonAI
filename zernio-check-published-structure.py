#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE = "https://zernio.com/api/v1"
API_KEY = os.getenv('ZERNIO_API_KEY')
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

response = requests.get(
    f"{BASE}/posts?limit=50",
    headers=HEADERS,
    timeout=30
)

data = response.json()
posts = data.get('posts', [])

# Find first published post with complete data
found = False
for post in posts:
    if post.get('status') == 'published' and post.get('content'):
        print("Sample PUBLISHED post structure:")
        print(f"ID: {post.get('id')}")
        print(f"Title: {post.get('title')[:50] if post.get('title') else 'N/A'}")
        print(f"Content length: {len(post.get('content', ''))}")
        print(f"Has mediaItems: {bool(post.get('mediaItems'))}")
        print(f"Platforms configured: {len(post.get('platforms', []))}")
        print(f"\nPost structure keys: {sorted(post.keys())}")
        found = True
        break

if not found:
    print("No published posts with full content found")
