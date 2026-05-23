"""
Retry: Schedule the 2 failed posts (may-33 and may-34) from the retry run.
Images are already rendered. Just re-upload and schedule.
"""

import os
import requests, time
from pathlib import Path
from anthropic import Anthropic

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
ZERNIO_KEY    = os.getenv("ZERNIO_KEY")

ZERNIO_BASE   = "https://zernio.com/api/v1"
ZERNIO_HDR    = {"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID   = "690940455f6fbb9ef8323070"
INSTAGRAM_ID  = "690940655f6fbb9ef8323072"
FACEBOOK_ID   = "6909409a5f6fbb9ef8323074"
TIKTOK_ID     = "690941425f6fbb9ef8323078"
TIMEZONE      = "America/New_York"

IMAGES_DIR    = Path("/Users/toto/Claude TubeonAI/social-assets/linkedin-may/images")

anthropic = Anthropic(api_key=ANTHROPIC_KEY)

MISSING = [
    {
        "slug": "may-33",
        "slot": "2026-05-24T14:00:00",
        "topic": "The parking lot cry after a CaRMS rejection — what it means and what the person who had it went on to do",
        "pillar": "Identity Cage",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
    {
        "slug": "may-34",
        "slot": "2026-05-24T17:00:00",
        "topic": "4 non-clinical roles unmatched IMGs in Canada can start applying for this week — with salary ranges",
        "pillar": "Courage to Choose",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: www.crosswalkwisdom.com/img/calculator",
    },
]

SYSTEM_PROMPT = """\
You write LinkedIn posts for Crosswalk Wisdom, a brand by Sahawat Nilwatcharamanee — a former physician who left medicine, became a crossing guard, and now helps unmatched IMGs in Canada navigate career transitions.

AUDIENCE: A 34-year-old IMG from India. Passed MCCQE Part 1. Failed CaRMS twice. Working as a lab assistant at $48K/year. Family thinks he's "almost a doctor in Canada." Googles "IMG unmatched career options" at midnight.

STRUCTURE — follow this exactly, every time:
1. HOOK (2 lines max): Status-drop or vulnerability contrast.
2. REFRAME: "The question isn't X. It's Y."
3. SENSORY LIST (✨): 3 short lines. Specific sensory details.
4. LESSONS LIST (👣): 3 short lines.
5. BRAND REVEAL (mid-post only): "I call it Crosswalk Wisdom — [one-line description]."
6. CTA: "5 minutes. 📬 Link in the comments."
7. ENGAGEMENT QUESTION
8. HASHTAGS: Exactly 4. Always #CrosswalkWisdom #IMGCanada plus 2 contextual.

Under 1500 characters. Output ONLY the post."""


def upload_image(filepath: Path) -> str:
    fname = filepath.name
    fsize = filepath.stat().st_size
    r = requests.post(f"{ZERNIO_BASE}/media/presign", headers=ZERNIO_HDR,
        json={"filename": fname, "contentType": "image/png", "fileSize": fsize})
    r.raise_for_status()
    d = r.json()
    with open(filepath, "rb") as f:
        requests.put(d["uploadUrl"], data=f, headers={"Content-Type": "image/png"}).raise_for_status()
    return d["publicUrl"]


def main():
    print("=== Retry: may-33 and may-34 ===\n")

    for src in MISSING:
        print(f"\n{src['slug']}  |  {src['slot']}  |  {src['pillar']}")

        msg = anthropic.messages.create(
            model="claude-opus-4-6",
            max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": (
                f"Topic: {src['topic']}\nPillar: {src['pillar']}\n"
                "Write the post as Sahawat's lived experience."
            )}]
        )
        linkedin = msg.content[0].text.strip()

        msg2 = anthropic.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": (
                "Compress to 250-300 char Instagram caption, keep hook and hashtags:\n\n" + linkedin
            )}]
        )
        short = msg2.content[0].text.strip()
        print(f"  Post written ({len(linkedin)} chars)")

        final_p = IMAGES_DIR / f"{src['slug']}-final.png"
        cdn_url = upload_image(final_p)
        print(f"  Uploaded: {cdn_url[:70]}")

        body = {
            "content": linkedin,
            "mediaItems": [{"url": cdn_url, "type": "image"}],
            "platforms": [
                {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": linkedin,
                 "scheduledFor": src["slot"], "platformSpecificData": {"firstComment": src["first_comment"]}},
                {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": short,
                 "scheduledFor": src["slot"]},
                {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": linkedin,
                 "scheduledFor": src["slot"]},
                {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": short,
                 "scheduledFor": src["slot"]},
            ],
            "scheduledFor": src["slot"],
            "timezone": TIMEZONE,
        }
        r = requests.post(f"{ZERNIO_BASE}/posts", headers=ZERNIO_HDR, json=body)
        post_id = r.json().get("post", {}).get("_id", f"ERROR:{r.status_code}:{r.text[:80]}")
        status = "OK" if not post_id.startswith("ERROR") else "FAIL"
        print(f"  [{status}] {post_id}")

        time.sleep(3)


if __name__ == "__main__":
    main()
