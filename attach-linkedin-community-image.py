"""
Upload linkedin-teaser.png to Zernio and update the scheduled post with it.
Post ID from schedule-newsletter-reactivation.py run: 6a373a16515828e9c4cc4b89
"""
import requests
import os
import json

from zernio_key import ZERNIO_API_KEY as API_KEY

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
POST_ID = "6a373a16515828e9c4cc4b89"
IMAGE_PATH = "/Users/toto/Claude TubeonAI/community-cards/output/linkedin-teaser.png"
LINKEDIN_ID = "690940455f6fbb9ef8323070"

# Step 1: presign
file_size = os.path.getsize(IMAGE_PATH)
presign = requests.post(f"{BASE}/media/presign", headers=HEADERS, json={
    "filename": "linkedin-teaser.png",
    "contentType": "image/png",
    "size": file_size,
})
presign.raise_for_status()
pdata = presign.json()
upload_url = pdata.get("uploadUrl") or pdata.get("data", {}).get("uploadUrl")
public_url = pdata.get("publicUrl") or pdata.get("data", {}).get("publicUrl")
print(f"Public URL: {public_url}")

# Step 2: upload
with open(IMAGE_PATH, "rb") as f:
    put = requests.put(upload_url, data=f, headers={"Content-Type": "image/png"})
    put.raise_for_status()
print("Image uploaded.")

# Step 3: fetch current post to get full body
get_resp = requests.get(f"{BASE}/posts/{POST_ID}", headers=HEADERS)
get_resp.raise_for_status()
post = get_resp.json().get("post", get_resp.json())

# Step 4: PUT full body with image attached
payload = {
    "content": post["content"],
    "scheduledFor": post["scheduledFor"],
    "timezone": post.get("timezone", "America/New_York"),
    "isDraft": False,
    "mediaItems": [{"url": public_url, "type": "image"}],
    "platforms": [
        {
            "platform": "linkedin",
            "accountId": LINKEDIN_ID,
            "scheduledFor": post["scheduledFor"],
        }
    ],
}

update = requests.put(f"{BASE}/posts/{POST_ID}", headers=HEADERS, json=payload)
print(f"Update status: {update.status_code}")
print(json.dumps(update.json(), indent=2)[:800])
