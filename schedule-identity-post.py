"""
Schedule the Identity post ("I spent 20 years building my identity as a doctor...")
Image: identity-white-coat.jpeg
Scheduled: 2026-04-01 at 12:00 PM ET (Wednesday)
Platforms: LinkedIn, Instagram, Facebook, TikTok (YouTube excluded — image only)
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

IMAGE_PATH    = "/Users/toto/Claude TubeonAI/identity-white-coat.jpeg"
SCHEDULED_FOR = "2026-04-01T12:00:00"

LINKEDIN_COPY = """I spent 20 years building my identity as a doctor.
Then I had to let it go.

Not because I failed. Not because I was forced out.

Because I finally asked a question I'd been avoiding for years:

"Is this still who I choose to be?"

The answer was no.

I expected relief. What I got first was grief.

Grief for the person I'd built. For the identity that had carried me through med school, residency, 12-hour shifts, and every dinner where I introduced myself as "Dr. Sahawat."

"Doctor" wasn't just my job title. It was the answer to every version of "who are you."

And letting it go felt — for a while — like dying.

But here's what nobody tells you about that kind of death:

Something else gets to be born.

I became a crossing guard. Wore a yellow vest. Helped first-graders cross the street.

Standing on that corner, watching people step off the curb into something new — I remembered who I was before medicine told me who to be.

That version of me? Still there. Just buried under a white coat for two decades.

If you're carrying a title that no longer fits — and you're terrified of what's underneath — I want to tell you: the fear is right. Something does die.

And what replaces it is worth it.

I built a 2-minute quiz that helps you name the fear keeping you inside that identity. Link in the first comment.

#HealthcareBurnout #PhysicianBurnout #IdentityShift #LeavingMedicine #CrosswalkWisdom #CareerTransition #NurseBurnout #HealthcareWorkers"""

INSTAGRAM_COPY = """I spent 20 years building my identity as a doctor.
Then I had to let it go. 🩺

Not because I failed.

Because I finally asked: "Is this still who I choose to be?"

I expected relief. What I got first was grief.

"Doctor" wasn't just my job title.
It was the answer to every version of "who are you."

Letting it go felt like dying — because a version of me was.

But here's what nobody tells you about that kind of death:

Something else gets to be born.

If you're carrying a title that no longer fits → the Fear Audit is 2 minutes and free. Link in bio.

#HealthcareBurnout #PhysicianBurnout #NurseBurnout #IdentityShift #LeavingMedicine #CrosswalkWisdom #CareerChange #BurnoutRecovery #HealthcareWorker #DoctorLife #NurseLife #MedTwitter #CareerTransition"""

FACEBOOK_COPY = """Something I've never said as clearly as I want to say it today:

I spent 20 years building my identity as a doctor. Then I had to let it go.

Not because I failed. Not because anyone pushed me out. Because I finally asked myself honestly: "Is this still who I choose to be?"

The answer was no.

I expected relief. What came first was grief. Real grief — for the person I'd built, for the identity I'd worn like armour through med school and residency and a thousand 12-hour shifts.

"Doctor" wasn't just a job title. It was my answer to every version of the question "who are you?"

Letting it go felt like dying. Because a version of me was.

But here's what nobody tells you about that kind of death: something else gets to be born.

If you're in healthcare right now and carrying a title that no longer fits — I'd love to hear from you in the comments. You're not alone in this.

And if you're ready to name what's holding you there, I built a free 2-minute quiz for exactly this. Link in the comments. 👇"""

def upload_image(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    print(f"  Uploading {filename} ({filesize:,} bytes)...")
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "image/jpeg", "fileSize": filesize},
    )
    r.raise_for_status()
    data = r.json()
    with open(filepath, "rb") as f:
        requests.put(data["uploadUrl"], data=f, headers={"Content-Type": "image/jpeg"}).raise_for_status()
    print(f"  Upload OK → {data['publicUrl'][:80]}")
    return data["publicUrl"]


def main():
    print("=== Identity Post — Schedule to 4 Platforms ===\n")

    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image not found at {IMAGE_PATH}")
        return

    image_url = upload_image(IMAGE_PATH)

    platforms = [
        {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": LINKEDIN_COPY,  "scheduledFor": SCHEDULED_FOR},
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": INSTAGRAM_COPY, "scheduledFor": SCHEDULED_FOR},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": FACEBOOK_COPY,  "scheduledFor": SCHEDULED_FOR},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": INSTAGRAM_COPY, "scheduledFor": SCHEDULED_FOR},
    ]

    body = {
        "content": LINKEDIN_COPY,
        "mediaItems": [{"url": image_url, "type": "image"}],
        "platforms": platforms,
        "scheduledFor": SCHEDULED_FOR,
        "timezone": TIMEZONE,
    }

    print("  Scheduling on LinkedIn, Instagram, Facebook, TikTok...")
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    print(f"  Response {r.status_code}: {r.text[:200]}")

    if r.status_code in (200, 201):
        print(f"\n✓ Scheduled for {SCHEDULED_FOR} ET — Wednesday April 1")
    else:
        print(f"\n✗ Failed with status {r.status_code}")


if __name__ == "__main__":
    main()
