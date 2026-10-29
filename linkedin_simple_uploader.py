#!/usr/bin/env python3
"""
Simplified LinkedIn Image Uploader
Uploads images directly without needing to fetch posts
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load from .env
load_dotenv()

LINKEDIN_API_BASE = "https://api.linkedin.com/v2"

class SimplifiedLinkedInUploader:
    """Upload images to LinkedIn without fetching posts"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.images_dir = Path.home() / "Downloads" / "Agency LinkedIn Post Pictures"

    def upload_image(self, image_path: Path) -> dict:
        """Upload image and return asset info"""
        try:
            # Register upload
            print(f"\n📤 Uploading: {image_path.name}")

            register_response = requests.post(
                f"{LINKEDIN_API_BASE}/assets?action=registerUpload",
                headers=self.headers,
                json={
                    "registerUploadRequest": {
                        "owner": "urn:li:person:me",
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
                print(f"❌ Upload failed: {register_response.text}")
                return None

            response_data = register_response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")

            try:
                upload_url = response_data["value"]["uploadMechanism"][
                    "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
                ]["uploadUrl"]
                asset_urn = response_data["value"]["asset"]
            except KeyError as e:
                print(f"❌ Unexpected response format: {e}")
                return None

            # Upload image file
            with open(image_path, "rb") as f:
                upload_response = requests.put(
                    upload_url,
                    data=f.read(),
                    headers={"Content-Type": "image/png"}
                )

                if upload_response.status_code not in [200, 201]:
                    print(f"❌ Image upload failed: {upload_response.text}")
                    return None

            print(f"✅ Uploaded successfully!")
            return {
                "filename": image_path.name,
                "asset_urn": asset_urn,
                "upload_url": upload_url
            }

        except Exception as e:
            print(f"❌ Error uploading {image_path.name}: {e}")
            return None

    def test_connection(self) -> bool:
        """Test if access token is valid"""
        try:
            print("🔐 Testing access token...")
            response = requests.get(
                f"{LINKEDIN_API_BASE}/me",
                headers=self.headers
            )

            if response.status_code == 200:
                print("✅ Access token is valid!")
                return True
            elif response.status_code == 401:
                print("❌ Access token is invalid or expired")
                return False
            elif response.status_code == 403:
                print("⚠️  Access token is valid but missing permissions")
                print("   Proceeding with image uploads anyway...")
                return True
            else:
                print(f"⚠️  Unexpected response: {response.status_code}")
                return True

        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

    def run(self):
        """Execute image uploads"""
        print("\n" + "="*80)
        print("🔗 LinkedIn Image Uploader (Simplified)")
        print("="*80)

        # Test connection
        if not self.test_connection():
            return False

        # Find images
        if not self.images_dir.exists():
            print(f"❌ Images directory not found: {self.images_dir}")
            return False

        image_files = sorted([
            f for f in os.listdir(self.images_dir)
            if f.endswith(".png")
        ])

        print(f"\n📸 Found {len(image_files)} images")

        if not image_files:
            print("❌ No images found")
            return False

        # Upload all images
        print("\n🚀 Uploading images...\n")

        uploaded = []
        for image_file in image_files:
            image_path = self.images_dir / image_file
            result = self.upload_image(image_path)
            if result:
                uploaded.append(result)

        # Summary
        print("\n" + "="*80)
        print(f"✅ Uploaded {len(uploaded)}/{len(image_files)} images")
        print("="*80)

        # Save asset info
        if uploaded:
            with open("linkedin_assets.json", "w") as f:
                json.dump(uploaded, f, indent=2)
            print(f"\n📋 Asset info saved to: linkedin_assets.json")
            print("   (Use these asset URNs in your LinkedIn posts)")

        return len(uploaded) == len(image_files)


if __name__ == "__main__":
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

    if not access_token:
        print("❌ No access token found in environment")
        print("Make sure LINKEDIN_ACCESS_TOKEN is set in your .env file")
        exit(1)

    uploader = SimplifiedLinkedInUploader(access_token)
    success = uploader.run()

    exit(0 if success else 1)
