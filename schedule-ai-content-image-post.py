"""
Schedule AI content system image post — April 7, 2026 at 9am ET (13:00 UTC)
4 platforms: LinkedIn, Instagram, Facebook, TikTok
Image: /Users/toto/crosswalk-wisdom-new/public/sleek-laptop.jpg
"""
import os, requests

BASE    = "https://zernio.com/api/v1"
API_KEY = "***REMOVED-ZERNIO-KEY***"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"

IMAGE_PATH = "/Users/toto/crosswalk-wisdom-new/public/sleek-laptop.jpeg"
SCHEDULED_AT = "2026-04-07T13:00:00.000Z"  # 9am ET

LINKEDIN_COPY = """Your AI content looks like everyone else's because your input looks like everyone else's.

Claude doesn't make carousels generic. You make them generic.

The fix isn't a better tool. It's a better system.

Here's how I do it:

First, I build a brand system doc — colors, voice, typography, tone. Claude references it every time, so everything stays consistent without me thinking about it.

Then I batch 20-30 custom images using Nana Banana. One session, a few weeks of assets. Claude reads the mood of each image and matches it to the right slide in the carousel — automatically.

Two prompts. A finished carousel that looks like nothing else in the feed.

The creator who builds the system on Sunday will always outperform the one asking AI to "make something cool."

Your AI is only as good as what you give it.

Build the system.

#ContentMarketing #AITools #SocialMediaMarketing #InstagramGrowth #ContentStrategy"""

INSTAGRAM_COPY = """Your AI content looks like everyone else's because your input looks like everyone else's.

Here's how I fixed it: brand system doc + 30 custom images + Claude. Two prompts. A carousel that's actually mine.

Build the system. Own the feed.

Link in bio for the full breakdown.

#ContentMarketing #AITools #InstagramCarousel #SocialMediaMarketing #ContentCreator #AIContentCreation #InstagramGrowth #ContentStrategy #CarouselPost #DigitalMarketing #ClaudeAI #CreatorTools"""

FACEBOOK_COPY = """Here's something nobody tells you about AI content tools:

The reason your posts look like everyone else's isn't the tool. It's that you're giving it the same generic input as everyone else.

Here's how I do it differently — I keep a brand system doc Claude references every time, and I batch custom images with Nana Banana so Claude can match the mood of each image to the right moment in the carousel.

Two prompts. Done. And it looks nothing like the Canva templates flooding your feed.

What's one thing you're doing right now to make your content stand out?"""

TIKTOK_COPY = """Your AI content is generic because your input is generic.

Here's how I do it: brand system doc, 30 custom images, Claude.

Two prompts. A carousel that's actually yours.

Build the system — not just the post.

#AITools #ContentCreator #InstagramTips #ClaudeAI #ContentMarketing"""

PLATFORM_COPY = {
    LINKEDIN_ID:  LINKEDIN_COPY,
    INSTAGRAM_ID: INSTAGRAM_COPY,
    FACEBOOK_ID:  FACEBOOK_COPY,
    TIKTOK_ID:    TIKTOK_COPY,
}


def upload_image(filepath):
    filename  = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    data = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "image/jpeg", "size": file_size},
    ).json()
    upload_url = data.get("uploadUrl") or data.get("data", {}).get("uploadUrl")
    public_url = data.get("publicUrl") or data.get("data", {}).get("publicUrl")
    with open(filepath, "rb") as f:
        requests.put(upload_url, data=f, headers={"Content-Type": "image/jpeg"}).raise_for_status()
    print(f"  Uploaded: {public_url}")
    return public_url


def schedule_all(media_url):
    payload = {
        "content": LINKEDIN_COPY,
        "scheduledFor": SCHEDULED_AT,
        "timezone": "America/New_York",
        "mediaItems": [{"url": media_url, "type": "image"}],
        "platforms": [
            {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": LINKEDIN_COPY,  "scheduledFor": SCHEDULED_AT},
            {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": INSTAGRAM_COPY, "scheduledFor": SCHEDULED_AT},
            {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": FACEBOOK_COPY,  "scheduledFor": SCHEDULED_AT},
            {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": TIKTOK_COPY,    "scheduledFor": SCHEDULED_AT},
        ],
    }
    resp = requests.post(f"{BASE}/posts", headers=HEADERS, json=payload)
    print(f"  Status: {resp.status_code} {'OK' if resp.status_code in (200, 201) else resp.text[:300]}")
    return resp.status_code


if __name__ == "__main__":
    print("Uploading image...")
    media_url = upload_image(IMAGE_PATH)

    print("\nScheduling posts...")
    schedule_all(media_url)

    print("\nDone. Remember to add the article/video link as a first comment after each post publishes.")
