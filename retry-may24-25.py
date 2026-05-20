"""
Retry: Schedule the 5 missing posts from schedule-may19-24.py run.
Indices 25-29 (slugs may-32 through may-36) were not processed.
Slots: May 24 11:00/14:00/17:00/20:00 and May 25 08:00 (America/New_York)
"""

from __future__ import annotations
import os, re, time, json, subprocess, requests
from pathlib import Path
from anthropic import Anthropic

# ── Config ─────────────────────────────────────────────────────────────────────
ANTHROPIC_KEY = "***REMOVED-ANTHROPIC-KEY***"
OPENAI_KEY    = "***REMOVED-OPENAI-KEY***"
ZERNIO_KEY    = "***REMOVED-ZERNIO-KEY***"

ZERNIO_BASE  = "https://zernio.com/api/v1"
ZERNIO_HDR   = {"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"}
OPENAI_HDR   = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TIMEZONE     = "America/New_York"

IMAGES_DIR = Path("/Users/toto/Claude TubeonAI/social-assets/linkedin-may/images")
HTML_DIR   = Path("/Users/toto/Claude TubeonAI/social-assets/linkedin-may")

IMAGES_DIR.mkdir(parents=True, exist_ok=True)

anthropic = Anthropic(api_key=ANTHROPIC_KEY)

# ── Missing slots (indices 25-29 from original script) ─────────────────────────
MISSING = [
    {
        "slug": "may-32",
        "slot": "2026-05-24T11:00:00",
        "topic": "The calm after the crossing — why peace feels unfamiliar when you have been in survival mode for years",
        "pillar": "Crossing Guard Philosophy",
        "first_comment": "This is where Crosswalk Wisdom starts. If the crosswalk is calling you: https://crosswalkwisdom.com/start",
        "image_prompt": "Person sitting on steps outside in late afternoon sun, eyes closed, relaxed posture, warm golden light on face, crosswalk in background, cinematic 35mm film grain, earned stillness, close-up portrait",
    },
    {
        "slug": "may-33",
        "slot": "2026-05-24T14:00:00",
        "topic": "The parking lot cry after a CaRMS rejection — what it means and what the person who had it went on to do",
        "pillar": "Identity Cage",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
        "image_prompt": "Empty hospital parking lot at dusk, single car, person sitting inside with head resting on steering wheel, amber parking lot lights, cinematic 35mm film grain, emotional privacy, cinematic wide shot",
    },
    {
        "slug": "may-34",
        "slot": "2026-05-24T17:00:00",
        "topic": "4 non-clinical roles unmatched IMGs in Canada can start applying for this week — with salary ranges",
        "pillar": "Courage to Choose",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
        "image_prompt": "Confident professional walking into a modern office building, business casual attire, briefcase, glass doors, morning light, cinematic 35mm film grain, forward momentum, sense of new beginning",
    },
    {
        "slug": "may-35",
        "slot": "2026-05-24T20:00:00",
        "topic": "The crosswalk moment — the exact point when an IMG stops waiting for permission and starts crossing",
        "pillar": "Crossing Guard Philosophy",
        "first_comment": "This is where Crosswalk Wisdom starts. If the crosswalk is calling you: https://crosswalkwisdom.com/start",
        "image_prompt": "Person mid-step crossing a crosswalk in early morning light, looking forward not back, amber sunrise ahead, motion slightly blurred, cinematic 35mm film grain, decisive and free, hopeful energy",
    },
    {
        "slug": "may-36",
        "slot": "2026-05-25T08:00:00",
        "topic": "What the free IMG calculator revealed — the number that finally made 300 people choose to cross",
        "pillar": "Courage to Choose",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
        "image_prompt": "Person looking at a smartphone screen, slight relief and recognition on their face, warm interior lighting, sitting at a kitchen table, cinematic 35mm film grain, moment of clarity, shallow depth of field",
    },
]

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


def write_linkedin_post(topic: str, pillar: str) -> str:
    print(f"  Writing post via Claude...")
    context = (
        f"Topic: {topic}\n\n"
        f"Content pillar: {pillar}\n\n"
        f"Write this post entirely as Sahawat's lived experience — "
        f"draw from his journey as an IMG who failed CaRMS, worked as a crossing guard, "
        f"and founded Crosswalk Wisdom. Make the sensory details feel real and specific."
    )
    msg = anthropic.messages.create(
        model="claude-opus-4-6",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": context}]
    )
    return msg.content[0].text.strip()


def write_short_copy(linkedin_post: str) -> str:
    msg = anthropic.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                "Compress this LinkedIn post into a short 250-300 character Instagram caption "
                "keeping the hook and hashtags. Output only the caption.\n\n" + linkedin_post
            )
        }]
    )
    return msg.content[0].text.strip()


def generate_image(prompt: str, filename: str) -> Path:
    print(f"  Generating image via DALL-E...")
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=OPENAI_HDR,
        json={"model": "dall-e-3", "prompt": prompt, "n": 1, "size": "1024x1024",
              "quality": "standard", "response_format": "url"}
    )
    r.raise_for_status()
    img_url = r.json()["data"][0]["url"]
    path = IMAGES_DIR / filename
    img_data = requests.get(img_url).content
    path.write_bytes(img_data)
    print(f"  Image saved: {path.name} ({len(img_data)//1024}KB)")
    return path


def extract_hook(post: str) -> tuple[str, str]:
    lines = [l.strip() for l in post.split("\n") if l.strip()]
    h1 = lines[0] if lines else "Crosswalk Wisdom"
    h2 = lines[1] if len(lines) > 1 else ""
    return h1, h2


def extract_sub(post: str) -> str:
    lines = [l.strip() for l in post.split("\n") if l.strip()]
    return lines[2] if len(lines) > 2 else ""


def write_html(slug: str, img_filename: str, hook1: str, hook2: str, sub: str, tag: str) -> Path:
    def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', '&quot;')
    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1080px; height:1080px; overflow:hidden; }}
.card {{ width:1080px; height:1080px; position:relative; background-image:url('./images/{img_filename}'); background-size:cover; background-position:center; display:flex; flex-direction:column; justify-content:flex-end; }}
.overlay {{ position:absolute; inset:0; background:linear-gradient(to top, rgba(18,14,10,0.96) 0%, rgba(18,14,10,0.78) 40%, rgba(18,14,10,0.30) 75%, rgba(18,14,10,0.10) 100%); }}
.accent {{ position:absolute; top:0; left:0; bottom:0; width:4px; background:linear-gradient(180deg, rgba(212,168,67,0.15) 0%, #D4A843 40%, rgba(212,168,67,0.2) 100%); }}
.content {{ position:relative; z-index:2; padding:0 88px 72px 92px; }}
.tag {{ display:inline-block; font-family:'Inter',sans-serif; font-size:11px; font-weight:700; letter-spacing:0.2em; text-transform:uppercase; color:#D4A843; background:rgba(212,168,67,0.12); border:1px solid rgba(212,168,67,0.3); padding:7px 16px; border-radius:2px; margin-bottom:32px; }}
.hook {{ font-family:'Playfair Display',Georgia,serif; font-size:50px; font-weight:900; line-height:1.1; color:#FAF7F2; margin-bottom:20px; max-width:860px; }}
.hook em {{ font-style:italic; color:#D4A843; }}
.sub {{ font-family:'Inter',sans-serif; font-size:19px; font-weight:400; color:rgba(250,247,242,0.55); line-height:1.5; max-width:680px; margin-bottom:44px; }}
.divider {{ width:48px; height:2px; background:rgba(212,168,67,0.4); margin-bottom:32px; }}
.bottom {{ display:flex; align-items:center; justify-content:space-between; }}
.brand {{ font-family:'Playfair Display',Georgia,serif; font-size:18px; font-weight:700; color:rgba(212,168,67,0.7); }}
.author {{ font-family:'Inter',sans-serif; font-size:13px; color:rgba(250,247,242,0.3); }}
</style></head>
<body><div class="card">
  <div class="overlay"></div><div class="accent"></div>
  <div class="content">
    <div class="tag">{esc(tag)}</div>
    <div class="hook">{esc(hook1)}<br><em>{esc(hook2)}</em></div>
    <div class="divider"></div>
    <div class="sub">{esc(sub)}</div>
    <div class="bottom">
      <span class="brand">Crosswalk Wisdom</span>
      <span class="author">Sahawat — IMG, Crossing Guard, Founder</span>
    </div>
  </div>
</div></body></html>"""
    path = HTML_DIR / f"{slug}.html"
    path.write_text(html)
    return path


def render_png(html_file: Path, out_png: Path) -> Path:
    print(f"  Rendering PNG...")
    result = subprocess.run(
        ["shot-scraper", str(html_file), "-o", str(out_png),
         "--width", "1080", "--height", "1080"],
        cwd=str(HTML_DIR), capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"shot-scraper failed: {result.stderr}")
    return out_png


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
            {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": short_copy,
             "scheduledFor": scheduled_for},
            {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": linkedin_copy,
             "scheduledFor": scheduled_for},
            {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": short_copy,
             "scheduledFor": scheduled_for},
        ],
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
    }
    r = requests.post(f"{ZERNIO_BASE}/posts", headers=ZERNIO_HDR, json=body)
    return r.json().get("post", {}).get("_id", f"ERROR:{r.status_code}:{r.text[:80]}")


def main():
    print("=== Crosswalk Wisdom — Retry May 24-25 (5 missing posts) ===\n")
    results = []

    for i, src in enumerate(MISSING):
        slug = src["slug"]
        img_raw   = f"{slug}-raw.png"
        img_final = f"{slug}-final.png"

        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(MISSING)}]  {src['slot']}  |  {src['pillar']}")
        print(f"Topic: {src['topic'][:80]}...")

        linkedin = write_linkedin_post(src["topic"], src["pillar"])
        short    = write_short_copy(linkedin)
        print(f"  Post written ({len(linkedin)} chars)")

        raw_path = generate_image(src["image_prompt"], img_raw)

        h1, h2  = extract_hook(linkedin)
        sub     = extract_sub(linkedin)
        html_f  = write_html(slug, img_raw, h1, h2, sub, src["pillar"])
        final_p = IMAGES_DIR / img_final
        render_png(html_f, final_p)
        print(f"  PNG rendered: {img_final}")

        cdn_url = upload_image(final_p)
        print(f"  Uploaded: {cdn_url[:70]}")

        post_id = schedule_post(linkedin, short, cdn_url, src["slot"], src["first_comment"])
        print(f"  Scheduled: {post_id}")

        results.append({
            "slot": src["slot"], "pillar": src["pillar"],
            "post_id": post_id, "cdn_url": cdn_url,
        })

        time.sleep(2)

    print(f"\n\n{'='*60}")
    print("RETRY RESULTS")
    print(f"{'='*60}")
    for r in results:
        status = "OK" if not r["post_id"].startswith("ERROR") else "FAIL"
        print(f"  [{status}]  {r['slot']}  {r['pillar']:<30}  {r['post_id'][:30]}")

    ok = sum(1 for r in results if not r["post_id"].startswith("ERROR"))
    print(f"\nDone. {ok}/{len(results)} posts scheduled.\n")


if __name__ == "__main__":
    main()
