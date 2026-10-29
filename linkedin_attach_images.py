#!/usr/bin/env python3
"""
LinkedIn Image Attachment Script
Attaches uploaded images to scheduled posts
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load from .env
load_dotenv()

LINKEDIN_API_BASE = "https://api.linkedin.com/v2"

class LinkedInImageAttacher:
    """Attach uploaded images to LinkedIn posts"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def get_assets(self) -> dict:
        """Load assets from file"""
        try:
            with open("linkedin_assets.json") as f:
                assets = json.load(f)
            return {asset["filename"]: asset["asset_urn"] for asset in assets}
        except FileNotFoundError:
            print("❌ linkedin_assets.json not found")
            print("   Run: python linkedin_simple_uploader.py first")
            return None

    def create_post_with_image(self, text: str, asset_urn: str) -> bool:
        """Create a new post with image (alternative to updating scheduled posts)"""
        try:
            post_data = {
                "author": "urn:li:person:me",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "media": asset_urn
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            response = requests.post(
                f"{LINKEDIN_API_BASE}/ugcPosts",
                headers=self.headers,
                json=post_data
            )

            if response.status_code in [200, 201]:
                print(f"✅ Post created with image")
                return True
            else:
                print(f"❌ Failed to create post: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error creating post: {e}")
            return False

    def list_scheduled_posts(self) -> list:
        """List user's scheduled posts"""
        try:
            print("🔄 Fetching scheduled posts...")

            response = requests.get(
                f"{LINKEDIN_API_BASE}/ugcPosts",
                headers=self.headers,
                params={
                    "q": "authors",
                    "authors": ["urn:li:person:me"],
                    "count": 100
                }
            )

            if response.status_code == 200:
                posts = response.json().get("elements", [])
                return posts
            else:
                print(f"⚠️  Could not fetch posts: {response.status_code}")
                return []

        except Exception as e:
            print(f"⚠️  Error fetching posts: {e}")
            return []

    def run_manual_mode(self, assets: dict):
        """Manual mode - user provides post IDs and text"""
        print("\n" + "="*80)
        print("📋 Manual Attachment Mode")
        print("="*80)
        print("\nSince automatic post matching is complex, let's do it manually.")
        print("You'll provide post content and we'll attach images.\n")

        posts_data = [
            ("01-linkedin-post-problem.png", "Post 1: Problem - Jun 10"),
            ("02-linkedin-post-gap.png", "Post 2: Gap - Jun 13"),
            ("03-linkedin-post-math.png", "Post 3: Math - Jun 17"),
            ("04-linkedin-post-real-problem.png", "Post 4: Real Problem - Jun 20"),
            ("05-linkedin-post-case-study.png", "Post 5: Case Study - Jun 24"),
            ("06-linkedin-post-positioning.png", "Post 6: Positioning - Jun 27"),
            ("07-linkedin-post-ask.png", "Post 7: Ask - Jul 1"),
        ]

        created = 0
        for filename, description in posts_data:
            if filename not in assets:
                print(f"⏭️  Skipping {filename} (not found in assets)")
                continue

            asset_urn = assets[filename]

            print(f"\n📝 {description}")
            print(f"   Asset URN: {asset_urn}")
            print("\nEnter the post text (paste from your LINKEDIN_POSTS_READY_TO_SCHEDULE.md)")
            print("(Press Enter twice when done):\n")

            lines = []
            while True:
                line = input()
                if not line:
                    if lines and not lines[-1]:
                        break
                    lines.append("")
                else:
                    lines.append(line)

            post_text = "\n".join(lines[:-1]).strip()

            if not post_text:
                print("⏭️  Skipped (no text provided)")
                continue

            if self.create_post_with_image(post_text, asset_urn):
                created += 1

        print("\n" + "="*80)
        print(f"✅ Created {created}/7 posts with images")
        print("="*80)

    def run_auto_mode(self, assets: dict):
        """Automatic mode - try to fetch posts and attach images"""
        print("\n" + "="*80)
        print("🤖 Automatic Attachment Mode")
        print("="*80)

        posts = self.list_scheduled_posts()

        if not posts:
            print("\n⚠️  Could not fetch scheduled posts")
            print("Switching to manual mode...\n")
            return self.run_manual_mode(assets)

        print(f"✅ Found {len(posts)} posts")

        # Try to match images to posts
        print("\n📋 Matching images to posts...")
        print("Note: Matching by post order. Please verify:\n")

        image_files = sorted(list(assets.keys()))

        matches = {}
        for idx, (image_file, asset_urn) in enumerate(zip(image_files, posts)):
            post_id = posts[idx].get("id")
            matches[image_file] = {
                "post_id": post_id,
                "asset_urn": asset_urn
            }
            print(f"  {idx+1}. {image_file} → Post {idx+1}")

        print("\n⚠️  Are these matches correct? (yes/no)")
        if input().lower() != "yes":
            print("Switching to manual mode...\n")
            return self.run_manual_mode(assets)

        # Attach images to posts
        print("\n🚀 Attaching images to posts...\n")
        attached = 0
        for image_file, (post_id, asset_urn) in matches.items():
            try:
                update_data = {
                    "content": {
                        "media": [
                            {
                                "status": "READY",
                                "media": asset_urn,
                                "type": "IMAGE"
                            }
                        ]
                    }
                }

                response = requests.patch(
                    f"{LINKEDIN_API_BASE}/ugcPosts/{post_id}",
                    headers=self.headers,
                    json=update_data
                )

                if response.status_code in [200, 204]:
                    print(f"✅ {image_file} → Post attached")
                    attached += 1
                else:
                    print(f"❌ {image_file} → Failed: {response.status_code}")

            except Exception as e:
                print(f"❌ {image_file} → Error: {e}")

        print("\n" + "="*80)
        print(f"✅ Attached images to {attached}/7 posts")
        print("="*80)

    def run(self):
        """Main entry point"""
        print("\n" + "="*80)
        print("🔗 LinkedIn Image Attacher")
        print("="*80)

        assets = self.get_assets()
        if not assets:
            return False

        print(f"✅ Found {len(assets)} uploaded images")

        # Try automatic mode first
        self.run_auto_mode(assets)

        return True


if __name__ == "__main__":
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

    if not access_token:
        print("❌ No access token found")
        exit(1)

    attacher = LinkedInImageAttacher(access_token)
    success = attacher.run()

    exit(0 if success else 1)
