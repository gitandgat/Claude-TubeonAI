#!/usr/bin/env python3
"""
Update all 106 posts to cross-post to all 5 platforms (LinkedIn, Instagram, Facebook, TikTok, YouTube)
with proper content and carousel images for TikTok
"""

import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY environment variable not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

DRAFTS_DIR = "drafts/blog-social"
PLATFORM_ACCOUNT_IDS = {
    "linkedin": "690940455f6fbb9ef8323070",
    "instagram": "690940655f6fbb9ef8323072",
    "facebook": "6909409a5f6fbb9ef8323074",
    "tiktok": "690941425f6fbb9ef8323078",
    "youtube": "690940d35f6fbb9ef8323077"
}

def upload_image_to_zernio(image_path):
    """Upload carousel image to Zernio CDN"""
    if not os.path.exists(image_path):
        return None

    try:
        filename = os.path.basename(image_path)
        filesize = os.path.getsize(image_path)

        # Presign upload
        presign_response = requests.post(
            f"{BASE}/media/presign",
            headers=HEADERS,
            json={"filename": filename, "contentType": "image/png", "fileSize": filesize},
            timeout=30
        )
        presign_response.raise_for_status()
        data = presign_response.json()
        upload_url = data["uploadUrl"]
        public_url = data["publicUrl"]

        # Upload to CDN
        with open(image_path, "rb") as f:
            put_response = requests.put(upload_url, data=f, headers={"Content-Type": "image/png"}, timeout=30)
            put_response.raise_for_status()

        return public_url
    except Exception as e:
        print(f"    Error uploading {image_path}: {str(e)}")
        return None

def get_all_content():
    """Read all content from drafts/blog-social/"""
    content_map = {}
    drafts_path = Path(DRAFTS_DIR)

    for content_dir in sorted(drafts_path.iterdir()):
        if not content_dir.is_dir():
            continue

        slug = content_dir.name
        content_map[slug] = {}

        # Read platform-specific content
        for platform_file in ['linkedin.md', 'instagram.md', 'facebook.md', 'tiktok-reels.md']:
            file_path = content_dir / platform_file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    platform = platform_file.replace('.md', '').replace('-reels', '')
                    content_map[slug][platform] = f.read().strip()

        # Check for carousel image
        carousel_path = content_dir / "carousel" / "slide-01.png"
        if carousel_path.exists():
            content_map[slug]['image_path'] = str(carousel_path)

    return content_map

def get_scheduled_posts():
    """Fetch all scheduled posts"""
    all_scheduled = []
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
            scheduled = [p for p in posts if p.get('status') == 'scheduled']
            all_scheduled.extend(scheduled)

            if len(posts) < per_page:
                break

            page += 1

        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    return all_scheduled

def update_post_crosspost(post_id, content_data, image_urls):
    """Update post with cross-platform content"""
    try:
        # Fetch current post
        get_response = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS, timeout=30)
        get_response.raise_for_status()
        post_data = get_response.json()

        # Prepare media items
        media_items = []
        if 'tiktok' in image_urls and image_urls['tiktok']:
            media_items.append({"url": image_urls['tiktok'], "type": "image"})

        # Prepare platforms with all 5 options
        platforms = []

        # LinkedIn
        if 'linkedin' in content_data:
            platforms.append({
                "platform": "linkedin",
                "accountId": PLATFORM_ACCOUNT_IDS["linkedin"],
                "customContent": content_data['linkedin'],
                "scheduledFor": post_data.get('scheduledFor')
            })

        # Instagram
        if 'instagram' in content_data:
            platforms.append({
                "platform": "instagram",
                "accountId": PLATFORM_ACCOUNT_IDS["instagram"],
                "customContent": content_data['instagram'],
                "scheduledFor": post_data.get('scheduledFor')
            })

        # Facebook
        if 'facebook' in content_data:
            platforms.append({
                "platform": "facebook",
                "accountId": PLATFORM_ACCOUNT_IDS["facebook"],
                "customContent": content_data['facebook'],
                "scheduledFor": post_data.get('scheduledFor')
            })

        # TikTok
        if 'tiktok' in content_data:
            platforms.append({
                "platform": "tiktok",
                "accountId": PLATFORM_ACCOUNT_IDS["tiktok"],
                "customContent": content_data['tiktok'],
                "scheduledFor": post_data.get('scheduledFor')
            })

        # YouTube
        if 'linkedin' in content_data:  # Use LinkedIn content for YouTube
            platforms.append({
                "platform": "youtube",
                "accountId": PLATFORM_ACCOUNT_IDS["youtube"],
                "customContent": content_data['linkedin'],
                "title": "Crosswalk Wisdom",
                "scheduledFor": post_data.get('scheduledFor')
            })

        # Update post
        post_data['content'] = content_data.get('linkedin', '')
        post_data['isDraft'] = False
        post_data['platforms'] = platforms
        if media_items:
            post_data['mediaItems'] = media_items

        # PUT back
        put_response = requests.put(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=post_data,
            timeout=30
        )

        if put_response.status_code in (200, 201):
            return True
        else:
            return False

    except Exception as e:
        return False

def main():
    print("=" * 70)
    print("Cross-Post All 106 Posts to 5 Platforms")
    print("=" * 70)

    # Load content
    print("\nLoading content from drafts...")
    content_map = get_all_content()
    print(f"✓ Loaded {len(content_map)} content pieces\n")

    # Get scheduled posts
    print("Fetching scheduled posts...")
    scheduled_posts = get_scheduled_posts()
    print(f"✓ Found {len(scheduled_posts)} scheduled posts\n")

    # Upload images
    print("Uploading carousel images...")
    image_upload_cache = {}
    for slug, content in content_map.items():
        if 'image_path' in content:
            image_url = upload_image_to_zernio(content['image_path'])
            if image_url:
                image_upload_cache[slug] = image_url

    print(f"✓ Uploaded {len(image_upload_cache)} images\n")

    # Update posts with cross-posting
    print("Updating posts with cross-platform configuration...\n")

    successful = 0
    failed = 0
    content_idx = 0

    for idx, post in enumerate(scheduled_posts):
        post_id = post.get('id') or post.get('_id')

        # Cycle through content pieces
        slugs = list(content_map.keys())
        slug = slugs[idx % len(slugs)]
        content_data = content_map[slug]

        # Get image URL for this content
        image_urls = {'tiktok': image_upload_cache.get(slug)}

        # Update post
        if update_post_crosspost(post_id, content_data, image_urls):
            successful += 1
        else:
            failed += 1

        if (idx + 1) % 10 == 0:
            print(f"  {idx + 1}/{len(scheduled_posts)} posts updated ({successful} OK, {failed} failed)")

        time.sleep(0.3)

    # Summary
    print("\n" + "=" * 70)
    print("Results")
    print("=" * 70)
    print(f"✓ Cross-posted: {successful}/{len(scheduled_posts)}")
    print(f"✗ Failed: {failed}/{len(scheduled_posts)}")

    if successful == len(scheduled_posts):
        print("\n✓ All 106 posts successfully configured for cross-posting to 5 platforms!")
    else:
        print(f"\n⚠️  {failed} posts failed to update")

if __name__ == '__main__':
    main()
