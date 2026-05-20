"""
Schedule: Crosswalk Burnout Assessment — 4 Stages CTA
Hook: "One of the answers on this burnout assessment reads: 'I've stopped imagining a future.'"
Image: freepik__cinematic-shot-of-a-person-walking-across-a-wet-ci__52554.jpeg
Platforms: LinkedIn, Instagram, Facebook, TikTok (YouTube excluded — image only)
Date: 2026-05-07 at 3:00 PM ET
First comment URL: crosswalkwisdom.com/assessment
"""
import os
import requests

BASE    = "https://zernio.com/api/v1"
API_KEY = "sk_d1c977cc304ec9685c24f22c7e3b868abd5a10b9db8f7648b2b74384ab1ca399"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TIMEZONE     = "America/New_York"

IMAGE_PATH    = "/Users/toto/Claude TubeonAI/crosswalk-remotion/public/assets/april/freepik__cinematic-shot-of-a-person-walking-across-a-wet-ci__52554.jpeg"
SCHEDULED_FOR = "2026-05-07T15:00:00"

LINKEDIN_COPY = """One of the answers on this burnout assessment reads:

"I've stopped imagining a future."

If that sentence just hit you somewhere — you already know which stage you're in.

Most burnout resources treat it like a yes/no question. Are you burned out? And if yes — here's your meditation app, your breathing exercise, your work-life balance tip.

But burnout isn't a diagnosis. It's a location. And where you are right now changes everything about what you actually need.

I built a free 12-question assessment that places you in one of 4 stages:

START — You're noticing the cracks before they become canyons. The most powerful place to be.
STOP — You've hit the yellow light. The old coping mechanisms aren't working. This is the pause before the turn.
ELDER — You're reaching outward for answers because the ones inside feel depleted. That's not weakness. That's wisdom.
HUMAN — The armor has come off. This stage feels like the end. It's actually the beginning.

Each stage gets a specific next step. Not a generic habit list. The one move that actually makes sense for where you are right now.

2 minutes. Free. Built for nurses, doctors, and healthcare workers who are tired of being told to do more self-care.

Link in the first comment.

Which stage do you think you're in?

#HealthcareBurnout #NurseBurnout #BurnoutRecovery #PhysicianBurnout #CrosswalkWisdom #IdentityLoss #HealthcareWorkers #CareerTransition #BurnoutAssessment"""

INSTAGRAM_COPY = """One of the answers on this burnout assessment reads:

"I've stopped imagining a future."

If that sentence just hit you — you already know which stage you're in.

Burnout isn't a yes/no question. It's a location.

There are 4 stages:

START — The cracks haven't become canyons yet.
STOP — You've hit the yellow light.
ELDER — You're seeking answers because the ones inside feel depleted.
HUMAN — The armor has come off. This isn't the end. It's the beginning.

Each one has a different next step. Not "meditate more." The actual move for where you are right now.

Free. 12 questions. 2 minutes. Built for nurses, doctors, and healthcare workers.

Link in bio — or check the first comment.

Which stage feels most like you right now? Drop it below. 👇

#HealthcareBurnout #NurseBurnout #BurnoutRecovery #CrosswalkWisdom #NurseLife #HealthcareWorker #IdentityLoss #PhysicianBurnout #CareerTransition #BurnoutStages"""

FACEBOOK_COPY = """One of the answers on this burnout assessment reads: "I've stopped imagining a future."

When I wrote that question, I already knew — for people in the deepest stage of burnout, that sentence isn't dramatic. It's just accurate.

Here's what I've learned from talking to hundreds of burned-out healthcare workers: burnout isn't a single state. It's a location. And where you are determines what you actually need to start moving again.

I built a free 12-question assessment that identifies which of 4 stages you're in:

The START stage: You're noticing the early signs before they become crises. That awareness is the most powerful thing you can have right now.

The STOP stage: Something in you has hit the brakes. The old ways of coping stopped working. This is the pause before the turn — not a failure.

The ELDER stage: You're reaching outward — books, coaches, anything that might show you a way through. That reaching is wisdom, not weakness.

The HUMAN stage: The armor has come off. This feels like the end. It's actually the beginning of something real.

Each stage gets a specific next step. Not a wellness checklist. The one move that makes sense for exactly where you are.

If you're a nurse, NP, doctor, or any healthcare professional who is tired of generic burnout advice — I built this for you.

Free. 12 questions. 2 minutes.

Link in the comments. And if you're comfortable — tell me which stage resonates most. I read every response."""

TIKTOK_COPY = """One of the answers on this burnout assessment reads:

"I've stopped imagining a future."

If that sentence just hit you — you already know which stage you're in.

Burnout isn't a yes/no question. It's a location.

There are 4 stages:

START — The cracks haven't become canyons yet.
STOP — You've hit the yellow light.
ELDER — You're seeking answers because the ones inside feel depleted.
HUMAN — The armor has come off. This isn't the end. It's the beginning.

Each one has a different next step. Not "meditate more." The actual move for where you are right now.

Free. 12 questions. 2 minutes. Built for nurses, doctors, and healthcare workers.

Link in bio.

#HealthcareBurnout #NurseBurnout #BurnoutRecovery #CrosswalkWisdom #NurseLife #HealthcareWorker #IdentityLoss #PhysicianBurnout #CareerTransition #BurnoutStages"""


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
    print("=== Burnout Assessment: 4 Stages — Schedule to 4 Platforms ===\n")

    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image not found at {IMAGE_PATH}")
        return

    print("Step 1: Upload image to Zernio CDN")
    image_url = upload_image(IMAGE_PATH)

    print("\nStep 2: Schedule post")
    status = schedule_post(image_url)

    if status in (200, 201):
        print(f"\n✓ Scheduled for {SCHEDULED_FOR} ET — Thursday May 7, 2026")
        print("  Reminder: post crosswalkwisdom.com/assessment as the first comment on each platform after it publishes.")
    else:
        print(f"\n✗ Failed with status {status}")


if __name__ == "__main__":
    main()
