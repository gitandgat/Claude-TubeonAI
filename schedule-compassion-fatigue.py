"""
Schedule: Compassion Fatigue — "You Stopped Caring. You Didn't Mean To."
Hook: "You stopped caring. You didn't mean to. And now you're afraid that makes you a bad nurse."
Image: compassion-fatigue-nurse.jpg (square 1:1)
Platforms: LinkedIn, Instagram, Facebook, TikTok (YouTube excluded — image only)
Date: 2026-04-07 at 3:00 PM ET
"""
import os
import requests

BASE    = "https://zernio.com/api/v1"
from zernio_key import ZERNIO_API_KEY as API_KEY
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TIMEZONE     = "America/New_York"

IMAGE_PATH    = "/Users/toto/crosswalk-wisdom-new/public/compassion-fatigue-nurse.jpg"
SCHEDULED_FOR = "2026-04-25T08:00:00"

LINKEDIN_COPY = """You stopped caring.

You didn't mean to. And now you're afraid that makes you a bad nurse.

The question isn't "What kind of caregiver doesn't care anymore?"

It's "What kind of system extracts empathy at scale — and never asks what's left for you?"

---

Here's what's actually happening under the hood.

Every time you sit with someone's pain, your nervous system mirrors it.

Dozens of times a day.
For years.

👣 Your brain doesn't have infinite load capacity.
👣 When that load maxes out without real recovery, the system starts throttling input.
👣 Automatically. Involuntarily.
👣 Your brain learned to feel less so it could keep showing up.

That's compassion fatigue. Not weakness. Biology.

---

And then it follows you home.

✨ You go through the motions — competently.
✨ Your hands do what they're trained to do.
✨ Your voice stays steady.
✨ But something is gone. And you can feel that you're not feeling it.

The guilt arrives right behind it: "What kind of caregiver doesn't care anymore?"

The answer: the depleted kind.

Depletion is not a character flaw. It's a signal.

I call it the moment the body becomes smarter than the calendar. Crosswalk Wisdom was built for that moment — and for what comes next.

I wrote the full piece — the mechanism, the misdiagnosis, and the question that actually helps. Link in the first comment.

---

Have you ever felt the numbness before you could name it? What was the moment you realized it wasn't just a bad week?

#BurnoutRecovery #NurseBurnout #HealthcareBurnout #CrosswalkWisdom"""

INSTAGRAM_COPY = """You stopped caring.

You didn't mean to. And now you're afraid that makes you a bad nurse.

It doesn't. It makes you a depleted human. There's a difference.

---

Every time you sit with someone's pain, your nervous system mirrors it. Dozens of times a day. For years.

Eventually it starts throttling the input automatically. Your brain learns to feel less so it can keep showing up.

That's not failure. That's biology. Your body running damage control on your behalf.

The guilt that follows — "what kind of caregiver doesn't care anymore?" — is the most unfair part of all.

The answer: the exhausted kind. And exhaustion is a signal, not a verdict.

Full piece at the link in bio 🔗

#nurseburnout #compassionfatigue #nurselife #burnoutrecovery #nursepractitioner #healthcareburnout #nplife #nursinglife #careerchange #healthcareworkers #burnout #nursecareerchange #crosswalkwisdom"""

FACEBOOK_COPY = """Can I say something out loud that most healthcare professionals are only thinking in the parking lot?

You stopped caring. And you didn't mean to. And now you're terrified that makes you a bad nurse — or a bad doctor, or a bad NP.

It doesn't. It makes you a depleted human. There's a difference.

Compassion fatigue isn't a character flaw. It's what happens when your capacity to feel for others gets used as a resource — extracted, optimized, scheduled — without anyone ever asking if there was anything left for you.

Your nervous system isn't broken. It's protecting you.

I wrote about what that actually looks like, why the usual fixes don't work, and the one question that does. It's in this week's post → link in first comment.

If this sounds like you, or someone you know — share it. This one needs to land with the right people."""

TIKTOK_COPY = INSTAGRAM_COPY


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
    print(f"  Uploading...")
    with open(filepath, "rb") as f:
        put_r = requests.put(upload_url, data=f, headers={"Content-Type": "image/jpeg"})
        put_r.raise_for_status()
    print(f"  Upload OK → {public_url[:80]}")
    return public_url


def schedule_post(image_url):
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
    print(f"  Response {r.status_code}: {r.text[:500]}")
    return r.status_code


def main():
    print("=== Compassion Fatigue — Schedule to 4 Platforms ===\n")

    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image not found at {IMAGE_PATH}")
        return

    print("Step 1: Upload image to Zernio CDN")
    image_url = upload_image(IMAGE_PATH)

    print("\nStep 2: Schedule post")
    status = schedule_post(image_url)

    if status in (200, 201):
        print(f"\n✓ Scheduled for {SCHEDULED_FOR} ET — Saturday April 25, 2026")
        print("  Reminder: post the blog link (crosswalkwisdom.com/blog/compassion-fatigue-what-nobody-tells-you)")
        print("  as the first comment on LinkedIn and Facebook after it publishes.")
    else:
        print(f"\n✗ Failed with status {status}")


if __name__ == "__main__":
    main()
