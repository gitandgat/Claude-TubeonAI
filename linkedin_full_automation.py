#!/usr/bin/env python3
"""
LinkedIn Full Automation
ONE COMMAND: reads posts from markdown, uploads images with correct owner,
creates posts. Fully self-contained — no separate upload step needed.
"""

import os
import json
import requests
import re
import time
from pathlib import Path
from dotenv import load_dotenv

# Load from .env
load_dotenv()

LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
IMAGES_DIR = Path.home() / "Downloads" / "Agency LinkedIn Post Pictures"


class LinkedInFullAutomation:
    """Complete automation: image upload + post creation with one owner URN"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.author_urn = self._fetch_author_urn()

    def _fetch_author_urn(self):
        """Get member ID via /userinfo (OpenID) with /me fallback"""
        print("🔍 Fetching member ID via /userinfo...")
        try:
            resp = requests.get("https://api.linkedin.com/v2/userinfo", headers=self.headers)
            if resp.status_code == 200:
                member_id = resp.json().get("sub")
                if member_id:
                    urn = f"urn:li:person:{member_id}"
                    print(f"✅ Author URN: {urn}")
                    return urn

            print(f"   /userinfo failed ({resp.status_code}), trying /me...")
            resp = requests.get(f"{LINKEDIN_API_BASE}/me", headers=self.headers)
            resp.raise_for_status()
            urn = f"urn:li:person:{resp.json()['id']}"
            print(f"✅ Author URN: {urn}")
            return urn
        except Exception as e:
            print(f"❌ Could not fetch member ID: {e}")
            return None

    def extract_posts_from_markdown(self) -> dict:
        """Extract all 7 posts from markdown file"""
        markdown_file = Path("LINKEDIN_POSTS_READY_TO_SCHEDULE.md")

        if not markdown_file.exists():
            print(f"❌ {markdown_file} not found")
            return None

        with open(markdown_file) as f:
            content = f.read()

        posts = {}
        blocks = re.split(r'```', content)
        post_num = 1
        for i, block in enumerate(blocks):
            if i % 2 == 1:  # Odd indices are code blocks
                if post_num <= 7:
                    posts[f"post_{post_num}"] = block.strip()
                    post_num += 1

        return posts if posts else None

    def find_image(self, post_num: int) -> Path:
        """Find image file for a post number (e.g. 01-linkedin-post-*.png)"""
        matches = list(IMAGES_DIR.glob(f"{post_num:02d}-linkedin-post-*.png"))
        return matches[0] if matches else None

    def upload_image(self, image_path: Path) -> str:
        """Upload image with the CORRECT owner URN. Returns asset URN."""
        try:
            register_response = requests.post(
                f"{LINKEDIN_API_BASE}/assets?action=registerUpload",
                headers=self.headers,
                json={
                    "registerUploadRequest": {
                        "owner": self.author_urn,
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

            if register_response.status_code != 200:
                print(f"   ❌ registerUpload failed: {register_response.text[:200]}")
                return None

            value = register_response.json()["value"]
            upload_mechanism = value["uploadMechanism"]
            # Handle both response shapes LinkedIn returns
            request_key = next(iter(upload_mechanism))
            upload_url = upload_mechanism[request_key]["uploadUrl"]
            asset_urn = value["asset"]

            with open(image_path, "rb") as f:
                upload_response = requests.put(
                    upload_url,
                    data=f.read(),
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "image/png"
                    }
                )

            if upload_response.status_code not in [200, 201]:
                print(f"   ❌ Image PUT failed: {upload_response.status_code}")
                return None

            return asset_urn

        except Exception as e:
            print(f"   ❌ Upload error: {e}")
            return None

    def create_post_with_image(self, text: str, asset_urn: str) -> str:
        """Create a post with image. Returns the ugcPost URN (needed to comment) or ''."""
        try:
            post_data = {
                "author": self.author_urn,
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
                # LinkedIn returns the post URN in the X-RestLi-Id header (and 'id' body)
                post_urn = response.headers.get("X-RestLi-Id") or response.json().get("id", "")
                return post_urn
            else:
                print(f"   ❌ Post failed ({response.status_code}): {response.text[:200]}")
                return ""

        except Exception as e:
            print(f"   ❌ Error creating post: {e}")
            return ""

    def add_comment(self, post_urn: str, text: str) -> bool:
        """Add a first comment (e.g. the resource link) to one of our own posts.

        Uses the socialActions API. Comment author must equal the post author;
        works with the same w_member_social scope used for publishing.
        """
        if not post_urn:
            return False
        try:
            import urllib.parse
            encoded = urllib.parse.quote(post_urn, safe="")
            payload = {
                "actor": self.author_urn,
                "message": {"text": text},
            }
            resp = requests.post(
                f"{LINKEDIN_API_BASE}/socialActions/{encoded}/comments",
                headers=self.headers,
                json=payload,
            )
            if resp.status_code in (200, 201):
                print("   ✓ First comment added")
                return True
            print(f"   ⚠ Comment failed ({resp.status_code}): {resp.text[:160]}")
            return False
        except Exception as e:
            print(f"   ⚠ Comment error: {e}")
            return False

    def run(self, only_posts: list = None):
        """Execute full automation: upload + post for each entry.

        Args:
            only_posts: optional list of post numbers to publish (e.g. [1, 3]).
                        Default: all 7.
        """
        print("\n" + "="*80)
        print("🚀 LinkedIn Full Automation (upload + post)")
        print("="*80)

        if not self.author_urn:
            print("❌ No author URN — re-run: python linkedin_oauth.py")
            return False

        # Extract posts
        print("\n📖 Reading posts from markdown...")
        posts = self.extract_posts_from_markdown()
        if not posts:
            print("❌ Could not extract posts")
            return False
        print(f"✅ Found {len(posts)} posts")

        targets = only_posts or list(range(1, 8))

        # Upload + post, one by one
        print("\n🚀 Publishing...\n")
        created = 0
        for post_num in targets:
            post_key = f"post_{post_num}"
            print(f"📤 Post {post_num}:", end=" ")

            if post_key not in posts:
                print("⏭️  no text found, skipped")
                continue

            image_path = self.find_image(post_num)
            if not image_path:
                print("⏭️  no image found, skipped")
                continue

            # Step 1: upload image with correct owner
            asset_urn = self.upload_image(image_path)
            if not asset_urn:
                print("❌ image upload failed")
                continue

            # Step 2: create the post
            if self.create_post_with_image(posts[post_key], asset_urn):
                print(f"✅ published ({image_path.name})")
                created += 1

            # Gentle rate limiting between posts
            if post_num != targets[-1]:
                time.sleep(2)

        # Summary
        print("\n" + "="*80)
        if created == len(targets):
            print(f"✅ SUCCESS! All {created} posts published with images!")
            print("   Check your profile: https://www.linkedin.com/in/sahawat-crosswalkwisdom/")
        else:
            print(f"⚠️  Published {created}/{len(targets)} posts")
        print("="*80)

        return created == len(targets)


if __name__ == "__main__":
    import sys

    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

    if not access_token:
        print("❌ No access token found in .env")
        exit(1)

    # Optional: pass post numbers as args, e.g. python linkedin_full_automation.py 1 2
    only = [int(a) for a in sys.argv[1:] if a.isdigit()] or None

    automation = LinkedInFullAutomation(access_token)
    success = automation.run(only_posts=only)

    exit(0 if success else 1)
