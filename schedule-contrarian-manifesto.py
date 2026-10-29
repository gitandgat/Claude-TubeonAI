"""
Schedule the Contrarian Manifesto post across all 5 platforms.
Image: Walk out of the ward.jpeg
Scheduled: 2026-03-28 at 12:00 PM ET
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
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"
TIMEZONE     = "America/New_York"

IMAGE_PATH   = "/Users/toto/Claude TubeonAI/Walk out of the ward.jpeg"
SCHEDULED_FOR = "2026-03-30T12:00:00"

YOUTUBE_TITLE = "Burnout is not a wellness problem. It's an identity cage."

LINKEDIN_COPY = """Burnout is not a wellness problem. It's an identity cage.

And I'm tired of pretending otherwise.

Your hospital says you need more self-care.
Your EAP says you need a hotline.
The burnout podcast industry says you need a morning routine.

After 12 years in medicine and 2 years watching people cross the street, I've come to believe something different:

You are not burned out from working too hard.
You are burned out from being someone you didn't choose.

The cage isn't the hospital. It's the story you've been telling yourself about who you have to be.

"I am a doctor."
"I am a nurse."

These are not descriptions. They are load-bearing walls.

And taking them down feels like dying — because a version of you is.

Here's what nobody in healthcare is allowed to say out loud:

Leaving is not betrayal.
Erasing yourself to stay is.

If this landed differently than a wellness newsletter — you might be ready for the next step.

I built a 2-minute quiz that identifies the specific fear keeping you inside the cage. Link in the first comment.

#HealthcareBurnout #PhysicianBurnout #NurseBurnout #IdentityShift #CareerTransition #CrosswalkWisdom #BurnoutRecovery #HealthcareWorkers"""

INSTAGRAM_COPY = """Burnout isn't a wellness problem.

It's an identity cage. 🔒

You're not burned out from working too hard.
You're burned out from being someone you didn't choose.

The cage isn't the hospital.
It's the story you keep telling yourself about who you have to be.

"I am a doctor."
"I am a nurse."

These aren't descriptions. They're load-bearing walls.

Here's what nobody in healthcare says out loud:

Leaving is not betrayal.
Erasing yourself to stay is.

If this hit differently → take the Fear Audit. It's 2 minutes and free. Link in bio.

#HealthcareBurnout #NurseBurnout #PhysicianBurnout #BurnoutRecovery #IdentityShift #CareerChange #CrosswalkWisdom #HealthcareWorker #MedTwitter #NurseLife #DoctorLife #CareerTransition #HealthcareProfessionals"""

FACEBOOK_COPY = """Real talk for anyone in healthcare —

Burnout is not a wellness problem. It's an identity cage.

I've spent years watching burned-out healthcare workers try morning routines, meditation apps, and EAP hotlines. None of it works. Not because they're doing it wrong — but because they're solving the wrong problem.

You are not burned out from working too hard. You are burned out from being someone you didn't choose.

The cage isn't the hospital. It's the story you keep telling yourself: "I am a nurse." "I am a doctor." These feel like descriptions. They're actually load-bearing walls. And taking them down feels like dying — because a version of you is.

Here's what nobody in healthcare is allowed to say out loud: leaving is not betrayal. Erasing yourself to stay is.

I built a free 2-minute quiz — the Fear Audit — that identifies the specific fear keeping you inside the cage. Drop a 🙋 in the comments if you want the link.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom"""

YOUTUBE_DESC = LINKEDIN_COPY + "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition #PhysicianBurnout #IdentityShift"


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
    print(f"  Uploading to {upload_url[:60]}...")
    with open(filepath, "rb") as f:
        put_r = requests.put(upload_url, data=f, headers={"Content-Type": "image/jpeg"})
        put_r.raise_for_status()
    print(f"  Upload OK → {public_url[:80]}")
    return public_url


def schedule_post(image_url):
    media_item = {"url": image_url, "type": "image"}
    yt_desc = YOUTUBE_DESC

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
            "customContent": INSTAGRAM_COPY,
            "scheduledFor": SCHEDULED_FOR,
        },
        # YouTube excluded — requires video content, not images
    ]

    body = {
        "content": LINKEDIN_COPY,
        "mediaItems": [media_item],
        "platforms": platforms,
        "scheduledFor": SCHEDULED_FOR,
        "timezone": TIMEZONE,
    }

    print("  Creating post on LinkedIn, Instagram, Facebook, TikTok...")
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    print(f"  Response {r.status_code}: {r.text[:400]}")
    return r.status_code


def main():
    print("=== Contrarian Manifesto — Schedule to 5 Platforms ===\n")

    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image not found at {IMAGE_PATH}")
        return

    print("Step 1: Upload image to Zernio CDN")
    image_url = upload_image(IMAGE_PATH)

    print("\nStep 2: Schedule post")
    status = schedule_post(image_url)

    if status in (200, 201):
        print(f"\n✓ Scheduled for {SCHEDULED_FOR} ET on LinkedIn, Instagram, Facebook, TikTok")
    else:
        print(f"\n✗ Failed with status {status}")


if __name__ == "__main__":
    main()
