"""
Schedule the Viral Hooks founding-launch post across LI / IG / FB / TT.
Hook C, square brand card, link-in-first-comment (LI/FB) / link-in-bio (IG/TT).
Reads ZERNIO_API_KEY from .env (no hardcoded key).
"""
import os, requests
from dotenv import load_dotenv

load_dotenv()

BASE = "https://zernio.com/api/v1"
KEY = os.getenv("ZERNIO_API_KEY")
if not KEY:
    raise SystemExit("ZERNIO_API_KEY not set in .env")
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TIMEZONE     = "America/New_York"

SCHEDULED_FOR = "2026-06-19T08:00:00"  # 8am ET
IMAGE = "/Users/toto/Claude TubeonAI/viral-hooks-launch-card.png"

# First comment (LI/FB) — carries the founding link out of the post body
FC = "Founding access, locked in for life → https://sahawat.gumroad.com/l/viral-hooks"

LI = """I got so tired of staring at a blank caption box that I built something to fill it.

Five hooks. Sixty seconds.

Here's the thing nobody tells you about posting consistently: writing the post was never the hard part. The hard part is the first line — the one that decides whether anyone reads the other 200 words you sweated over.

I'd draft a whole post in fifteen minutes, then lose two hours to the opening line. Every time.

So I built a tool that studies the hook patterns that actually stop the scroll, and rewrites them in your voice. You give it a topic. It hands you five openers worth posting. You pick one and go.

It's been quietly running my own content for weeks. A few people asked what changed. This is what changed.

I'm opening it to a small founding group at $9/month — locked in for life.

If the blank caption box is where your posts go to die, this is the cheapest fix you'll ever find.

(Founding link in the comments.)

#ContentCreation #Copywriting #ContentMarketing #PersonalBranding #CreatorEconomy"""

IG = """I got so tired of staring at a blank caption box that I built something to fill it. Five hooks, sixty seconds.

Writing the post was never the hard part. The first line is — it's the one that decides if anyone reads the rest.

This tool studies the hooks that actually stop the scroll and rewrites them in your voice. Topic in, five openers out.

Founding access is $9/month, locked in for life. Link in bio.

#ContentCreation #ContentCreator #Copywriting #ContentMarketing #SocialMediaTips #CreatorEconomy #PersonalBranding #ContentStrategy #WritingTips #SocialMediaMarketing #BuildInPublic #HookWriting"""

FB = """I got so tired of staring at a blank caption box that I built something to fill it.

Funny thing — writing the post was never my problem. It was the first line. I'd lose two hours to one opening sentence, every single time. So I built a tool that hands me five scroll-stopping openers in about a minute, in my own voice.

It's been running my content quietly for weeks, and I'm finally opening it to a few founding members at $9/month.

Be honest: how long do you spend on the first line before you give up and just hit publish?"""

# TikTok photo posts use content as the slideshow title — capped at 90 chars
TT = "Still staring at the first line? 5 hooks in 60 seconds. $9/mo — link in bio."


def upload_image(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    r = requests.post(f"{BASE}/media/presign", headers=HEADERS,
        json={"filename": filename, "contentType": "image/png", "fileSize": filesize})
    r.raise_for_status()
    data = r.json()
    with open(filepath, "rb") as f:
        requests.put(data["uploadUrl"], data=f,
            headers={"Content-Type": "image/png"}).raise_for_status()
    return data["publicUrl"]


def main():
    assert len(TT) <= 90, f"TikTok content {len(TT)} chars > 90"
    print(f"TikTok title length: {len(TT)} chars (limit 90)")
    print("Uploading brand card to Zernio...")
    image_url = upload_image(IMAGE)
    print(f"  ✓ {image_url[:70]}...")

    body = {
        "content": LI,
        "mediaItems": [{"url": image_url, "type": "image"}],
        "scheduledFor": SCHEDULED_FOR,
        "timezone": TIMEZONE,
        "isDraft": False,
        "platforms": [
            {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": LI, "scheduledFor": SCHEDULED_FOR,
             "platformSpecificData": {"firstComment": FC}},
            {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": IG, "scheduledFor": SCHEDULED_FOR},
            {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": FB, "scheduledFor": SCHEDULED_FOR,
             "platformSpecificData": {"firstComment": FC}},
            {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": TT, "scheduledFor": SCHEDULED_FOR},
        ],
    }
    print(f"Scheduling for {SCHEDULED_FOR} ET across LI/IG/FB/TT...")
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    if r.status_code in (200, 201):
        pid = r.json().get("post", {}).get("_id") or r.json().get("_id", "?")
        print(f"  ✓ Scheduled. Post ID: {pid}")
    else:
        print(f"  ✗ Failed {r.status_code}: {r.text[:400]}")


if __name__ == "__main__":
    main()
