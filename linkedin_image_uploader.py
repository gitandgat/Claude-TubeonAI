#!/usr/bin/env python3
"""
LinkedIn Image Uploader - Automate adding images to scheduled posts
Attaches images to LinkedIn posts by updating scheduled content
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple
import time
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Configuration
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
POSTS_MAPPING = {
    "01-linkedin-post-problem.png": {
        "post_id": None,  # Will be populated
        "post_name": "Post 1: Problem",
        "date": "2026-06-10"
    },
    "02-linkedin-post-gap.png": {
        "post_id": None,
        "post_name": "Post 2: Gap",
        "date": "2026-06-13"
    },
    "03-linkedin-post-math.png": {
        "post_id": None,
        "post_name": "Post 3: Math",
        "date": "2026-06-17"
    },
    "04-linkedin-post-real-problem.png": {
        "post_id": None,
        "post_name": "Post 4: Real Problem",
        "date": "2026-06-20"
    },
    "05-linkedin-post-case-study.png": {
        "post_id": None,
        "post_name": "Post 5: Case Study",
        "date": "2026-06-24"
    },
    "06-linkedin-post-positioning.png": {
        "post_id": None,
        "post_name": "Post 6: Positioning",
        "date": "2026-06-27"
    },
    "07-linkedin-post-ask.png": {
        "post_id": None,
        "post_name": "Post 7: Ask",
        "date": "2026-07-01"
    }
}


class LinkedInImageUploader:
    """Upload images to LinkedIn scheduled posts"""

    def __init__(self, access_token: str):
        """
        Initialize with LinkedIn access token

        Args:
            access_token: LinkedIn API access token
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.images_dir = Path.home() / "Downloads" / "Agency LinkedIn Post Pictures"

    def get_user_id(self) -> str:
        """Get authenticated user's LinkedIn ID"""
        try:
            response = requests.get(
                f"{LINKEDIN_API_BASE}/me",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()["id"]
        except Exception as e:
            print(f"❌ Error getting user ID: {e}")
            return None

    def get_scheduled_posts(self) -> List[Dict]:
        """Get list of user's scheduled posts"""
        try:
            user_id = self.get_user_id()
            if not user_id:
                return []

            # Get user's posts (including scheduled)
            response = requests.get(
                f"{LINKEDIN_API_BASE}/ugcPosts",
                headers=self.headers,
                params={
                    "q": "authors",
                    "authors": [f"urn:li:person:{user_id}"],
                    "start": 0,
                    "count": 100
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("elements", [])
        except Exception as e:
            print(f"❌ Error getting posts: {e}")
            return []

    def upload_image(self, image_path: Path) -> str:
        """
        Upload image to LinkedIn and get asset URN

        Args:
            image_path: Path to image file

        Returns:
            Asset URN for use in post
        """
        try:
            user_id = self.get_user_id()
            if not user_id:
                return None

            # Register upload
            register_response = requests.post(
                f"{LINKEDIN_API_BASE}/assets?action=registerUpload",
                headers=self.headers,
                json={
                    "registerUploadRequest": {
                        "owner": f"urn:li:person:{user_id}",
                        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                        "serviceRelationships": [
                            {
                                "relationshipType": "OWNER",
                                "identifier": "urn:li:userGeneratedContent"
                            }
                        ]
                    }
                }
            )
            register_response.raise_for_status()
            upload_url = register_response.json()["value"]["uploadMechanism"][
                "com.linkedin.digitalmedia.uploading.AssetUploadHttpRequest"
            ]["uploadUrl"]
            asset_urn = register_response.json()["value"]["asset"]

            # Upload image file
            with open(image_path, "rb") as f:
                upload_response = requests.put(
                    upload_url,
                    data=f.read(),
                    headers={"Content-Type": "image/png"}
                )
                upload_response.raise_for_status()

            print(f"✅ Uploaded: {image_path.name}")
            return asset_urn
        except Exception as e:
            print(f"❌ Error uploading {image_path.name}: {e}")
            return None

    def update_post_with_image(self, post_id: str, asset_urn: str) -> bool:
        """
        Update a post to include the image

        Args:
            post_id: LinkedIn post ID
            asset_urn: Asset URN from image upload

        Returns:
            True if successful
        """
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
            response.raise_for_status()
            print(f"✅ Updated post with image")
            return True
        except Exception as e:
            print(f"❌ Error updating post: {e}")
            return False

    def match_images_to_posts(self, scheduled_posts: List[Dict]) -> Dict:
        """
        Match downloaded images to scheduled posts by date

        Args:
            scheduled_posts: List of user's posts from API

        Returns:
            Dictionary mapping image filenames to post IDs
        """
        matches = {}

        # This is a simplified matching - in production, you'd match by creation time or text content
        # For now, we'll assume posts were created in order
        print("\n📋 Matching images to posts...")
        print("Note: Matching by post order. Verify these are correct:")

        post_dates = {}
        for post in scheduled_posts:
            try:
                # Extract post creation time if available
                created_time = post.get("created", {}).get("time")
                post_id = post.get("id")
                if post_id:
                    post_dates[post_id] = created_time
            except:
                pass

        # Simple order-based matching
        image_files = sorted([
            f for f in os.listdir(self.images_dir)
            if f.endswith(".png")
        ])

        for idx, image_file in enumerate(image_files):
            if idx < len(scheduled_posts):
                post_id = scheduled_posts[idx].get("id")
                matches[image_file] = post_id
                post_name = POSTS_MAPPING.get(image_file, {}).get("post_name", f"Post {idx+1}")
                print(f"  {idx+1}. {image_file} → {post_name}")

        return matches

    def run(self):
        """Execute the image upload process"""
        print("\n" + "="*80)
        print("🔗 LinkedIn Image Uploader")
        print("="*80)

        # Verify images exist
        if not self.images_dir.exists():
            print(f"❌ Images directory not found: {self.images_dir}")
            return False

        image_files = [f for f in os.listdir(self.images_dir) if f.endswith(".png")]
        print(f"\n📸 Found {len(image_files)} images in {self.images_dir}")

        # Get scheduled posts
        print("\n🔄 Fetching your scheduled posts from LinkedIn...")
        scheduled_posts = self.get_scheduled_posts()

        if not scheduled_posts:
            print("❌ No posts found. Make sure:")
            print("   • Your LinkedIn access token is valid")
            print("   • You have scheduled posts on LinkedIn")
            return False

        print(f"✅ Found {len(scheduled_posts)} posts")

        # Match images to posts
        matches = self.match_images_to_posts(scheduled_posts)

        if not matches:
            print("❌ Could not match images to posts")
            return False

        # Confirm before proceeding
        print("\n⚠️  Review the matches above. Are they correct? (yes/no)")
        if input().lower() != "yes":
            print("Cancelled.")
            return False

        # Upload images and attach to posts
        print("\n🚀 Uploading images and updating posts...\n")

        success_count = 0
        for image_file, post_id in matches.items():
            if post_id is None:
                print(f"⏭️  Skipping {image_file} (no matching post)")
                continue

            image_path = self.images_dir / image_file
            if not image_path.exists():
                print(f"❌ Image not found: {image_file}")
                continue

            # Upload image
            asset_urn = self.upload_image(image_path)
            if not asset_urn:
                continue

            # Attach to post
            if self.update_post_with_image(post_id, asset_urn):
                success_count += 1

            # Rate limit
            time.sleep(1)

        print("\n" + "="*80)
        print(f"✅ Complete! Updated {success_count}/{len(matches)} posts with images")
        print("="*80 + "\n")
        return success_count == len(matches)


def get_access_token() -> str:
    """Get LinkedIn access token from environment or user input"""

    # Try environment variable first
    if os.getenv("LINKEDIN_ACCESS_TOKEN"):
        return os.getenv("LINKEDIN_ACCESS_TOKEN")

    # Try config file
    config_file = Path.home() / ".linkedin" / "config.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
                return config.get("access_token")
        except:
            pass

    # Ask user
    print("\n🔐 LinkedIn Access Token Required")
    print("Get your token at: https://www.linkedin.com/developers/apps")
    print("(or run: python linkedin_oauth.py to get one)\n")
    token = input("Paste your LinkedIn access token: ").strip()

    return token


if __name__ == "__main__":
    print("\n")
    access_token = get_access_token()

    if not access_token:
        print("❌ No access token provided")
        exit(1)

    uploader = LinkedInImageUploader(access_token)
    success = uploader.run()

    exit(0 if success else 1)
