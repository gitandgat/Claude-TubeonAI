"""
Schedule: LinkedIn Sunk Cost Post (Full Post, Hook C)
Source:   output/linkedin-sunk-cost-post.md — Full Post (Hook C)
Image:    crosswalk-remotion/public/assets/post-sunk-cost.jpg (2048x2048 square)
Date:     2026-05-12 (Tuesday) at 8:00 AM ET = 12:00 UTC

Post 1: LinkedIn, Instagram, Facebook, TikTok — with image
Post 2: YouTube — text only (YouTube rejects image-only posts)
"""
import os
import time
import json
import requests

BASE    = "https://zernio.com/api/v1"
API_KEY = "***REMOVED-ZERNIO-KEY***"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"
TIMEZONE      = "America/New_York"
SCHEDULED_FOR = "2026-05-12T08:00:00"

IMAGE_PATH = "/Users/toto/Claude TubeonAI/crosswalk-remotion/public/assets/post-sunk-cost.jpg"
OUTPUT_FILE = "/Users/toto/Claude TubeonAI/output/linkedin-sunk-cost-scheduled.md"

# ── Content ────────────────────────────────────────────────────────────────────

LINKEDIN_COPY = """\
You've lost $80,000. Five years. Your accent. Maybe your marriage.
Here's why "keep going" is the most dangerous advice anyone can give you.

The question isn't "how do I finally get matched?"
It's "what does the next dollar buy that the last $80,000 didn't?"

The Canadian residency match rate for IMGs is 10\u201322%.
Not because you aren't good enough.
Because the system was never designed to say yes to most of you.

That's not a motivational reframe. That's the math.

And yet \u2014 the sunk cost runs four layers deep.

\u2728 Financial: "I've spent too much to stop now."
\u2728 Time: "I've given too many years to walk away."
\u2728 Identity: "If I'm not a doctor, who am I?"
\u2728 Immigration: "If I step off this path, I lose Canada."

Every layer feels like a reason to stay.
Every layer is also a cage.

The crosswalk taught me something the treadmill never did:

\U0001f463 To see the difference between past investment and future cost \u2014 they are not the same ledger.
\U0001f463 To name the immigration fear out loud \u2014 it doesn't disappear by staying silent (and NOC codes exist for a reason).
\U0001f463 To separate "I am a doctor" from "I have a medical degree" \u2014 one is your identity, one is an asset.
\U0001f463 To understand that the next year is a choice. The last five are not.

I call it Crosswalk Wisdom \u2014 simple lessons from a simple place.

You didn't fail medicine.
The match rate failed you.
Those are not the same sentence.

If the math on your residency journey stopped making sense, I built a free calculator that shows you your actual numbers \u2014 financial, timeline, and what staying one more year really costs.
It takes 5 minutes. Gentle and honest. Link in the first comment.

Have you ever kept going at something \u2014 not because you believed in it, but because you'd already given too much to stop?
What finally helped you see the cost clearly?

#CrosswalkWisdom #BurnoutRecovery #IMGCanada #MedicalGraduate"""

INSTAGRAM_COPY = """\
You've lost $80,000. Five years. Your accent. Maybe your marriage.
Here's why "keep going" is the most dangerous advice anyone can give you.

The Canadian residency match rate for IMGs is 10\u201322%.
Not because you aren't good enough.
Because the system was never designed to say yes to most of you.

The sunk cost runs four layers deep:

\u2728 Financial: "I've spent too much to stop now."
\u2728 Time: "I've given too many years to walk away."
\u2728 Identity: "If I'm not a doctor, who am I?"
\u2728 Immigration: "If I step off this path, I lose Canada."

Every layer feels like a reason to stay.
Every layer is also a cage.

You didn't fail medicine.
The match rate failed you.
Those are not the same sentence.

Free sunk cost calculator \u2014 link in bio.

#CrosswalkWisdom #BurnoutRecovery #IMGCanada #MedicalGraduate #HealthcareBurnout #NurseBurnout #CareerTransition"""

FACEBOOK_COPY = LINKEDIN_COPY

TIKTOK_COPY = INSTAGRAM_COPY

YOUTUBE_TITLE = "You\u2019ve lost $80,000. Five years. Your accent. Maybe your marriage."

YOUTUBE_COPY = LINKEDIN_COPY + "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition"


# ── Helpers ────────────────────────────────────────────────────────────────────

def upload_image(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    print(f"  Presigning {filename} ({filesize:,} bytes)...")
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "image/jpeg", "fileSize": filesize},
    )
    r.raise_for_status()
    data = r.json()
    upload_url = data["uploadUrl"]
    public_url = data["publicUrl"]
    print(f"  Uploading to CDN...")
    with open(filepath, "rb") as f:
        put_r = requests.put(upload_url, data=f, headers={"Content-Type": "image/jpeg"})
        put_r.raise_for_status()
    print(f"  Upload OK -> {public_url[:80]}")
    return public_url


def schedule_image_post(image_url):
    """Post 1: LinkedIn, Instagram, Facebook, TikTok with image."""
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
            "customContent": FACEBOOK_COPY,
            "scheduledFor": SCHEDULED_FOR,
        },
        {
            "platform": "tiktok",
            "accountId": TIKTOK_ID,
            "customContent": TIKTOK_COPY,
            "scheduledFor": SCHEDULED_FOR,
        },
    ]

    body = {
        "content": LINKEDIN_COPY,
        "mediaItems": [{"url": image_url, "type": "image"}],
        "platforms": platforms,
        "scheduledFor": SCHEDULED_FOR,
        "timezone": TIMEZONE,
    }

    print("  Creating post on LinkedIn, Instagram, Facebook, TikTok...")
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    print(f"  Response {r.status_code}: {r.text[:300]}")
    if r.status_code not in (200, 201):
        print(f"  ERROR: {r.text}")
        return None
    return r.json()


def schedule_youtube_text_post():
    """Post 2: YouTube text-only (YouTube rejects image-only posts)."""
    platforms = [
        {
            "platform": "youtube",
            "accountId": YOUTUBE_ID,
            "customContent": YOUTUBE_COPY,
            "title": YOUTUBE_TITLE,
            "scheduledFor": SCHEDULED_FOR,
        },
    ]

    body = {
        "content": YOUTUBE_COPY,
        "platforms": platforms,
        "scheduledFor": SCHEDULED_FOR,
        "timezone": TIMEZONE,
    }

    print("  Creating text post on YouTube...")
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    print(f"  Response {r.status_code}: {r.text[:300]}")
    if r.status_code not in (200, 201):
        print(f"  ERROR: {r.text}")
        return None
    return r.json()


def extract_id(response_json):
    if not response_json:
        return "FAILED"
    return response_json.get("id") or response_json.get("_id") or str(response_json)[:80]


def write_output(post1_id, post2_id, image_url):
    lines = [
        "# LinkedIn Sunk Cost Post — Scheduled",
        "",
        f"**Scheduled for:** {SCHEDULED_FOR} ET (Tuesday 2026-05-12, 8:00 AM ET = 12:00 UTC)",
        f"**Image used:** post-sunk-cost.jpg (2048x2048)",
        f"**CDN URL:** {image_url}",
        "",
        "## Post IDs",
        "",
        f"| Platform | Post ID |",
        f"|----------|---------|",
        f"| LinkedIn, Instagram, Facebook, TikTok | {post1_id} |",
        f"| YouTube (text-only) | {post2_id} |",
        "",
        "## Action Required",
        "",
        "Post the first comment on LinkedIn immediately after the post goes live:",
        "> Here's the free sunk cost calculator for IMGs — see your real numbers in 5 minutes: [CALCULATOR_URL]",
        "",
    ]
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines))
    print(f"\nOutput written to {OUTPUT_FILE}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=== LinkedIn Sunk Cost Post — Schedule to All 5 Platforms ===\n")

    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image not found at {IMAGE_PATH}")
        return

    # Step 1: Upload image
    print("Step 1: Upload image to Zernio CDN")
    image_url = upload_image(IMAGE_PATH)
    print()

    # Step 2: Schedule image post on 4 platforms
    print("Step 2: Schedule image post (LinkedIn / Instagram / Facebook / TikTok)")
    post1 = schedule_image_post(image_url)
    post1_id = extract_id(post1)
    print(f"  Post ID: {post1_id}")
    print()

    time.sleep(1.5)

    # Step 3: Schedule text post on YouTube
    print("Step 3: Schedule text post (YouTube)")
    post2 = schedule_youtube_text_post()
    post2_id = extract_id(post2)
    print(f"  Post ID: {post2_id}")
    print()

    # Step 4: Write output log
    write_output(post1_id, post2_id, image_url)

    print("\n=== SUMMARY ===")
    print(f"Scheduled: {SCHEDULED_FOR} ET (Tuesday 2026-05-12, 8am ET = 12:00 UTC)")
    print(f"LI/IG/FB/TT post ID : {post1_id}")
    print(f"YouTube post ID     : {post2_id}")
    print()
    print("ACTION: Post first comment on LinkedIn after publishing:")
    print("  'Here's the free sunk cost calculator for IMGs")
    print("   - see your real numbers in 5 minutes: [CALCULATOR_URL]'")


if __name__ == "__main__":
    main()
