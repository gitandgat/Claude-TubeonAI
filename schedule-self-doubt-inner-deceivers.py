"""
Schedule: Overcoming Self-Doubt — The Five Inner Deceivers
Platforms: LinkedIn, Instagram, Facebook, TikTok (YouTube excluded — text only)
Date: 2026-05-03 at 9:00 AM ET
Image: bg-carousel-nobody-tells-you.jpg
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
TIMEZONE     = "America/New_York"

IMAGE_PATH    = "/Users/toto/Claude TubeonAI/crosswalk-remotion/public/assets/bg-carousel-nobody-tells-you.jpg"
SCHEDULED_FOR = "2026-05-03T09:00:00"

LINKEDIN_COPY = """Self-doubt doesn't disappear when you get promoted.

It scales with responsibility.

(Research shows 90-95% of leaders — even at Google, McKinsey, and JP Morgan — experience it. The small group that doesn't? Often includes narcissists.)

So if you're waiting to feel confident before you take the next step — you'll wait forever.

What actually works: learning to separate from your inner critic.

Researchers found 5 recurring voices in hundreds of interviews with senior leaders:

→ The Judge: "You're not enough."
→ The Victimizer: "Nothing will change for you."
→ The Misguided Protector: "Stay small. It's safer."
→ The Ringmaster: "One more win and you'll finally feel worthy."
→ The Neglector: "Everyone else's needs come first."

The breakthrough isn't silencing these voices.

It's refusing to become them.

When one shows up, name it: "Classic Judge. I see you — but no thanks."

One language shift that also helps: replace "I should" with "I could" or "I choose to."

"Should" triggers resistance. "Choose to" restores agency.

Which of the 5 voices shows up most for you?

→ Join the free Crosswalk Wisdom email list for tools like this, delivered weekly. Link in the first comment.

#SelfDoubt #InnerCritic #MindsetShift #Leadership #CourageToChoose"""

INSTAGRAM_COPY = """Your inner critic has a name.

And the second you name it — everything shifts.

Researchers found 5 voices behind self-doubt in thousands of senior leaders:

→ The Judge: "You're not enough."
→ The Victimizer: "Nothing will change."
→ The Misguided Protector: "Stay small — it's safer."
→ The Ringmaster: "One more win and you'll feel worthy."
→ The Neglector: "Everyone else comes first."

Self-doubt doesn't disappear when you succeed. It scales with responsibility.

The practice: when one of these voices shows up, name it out loud. "Classic Judge. I see you — but no thanks."

That gap between thought and response? That's where your power lives.

Join the free Crosswalk Wisdom email list for tools like this. Link in bio.

#SelfDoubt #InnerCritic #BurnoutRecovery #CrosswalkWisdom #CourageToChoose #HealthcareBurnout #MindsetShift #NurseBurnout #Burnout #IdentityShift"""

FACEBOOK_COPY = """Have you ever crushed a goal — a promotion, a major project, a personal achievement — and then waited for the feeling of "enough" to finally arrive?

For most of us, it never does.

That's not a character flaw. It's your brain doing its job.

A psychologist who works with senior leaders at Google, Microsoft, and McKinsey shared something that stopped me cold: self-doubt doesn't disappear with success. It actually scales with responsibility. The more visible you become, the louder the inner critic gets.

So what do we do with that?

He described five recurring voices — what he calls the "inner deceivers" — identified across hundreds of interviews:

The Judge tells you that you're not enough. The Victimizer convinces you nothing will ever change. The Misguided Protector warns you away from every risk. The Ringmaster promises satisfaction after the next milestone — then moves the target. And the Neglector tells you that your needs simply don't matter as much as everyone else's.

Sound familiar?

Here's the small but powerful practice he recommends: when a critical thought shows up, name the voice out loud. "That's the Ringmaster talking." Then respond: "I see you. But no thanks."

That moment of naming creates psychological distance. And distance is where your power lives.

If any of this resonates, join the free Crosswalk Wisdom email list. Tools like this, every week, for people who are ready to stop living inside their inner critic's story.

Link in the comments."""

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
    print("=== Self-Doubt: Five Inner Deceivers — Schedule to 4 Platforms ===\n")

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
