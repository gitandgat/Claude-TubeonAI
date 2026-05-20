"""
Schedule Fear Audit Instagram Reel — April 5, 2026 at 5pm ET (21:00 UTC)
All 5 platforms: LinkedIn, Instagram, Facebook, TikTok, YouTube
"""
import os
import requests

BASE    = "https://zernio.com/api/v1"
API_KEY = "***REMOVED-ZERNIO-KEY***"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"

VIDEO_PATH    = "/Users/toto/Claude TubeonAI/crosswalk-remotion/out/fear-audit-reel.mp4"
SCHEDULED_FOR = "2026-04-05T21:00:00.000Z"  # 5pm ET (EDT = UTC-4)
TIMEZONE      = "America/New_York"
YOUTUBE_TITLE = "The fear that keeps physicians stuck (and how to name it)"

CAPTION = """Most physicians don't leave medicine because they hate it.

They stay because they're terrified of who they'll be without it.

I know. I was one of them.

I spent a decade building a medical identity in Thailand. "Dr." was the only title I allowed myself to have.

Then I walked away. And became a crossing guard.

People thought I'd lost my mind.

What I'd actually lost was the fear.

If you're a physician quietly asking yourself "is this all there is?" — that voice isn't weakness. It's the most honest thing you've felt in years.

I built something for you. It's free, takes 3 minutes.

Link in bio → Fear Audit"""

CAPTION_YT = CAPTION + "\n\n#Shorts #CrosswalkWisdom #PhysicianBurnout #HealthcareBurnout #CareerTransition #FearAudit"


def upload_video(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "video/mp4", "fileSize": filesize},
    )
    r.raise_for_status()
    data = r.json()
    upload_url = data["uploadUrl"]
    public_url = data["publicUrl"]
    with open(filepath, "rb") as f:
        put_r = requests.put(upload_url, data=f, headers={"Content-Type": "video/mp4"})
        put_r.raise_for_status()
    print(f"  [UPLOAD OK] {public_url[:60]}...")
    return public_url


def main():
    print("Scheduling Fear Audit Reel — April 5 @ 5pm ET\n")

    if not os.path.exists(VIDEO_PATH):
        print(f"[ERROR] Video not found: {VIDEO_PATH}")
        return

    video_url = upload_video(VIDEO_PATH)

    body = {
        "content": CAPTION,
        "mediaItems": [{"url": video_url, "type": "video"}],
        "scheduledFor": SCHEDULED_FOR,
        "timezone": TIMEZONE,
        "platforms": [
            {
                "platform": "linkedin",
                "accountId": LINKEDIN_ID,
                "customContent": CAPTION,
                "scheduledFor": SCHEDULED_FOR,
            },
            {
                "platform": "instagram",
                "accountId": INSTAGRAM_ID,
                "customContent": CAPTION,
                "scheduledFor": SCHEDULED_FOR,
            },
            {
                "platform": "facebook",
                "accountId": FACEBOOK_ID,
                "customContent": CAPTION,
                "scheduledFor": SCHEDULED_FOR,
            },
            {
                "platform": "tiktok",
                "accountId": TIKTOK_ID,
                "customContent": CAPTION,
                "scheduledFor": SCHEDULED_FOR,
            },
            {
                "platform": "youtube",
                "accountId": YOUTUBE_ID,
                "customContent": CAPTION_YT,
                "title": YOUTUBE_TITLE,
                "scheduledFor": SCHEDULED_FOR,
            },
        ],
    }

    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    if r.status_code in (200, 201):
        print(f"  [SCHEDULED OK] All 5 platforms — April 5 @ 5pm ET")
    else:
        print(f"  [FAIL {r.status_code}] {r.text[:300]}")


if __name__ == "__main__":
    main()
