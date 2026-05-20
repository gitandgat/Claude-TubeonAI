"""
Schedule: "bedside hours" standalone image post
Image: /Users/toto/crosswalk-wisdom-new/public/bedside-hour.jpg
Platforms: LI / IG / FB / TT (no YouTube — image post)
Date: 2026-04-05 at 9:00am ET (13:00 UTC)
"""
import os, requests

BASE    = "https://zernio.com/api/v1"
API_KEY = "***REMOVED-ZERNIO-KEY***"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"

IMAGE_PATH   = "/Users/toto/crosswalk-wisdom-new/public/bedside-hour.jpg"
SCHEDULE_AT  = "2026-04-05T13:00:00.000Z"   # 9:00am ET
TIMEZONE     = "America/New_York"

# ── Platform copy ─────────────────────────────────────────────────────────────

LINKEDIN = """The healthcare system told you your value lives in your bedside hours.
AI just made bedside hours the lowest-leverage thing in the room.
What happens to your identity when the cage disappears?

There's a new role emerging right now: the agent operator.

Not someone who executes tasks. Someone who manages systems that do.

Here's what nobody's saying out loud — but I will:

Nurses, NPs, and physicians have been agent operators for decades.

You triaged complexity no algorithm could replicate.
You made judgment calls with incomplete information at 3am.
You held broken systems together with training, intuition, and will.

The system just convinced you that none of it counted unless it happened at the bedside.

That was the cage.

AI isn't taking your skills. It's exposing the lie that your skills only exist inside a hospital.

The identity crisis you're feeling right now — the "who am I if I'm not a nurse?" spiral — that's not weakness.

That's the first honest question you've asked yourself in years.

The cage is opening. The question is whether you walk through.

#HealthcareWorkers #BurnoutRecovery #NursePractitioner #IdentityShift #CourageToChoose"""

INSTAGRAM = """The healthcare system told you your value lives in your bedside hours.
AI just made bedside hours the lowest-leverage thing in the room.
What happens to your identity when the cage disappears?

You've been triaging complexity, making judgment calls on incomplete information, and holding broken systems together with sheer will for years.

The system just convinced you none of it counted unless it happened at the bedside.

That was the lie. AI is exposing it.

The identity crisis you're feeling right now? That's not weakness. That's the first honest question you've asked in years.

Link in bio.

#BurnoutRecovery #HealthcareWorkers #NurseBurnout #PhysicianBurnout #IdentityShift #NursePractitioner #HealthcareLeadership #CourageToChoose #NurseLife #BurnoutHealing #CareerTransition #HealthcareTransformation"""

FACEBOOK = """The healthcare system told you your value lives in your bedside hours.
AI just made bedside hours the lowest-leverage thing in the room.
What happens to your identity when the cage disappears?

There's a new role emerging right now — the "agent operator." Someone who manages intelligent systems instead of executing tasks.

And here's what I keep thinking: healthcare professionals have been doing exactly that for decades. You triaged chaos. You made calls with no good options. You coordinated teams, held broken systems together, and kept humans alive on pure skill and judgment.

But somehow the system convinced you that none of it counted unless it was happening inside a hospital.

The identity crisis you're feeling — that "who am I if I'm not a nurse?" spiral — that's not weakness. That's the first honest question you've asked yourself in years.

The cage is opening. Are you going to walk through it?"""

TIKTOK = """The system told you your value lives in your bedside hours.
AI just made bedside hours the lowest-leverage thing in the room.
You've been an agent operator for decades — managing systems, triaging complexity, making judgment calls under pressure.
The cage was never your identity. It was just where they put you.
Are you ready to walk through?

#HealthcareWorkers #BurnoutRecovery #NurseBurnout #IdentityShift #CourageToChoose"""

# ── Upload image ──────────────────────────────────────────────────────────────

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
    print(f"  Uploaded → {public_url}")
    return public_url

# ── Schedule one post ─────────────────────────────────────────────────────────

def schedule(platform_id, content, media_url, label):
    payload = {
        "socialAccountIds": [platform_id],
        "content": content,
        "scheduledAt": SCHEDULE_AT,
        "timezone": TIMEZONE,
        "mediaItems": [{"url": media_url, "type": "image"}],
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=payload)
    print(f"  {label}: {r.status_code} {r.text[:120]}")

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Uploading image...")
    media_url = upload_image(IMAGE_PATH)

    print("Scheduling posts...")
    schedule(LINKEDIN_ID,  LINKEDIN,  media_url, "LinkedIn")
    schedule(INSTAGRAM_ID, INSTAGRAM, media_url, "Instagram")
    schedule(FACEBOOK_ID,  FACEBOOK,  media_url, "Facebook")
    schedule(TIKTOK_ID,    TIKTOK,    media_url, "TikTok")

    print("\nDone. Add the article link as first comment on each platform after publish.")
