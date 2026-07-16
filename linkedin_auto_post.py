#!/usr/bin/env python3
"""
LinkedIn Auto-Poster
Automatically posts all 7 posts with images using the wrapper service
"""

import os
import re
import getpass
from pathlib import Path
from linkedin_wrapper_service import LinkedInWrapperService


def extract_posts_from_markdown() -> dict:
    """Extract all 7 posts from markdown file"""
    markdown_file = Path("LINKEDIN_POSTS_READY_TO_SCHEDULE.md")

    if not markdown_file.exists():
        print(f"❌ {markdown_file} not found")
        return None

    with open(markdown_file) as f:
        content = f.read()

    posts = {}

    # Extract each post from code blocks
    blocks = re.split(r'```', content)
    post_num = 1
    for i, block in enumerate(blocks):
        if i % 2 == 1:  # Odd indices are code blocks
            if post_num <= 7:
                posts[f"post_{post_num}"] = block.strip()
                post_num += 1

    return posts if posts else None


def get_image_path(post_num: int) -> str:
    """Get image path for post number"""
    images_dir = Path.home() / "Downloads" / "Agency LinkedIn Post Pictures"
    image_file = f"{post_num:02d}-linkedin-post-*.png"

    # Find the image file
    for img in images_dir.glob(image_file):
        return str(img)

    return None


def main():
    """Main automation flow"""
    print("\n" + "="*80)
    print("🚀 LinkedIn Auto-Poster")
    print("="*80)

    # Get credentials
    print("\n🔐 LinkedIn Credentials (for automated posting)")
    email = input("📧 Enter your LinkedIn email: ")
    password = getpass.getpass("🔐 Enter your LinkedIn password (hidden): ")

    # Initialize service
    print("\n🌐 Starting LinkedIn wrapper service...")
    service = LinkedInWrapperService(headless=False)

    # Login
    if not service.login(email, password):
        print("❌ Login failed")
        return False

    # Extract posts
    print("\n📖 Reading posts from markdown...")
    posts = extract_posts_from_markdown()

    if not posts:
        print("❌ Could not extract posts")
        service.close()
        return False

    print(f"✅ Found {len(posts)} posts")

    # Prepare posts with images
    print("\n📸 Preparing posts with images...")
    posts_with_images = []

    for post_num in range(1, 8):
        post_key = f"post_{post_num}"

        if post_key not in posts:
            print(f"⏭️  Post {post_num}: Not found")
            continue

        image_path = get_image_path(post_num)
        if not image_path:
            print(f"⏭️  Post {post_num}: Image not found")
            continue

        posts_with_images.append({
            "text": posts[post_key],
            "image": image_path,
            "number": post_num
        })

        print(f"✅ Post {post_num}: Ready")

    if not posts_with_images:
        print("❌ No posts ready to post")
        service.close()
        return False

    # Confirm before posting
    print(f"\n⚠️  About to post {len(posts_with_images)} posts to LinkedIn")
    print("   This will post them immediately (not scheduled)")
    confirm = input("   Continue? (yes/no): ")

    if confirm.lower() != "yes":
        print("Cancelled")
        service.close()
        return False

    # Post all
    print("\n🚀 Posting to LinkedIn...\n")

    results = {
        "success": 0,
        "failed": 0
    }

    for idx, post_data in enumerate(posts_with_images, 1):
        print(f"[{idx}/{len(posts_with_images)}] Posting...", end=" ")

        if service.post_with_image(post_data["text"], post_data["image"]):
            results["success"] += 1
            print("✅")
        else:
            results["failed"] += 1
            print("❌")

    # Summary
    print("\n" + "="*80)
    print(f"✅ Complete! {results['success']}/{len(posts_with_images)} posted successfully")
    print("="*80)

    # Close
    service.close()

    return results["success"] == len(posts_with_images)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
