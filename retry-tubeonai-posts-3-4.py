"""
Retry scheduling posts 3 and 4 from the TubeonAI → Zernio run.
These failed with ERROR:429. Images are already rendered on disk.
Re-uploads images and reschedules.
"""

import os, time, requests
from pathlib import Path
from anthropic import Anthropic

ANTHROPIC_KEY = "***REMOVED-ANTHROPIC-KEY***"
OPENAI_KEY    = "***REMOVED-OPENAI-KEY***"
ZERNIO_KEY    = "***REMOVED-ZERNIO-KEY***"

ZERNIO_BASE  = "https://zernio.com/api/v1"
ZERNIO_HDR   = {"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TIMEZONE     = "America/New_York"

IMAGES_DIR  = Path("/Users/toto/Claude TubeonAI/social-assets/linkedin-may/images")
PROJECT_DIR = Path("/Users/toto/Claude TubeonAI")

anthropic = Anthropic(api_key=ANTHROPIC_KEY)

SYSTEM_PROMPT = """\
You write LinkedIn posts for Crosswalk Wisdom, a brand by Sahawat Nilwatcharamanee — a former physician who left medicine, became a crossing guard, and now helps unmatched IMGs in Canada navigate career transitions.

AUDIENCE: A 34-year-old IMG from India. Passed MCCQE Part 1. Failed CaRMS twice. Working as a lab assistant at $48K/year. Family thinks he's "almost a doctor in Canada." Googles "IMG unmatched career options" at midnight.

STRUCTURE — follow this exactly, every time:
1. HOOK (2 lines max): Status-drop or vulnerability contrast. Creates cognitive dissonance. Pairs a hard truth with a surprising outcome.
2. REFRAME: "The question isn't X. It's Y." — redirect from failure/loss to discovery/gain.
3. SENSORY LIST (✨): 3 short lines. Specific sensory details — Tim Hortons, lab coat, $18,000, midnight Google search, parking lot tears, WhatsApp family chat, CaRMS email, yellow vest.
4. LESSONS LIST (👣): 3 short lines. Lessons as short infinitive phrases.
5. BRAND REVEAL (mid-post only): "I call it Crosswalk Wisdom — [one-line description]."
6. CTA: "5 minutes. 📬 Link in the comments." Never put URLs in the post body.
7. ENGAGEMENT QUESTION: One universal question any professional — not just IMGs — would answer.
8. HASHTAGS: Exactly 4. Always #CrosswalkWisdom #IMGCanada plus 2 contextual.

RULES:
- Never preach. Share what was found.
- Never mention any video, source, or research. Write as lived experience.
- Sensory specifics only — no abstract language.
- Brand reveal mid-story, never in the opening.
- Under 1500 characters total.
- Output ONLY the post. No intro, no explanation, no commentary."""

FAILED_POSTS = [
    {
        "index": 3,
        "slug": "tubeonai-03",
        "slot": "2026-05-19T11:00:00",
        "pillar": "Identity Cage",
        "topic": "The immediate aftermath of failing CaRMS — what to do, what to feel, what actually matters",
        "file": "Didnt Match in CaRMS First Iteration WATCH THIS Be.txt",
        "first_comment": "Here's the Fear Audit — what you're feeling right now has a name. 5 minutes: https://fear-audit.vercel.app",
    },
    {
        "index": 4,
        "slug": "tubeonai-04",
        "slot": "2026-05-19T14:00:00",
        "pillar": "Courage to Choose",
        "topic": "Ontario IMG policy changes — what the system shifting means for the 88% who don't match",
        "file": "Ontarios New IMG Policy What You Need to Know for .txt",
        "first_comment": "Here's the free IMG Reality Calculator — see how the new numbers affect your specific situation: https://crosswalkwisdom.com/calculator",
    },
]


def extract_summary(filepath: str) -> str:
    txt = Path(filepath).read_text()
    lines = txt.split("\n")
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("## LinkedIn Post"):
            start = i + 3
            break
    content = "\n".join(lines[start:])
    return content[:3000].strip()


def write_linkedin_post(summary: str, topic: str) -> str:
    print(f"  Writing post via Claude...")
    msg = anthropic.messages.create(
        model="claude-opus-4-6",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Topic: {topic}\n\nSource insights:\n{summary}\n\nWrite the LinkedIn post now."
        }]
    )
    return msg.content[0].text.strip()


def write_short_copy(linkedin_post: str) -> str:
    msg = anthropic.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"Compress this LinkedIn post into a short 250-300 character Instagram caption keeping the hook and hashtags. Output only the caption.\n\n{linkedin_post}"
        }]
    )
    return msg.content[0].text.strip()


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


def schedule_post(linkedin_copy: str, short_copy: str, image_url: str,
                  scheduled_for: str, first_comment: str) -> str:
    body = {
        "content": linkedin_copy,
        "mediaItems": [{"url": image_url, "type": "image"}],
        "platforms": [
            {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": linkedin_copy,
             "scheduledFor": scheduled_for, "platformSpecificData": {"firstComment": first_comment}},
            {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": short_copy,  "scheduledFor": scheduled_for},
            {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": linkedin_copy, "scheduledFor": scheduled_for},
            {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": short_copy,  "scheduledFor": scheduled_for},
        ],
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
    }
    r = requests.post(f"{ZERNIO_BASE}/posts", headers=ZERNIO_HDR, json=body)
    return r.json().get("post", {}).get("_id", f"ERROR:{r.status_code}")


def main():
    print("=== Retry: TubeonAI posts 3 & 4 ===\n")
    results = []

    for src in FAILED_POSTS:
        print(f"\n{'='*60}")
        print(f"[{src['index']}/6]  {src['slot']}  |  {src['pillar']}")
        print(f"Topic: {src['topic']}")

        summary  = extract_summary(str(PROJECT_DIR / src["file"]))
        linkedin = write_linkedin_post(summary, src["topic"])
        short    = write_short_copy(linkedin)
        print(f"  Post written ({len(linkedin)} chars)")

        final_img = IMAGES_DIR / f"{src['slug']}-final.png"
        print(f"  Re-uploading {final_img.name}...")
        cdn_url = upload_image(final_img)
        print(f"  Uploaded: {cdn_url[:70]}")

        post_id = schedule_post(linkedin, short, cdn_url, src["slot"], src["first_comment"])
        print(f"  Scheduled: {post_id}")

        results.append({"slot": src["slot"], "pillar": src["pillar"], "post_id": post_id})
        time.sleep(3)

    print(f"\n\n{'='*60}")
    print("RETRY RESULTS")
    print(f"{'='*60}")
    for r in results:
        status = "OK" if not r["post_id"].startswith("ERROR") else r["post_id"]
        print(f"  {r['slot']}  {r['pillar']:<25}  {r['post_id']}  [{status}]")
    print()


if __name__ == "__main__":
    main()
