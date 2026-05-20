"""
Schedule: "The Morning Nobody Knew My Name" story reel
Date: 2026-04-17 at 2:00pm ET
Platforms: LinkedIn, Instagram, Facebook, TikTok, YouTube (all 5)
Video: crosswalk-remotion/out/story/morning-nobody-knew-my-name.mp4
"""
import os
import time
import requests

BASE    = "https://zernio.com/api/v1"
API_KEY = "sk_d1c977cc304ec9685c24f22c7e3b868abd5a10b9db8f7648b2b74384ab1ca399"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"
TIMEZONE     = "America/New_York"

VIDEO_PATH    = "/Users/toto/Claude TubeonAI/crosswalk-remotion/out/story/morning-nobody-knew-my-name.mp4"
SCHEDULED_FOR = "2026-04-17T14:00:00"   # 2pm ET — no-Z + timezone field
YOUTUBE_TITLE = "I was a doctor. Then I became a crossing guard. Here's what happened."

# ─── Post copy ────────────────────────────────────────────────────────────────

LINKEDIN_COPY = """A few years ago, I was a doctor in Thailand.

Then I became a crossing guard in Canada.

---

The question isn't: what happened?

The question is: what did I find?

---

My first morning in the orange vest, -8°C, hands shaking — a little girl walked up to the curb and grabbed my hand.

No questions. No credentials checked. She just needed someone to help her cross.

✨ I found that worth was never in the title.
✨ I found that presence matters more than prestige.
✨ I found that the most important thing you do is not always the most impressive thing.

👣 The crossing guard vest taught me how to slow down.
👣 Slowing down taught me how to see.
👣 Seeing taught me who I was without the job.

I call it Crosswalk Wisdom — simple lessons from a street corner. The sidewalk is the classroom. You are the student.

If you're a healthcare worker standing at the edge of something — afraid to step off the curb — I built something for you. Takes 5 minutes. Gentle and honest.

📬 Link in the first comment.

---

Have you ever taken a step that didn't look impressive — but felt like the most honest thing you'd done in years? What's your version of the crossing?

#CrosswalkWisdom #BurnoutRecovery #NurseBurnout #HealthcareCareerChange"""

INSTAGRAM_COPY = """I was a doctor. Then I became a crossing guard in Canada.

My first morning in the vest, my hands were shaking — and not from the cold.

Nobody driving past knew who I used to be. For twelve years, my title had walked into every room before I did.

Standing at that intersection, I thought: I've made a terrible mistake.

Then a seven-year-old walked up to the curb and grabbed my hand without asking.

We crossed. She said thank you. She ran to class.

And I stood in the -8°C air with my stop sign and understood something for the first time:

The most important thing you do is not always the most impressive thing.

Worth was never in the title. It was always in the crossing.

I went back to Thailand changed. Not by Canada — by that sidewalk.

That experience is why I built Crosswalk Wisdom. For every healthcare worker standing at the edge of something, afraid to step off the curb.

The sidewalk is the classroom. You are the student. Healing is the lesson.

Link in bio if you're ready to cross.

#CrosswalkWisdom #BurnoutRecovery #NurseBurnout #HealthcareCareerChange"""

YOUTUBE_DESC = LINKEDIN_COPY + "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition"


# ─── Upload helper ────────────────────────────────────────────────────────────

def upload_video(filepath: str) -> str:
    """Presign → PUT → return publicUrl."""
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    print(f"  Uploading {filename} ({filesize / 1_000_000:.1f} MB)...")

    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "video/mp4", "fileSize": filesize},
    )
    r.raise_for_status()
    data   = r.json()
    up_url = data["uploadUrl"]
    pub    = data["publicUrl"]

    with open(filepath, "rb") as f:
        put = requests.put(up_url, data=f, headers={"Content-Type": "video/mp4"})
        put.raise_for_status()

    print(f"  Upload OK → {pub}")
    return pub


# ─── Schedule ─────────────────────────────────────────────────────────────────

def schedule(video_url: str) -> None:
    media = [{"url": video_url, "type": "video"}]

    platforms = [
        {
            "platform": "linkedin",
            "accountId": LINKEDIN_ID,
            "customContent": LINKEDIN_COPY,
            "scheduledFor": SCHEDULED_FOR,
        },
        {
            "platform": "instagram",
            "accountId": INSTAGRAM_ID,
            "customContent": INSTAGRAM_COPY,
            "scheduledFor": SCHEDULED_FOR,
        },
        {
            "platform": "facebook",
            "accountId": FACEBOOK_ID,
            "customContent": INSTAGRAM_COPY,
            "scheduledFor": SCHEDULED_FOR,
        },
        {
            "platform": "tiktok",
            "accountId": TIKTOK_ID,
            "customContent": INSTAGRAM_COPY,
            "scheduledFor": SCHEDULED_FOR,
        },
        {
            "platform": "youtube",
            "accountId": YOUTUBE_ID,
            "customContent": YOUTUBE_DESC,
            "title": YOUTUBE_TITLE,
            "scheduledFor": SCHEDULED_FOR,
        },
    ]

    body = {
        "content": LINKEDIN_COPY,
        "mediaItems": media,
        "platforms": platforms,
        "scheduledFor": SCHEDULED_FOR,
        "timezone": TIMEZONE,
    }

    print(f"  Scheduling to 5 platforms at {SCHEDULED_FOR} ET...")
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    if r.status_code in (200, 201):
        resp = r.json()
        post_id = resp.get("post", resp).get("_id", "unknown")
        print(f"  POST OK [{r.status_code}] → post ID: {post_id}")
        print(f"\n  Platforms: LinkedIn · Instagram · Facebook · TikTok · YouTube")
        print(f"  Time: April 17, 2026 at 2:00pm ET")
        print(f"\n  REMINDER: Drop the article link in first comment after publish.")
    else:
        print(f"  POST FAIL [{r.status_code}]: {r.text[:400]}")


# ─── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Story Reel Scheduler")
    print("  'The Morning Nobody Knew My Name'")
    print("="*60 + "\n")

    if not os.path.exists(VIDEO_PATH):
        print(f"  ERROR: Video not found at {VIDEO_PATH}")
        raise SystemExit(1)

    video_url = upload_video(VIDEO_PATH)
    time.sleep(1)
    schedule(video_url)
    print("\n" + "="*60 + "\n")
