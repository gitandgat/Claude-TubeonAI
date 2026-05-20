"""
Schedule: 10 Things to Stop — Fear Audit CTA
Hook: "You made it through a 12-hour shift without a single bathroom break."
Image: freepik__a-person-sitting-alone-in-a-softly-lit-hospital-co__52553.jpeg
Platforms: LinkedIn, Instagram, Facebook, TikTok (YouTube excluded — image only)
Date: 2026-05-05 at 3:00 PM ET
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

IMAGE_PATH    = "/Users/toto/Claude TubeonAI/crosswalk-remotion/public/assets/april/freepik__a-person-sitting-alone-in-a-softly-lit-hospital-co__52553.jpeg"
SCHEDULED_FOR = "2026-05-05T15:00:00"

LINKEDIN_COPY = """You made it through a 12-hour shift today without a single bathroom break.

You're proud of that.

That's the problem.

Healthcare trained you to treat your body like an inconvenience. Skip the water. Hold it. Be the one who never complains. And you got so good at it that you stopped noticing you were doing it.

Now you're reading burnout articles. Nodding at every item on every list. And still can't change anything.

Here's what those lists won't tell you:

The habits aren't the problem. The fear underneath them is.

Burned-out healthcare professionals who can't stop — can't stop saying yes, can't stop pushing through, can't stop holding everything in their heads — are almost always running from one of three specific fears:

Financial Insecurity — "I can't afford to slow down, even for a day."
Fear of Judgment — "What will people think if I'm the one who finally breaks?"
Identity Loss — "If I'm not the person who handles everything, who am I?"

That last one is the most common. And the hardest to see in yourself.

I built a free 2-minute assessment called the Fear Audit for exactly this moment — when you know something has to change, but you can't figure out why you're still stuck.

It doesn't give you more habits to break.

It gives you the name of the fear that's been making your decisions for you.

That name is where recovery actually starts.

Link in the first comment. Takes 2 minutes.

#HealthcareBurnout #NurseBurnout #PhysicianBurnout #BurnoutRecovery #IdentityLoss #CrosswalkWisdom #CareerTransition #HealthcareWorkers #FearAudit #CourageToChoose"""

INSTAGRAM_COPY = """You made it through a 12-hour shift without a single bathroom break.

You're proud of that. That's the problem.

Healthcare trained you to call exhaustion dedication. To treat self-sacrifice as professionalism. To override your body so many times you stopped noticing you were doing it.

So when you read "10 habits to stop when you're burned out" and nod at every single one — and still can't change — it's not a discipline problem.

It's because no habit advice works until you name the fear underneath it.

For most healthcare workers, it's one of three:

→ "I can't afford to stop." (Financial fear)
→ "People will judge me if I do." (Fear of judgment)
→ "I don't know who I am if I'm not this." (Identity loss)

That third one hits hardest. And most people have never heard it named out loud before.

I made a free 2-minute quiz that tells you which fear is running your life right now. It's called the Fear Audit.

Link in bio — or check the first comment.

You've pushed through long enough to deserve an actual answer.

#HealthcareBurnout #NurseBurnout #BurnoutRecovery #CrosswalkWisdom #FearAudit #IdentityLoss #NurseLife #HealthcareWorker #CareerTransition #CourageToChoose #PhysicianBurnout #MedTwitter"""

FACEBOOK_COPY = """You made it through a 12-hour shift today without a single bathroom break.

You're proud of that.

I want to sit with that for a moment — because it tells me something important.

Healthcare trained you to override your body. Skip the water. Hold it. Be the one who never complains. And you got so good at it that you stopped noticing you were doing it.

Now you're reading burnout articles. Nodding at every item on every list. And still can't change anything.

Here's what those lists don't tell you: the habits aren't the problem. The fear underneath them is.

Burned-out healthcare professionals who can't stop — can't stop saying yes, can't stop pushing through, can't stop holding everything in their heads — are almost always running from one of three specific fears:

Financial Insecurity: "I can't afford to slow down, even for a day."
Fear of Judgment: "What will people think if I'm the one who finally breaks?"
Identity Loss: "If I'm not the person who handles everything, who am I?"

That last one is the most common. And the hardest to see in yourself — because it's been masquerading as dedication for years.

I built a free 2-minute assessment called the Fear Audit for exactly this moment — when you know something has to change, but you can't figure out why you're still stuck.

It doesn't give you more habits to break. It gives you the name of the fear that's been making your decisions for you.

That name is where recovery actually starts.

Link in the comments — it takes 2 minutes.

If this resonated, share it with a healthcare professional you care about. They may not be looking for help yet — but someone naming what they're feeling might be exactly what they needed today."""

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
    print("=== Burnout Habits — Fear Audit CTA — Schedule to 4 Platforms ===\n")

    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image not found at {IMAGE_PATH}")
        return

    print("Step 1: Upload image to Zernio CDN")
    image_url = upload_image(IMAGE_PATH)

    print("\nStep 2: Schedule post")
    status = schedule_post(image_url)

    if status in (200, 201):
        print(f"\n✓ Scheduled for {SCHEDULED_FOR} ET — Tuesday May 5, 2026")
        print("  Reminder: post the Fear Audit link (fear-audit.vercel.app) as the first comment on each platform after it publishes.")
    else:
        print(f"\n✗ Failed with status {status}")


if __name__ == "__main__":
    main()
