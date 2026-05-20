"""
Retry script: schedules the 8 posts that failed in schedule-may19-24.py
  - Posts 2, 3, 8  → PNGs already rendered; re-upload + re-schedule
  - Posts 26-30    → generate new images + full pipeline
"""
from __future__ import annotations
import time, json, subprocess, requests
from pathlib import Path
from anthropic import Anthropic

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

anthropic = Anthropic(api_key=ANTHROPIC_KEY)

FC_FEAR  = "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app"
FC_START = "This is where Crosswalk Wisdom starts. If the crosswalk is calling you: https://crosswalkwisdom.com/start"
FC_CALC  = "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator"

SYSTEM_PROMPT = """\
You write LinkedIn posts for Crosswalk Wisdom, a brand by Sahawat Nilwatcharamanee — a former physician who left medicine, became a crossing guard, and now helps unmatched IMGs in Canada navigate career transitions.

AUDIENCE: A 34-year-old IMG from India. Passed MCCQE Part 1. Failed CaRMS twice. Working as a lab assistant at $48K/year. Family thinks he's "almost a doctor in Canada." Googles "IMG unmatched career options" at midnight.

STRUCTURE — follow this exactly, every time:
1. HOOK (2 lines max): Status-drop or vulnerability contrast. Creates cognitive dissonance.
2. REFRAME: "The question isn't X. It's Y." — redirect from failure/loss to discovery/gain.
3. SENSORY LIST (✨): 3 short lines. Specific sensory details — Tim Hortons, lab coat, $18,000, midnight Google search, parking lot tears, WhatsApp family chat, CaRMS email, yellow vest.
4. LESSONS LIST (👣): 3 short lines. Lessons as short infinitive phrases.
5. BRAND REVEAL (mid-post only): "I call it Crosswalk Wisdom — [one-line description]."
6. CTA: "5 minutes. 📬 Link in the comments." Never put URLs in the post body.
7. ENGAGEMENT QUESTION: One universal question any professional would answer.
8. HASHTAGS: Exactly 4. Always #CrosswalkWisdom #IMGCanada plus 2 contextual.

RULES: Never preach. Write as lived experience. No abstract language. Under 1500 characters total. Output ONLY the post."""

# ── Posts to retry ─────────────────────────────────────────────────────────────
# existing_png = True → skip image generation, re-upload the existing file
RETRY_POSTS = [
    # ── Already have PNGs — just re-upload + reschedule ────────────────────────
    {
        "slug": "may-08", "existing_png": True,
        "slot": "2026-05-19T14:00:00",
        "topic": "The WhatsApp family group lie — what unmatched IMGs tell their parents vs. what they feel at midnight",
        "pillar": "Identity Cage", "first_comment": FC_FEAR,
    },
    {
        "slug": "may-09", "existing_png": True,
        "slot": "2026-05-19T17:00:00",
        "topic": "Clinical research in Canada for IMGs — a $75K career path that doesn't require residency",
        "pillar": "Courage to Choose", "first_comment": FC_CALC,
    },
    {
        "slug": "may-14", "existing_png": True,
        "slot": "2026-05-20T17:00:00",
        "topic": "The $48K salary slip — what no one tells unmatched IMGs about income while they wait for residency",
        "pillar": "Identity Cage", "first_comment": FC_FEAR,
    },
    # ── Need fresh image + full pipeline ───────────────────────────────────────
    {
        "slug": "may-32", "existing_png": False,
        "slot": "2026-05-24T11:00:00",
        "topic": "The calm after the crossing — why peace feels unfamiliar when you have been in survival mode for years",
        "pillar": "Crossing Guard Philosophy", "first_comment": FC_START,
        "image_prompt": "Person sitting alone on outdoor steps at golden hour, warm amber sunlight, relaxed hands in lap, crosswalk visible in background, cinematic 35mm film grain, quiet contentment after long struggle",
    },
    {
        "slug": "may-33", "existing_png": False,
        "slot": "2026-05-24T14:00:00",
        "topic": "The parking lot cry after a CaRMS rejection — what it means and what the person who had it went on to do",
        "pillar": "Identity Cage", "first_comment": FC_FEAR,
        "image_prompt": "Empty hospital parking lot at dusk, single car with figure visible inside, amber overhead lights just turning on, cinematic 35mm film grain, wide establishing shot, quiet emotional weight",
    },
    {
        "slug": "may-34", "existing_png": False,
        "slot": "2026-05-24T17:00:00",
        "topic": "4 non-clinical roles unmatched IMGs in Canada can start applying for this week — with salary ranges",
        "pillar": "Courage to Choose", "first_comment": FC_CALC,
        "image_prompt": "Confident South Asian professional in smart casual attire walking toward modern office building entrance, morning light, glass doors, cinematic 35mm film grain, forward momentum, new beginning",
    },
    {
        "slug": "may-35", "existing_png": False,
        "slot": "2026-05-24T20:00:00",
        "topic": "The crosswalk moment — the exact point when an IMG stops waiting for permission and starts crossing",
        "pillar": "Crossing Guard Philosophy", "first_comment": FC_START,
        "image_prompt": "Person mid-stride on a crosswalk at sunrise, looking forward, amber morning light ahead, motion slightly captured, cinematic 35mm film grain, decisive and free, wide shot",
    },
    {
        "slug": "may-36", "existing_png": False,
        "slot": "2026-05-25T08:00:00",
        "topic": "What the free IMG Reality Calculator revealed — the number that made 300 people finally choose to cross",
        "pillar": "Courage to Choose", "first_comment": FC_CALC,
        "image_prompt": "Person at a kitchen table looking at a laptop screen with quiet relief, warm morning light through window, coffee cup nearby, cinematic 35mm film grain, moment of clarity, shallow depth of field",
    },
]


def write_post(topic: str, pillar: str) -> str:
    msg = anthropic.messages.create(
        model="claude-opus-4-7", max_tokens=800, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": (
            f"Topic: {topic}\nPillar: {pillar}\n\n"
            "Write this post as Sahawat's lived experience — former IMG, former crossing guard, founder of Crosswalk Wisdom."
        )}]
    )
    return msg.content[0].text.strip()


def write_short(post: str) -> str:
    msg = anthropic.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=300,
        messages=[{"role": "user", "content":
            "Compress this LinkedIn post into a 250-300 character Instagram caption keeping the hook and hashtags. Output only the caption.\n\n" + post
        }]
    )
    return msg.content[0].text.strip()


def generate_image(prompt: str, filename: str) -> Path:
    r = requests.post(
        "https://api.openai.com/v1/images/generations", headers=OPENAI_HDR,
        json={"model": "dall-e-3", "prompt": prompt, "n": 1, "size": "1024x1024",
              "quality": "standard", "response_format": "url"}
    )
    r.raise_for_status()
    img_url = r.json()["data"][0]["url"]
    path = IMAGES_DIR / filename
    path.write_bytes(requests.get(img_url).content)
    print(f"  Image: {filename} ({path.stat().st_size // 1024}KB)")
    return path


def extract_hook(post: str):
    lines = [l.strip() for l in post.split("\n") if l.strip()]
    return (lines[0] if lines else "Crosswalk Wisdom",
            lines[1] if len(lines) > 1 else "")


def extract_sub(post: str) -> str:
    lines = [l.strip() for l in post.split("\n") if l.strip()]
    return lines[2] if len(lines) > 2 else ""


def write_html(slug: str, img_filename: str, h1: str, h2: str, sub: str, tag: str) -> Path:
    def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace('"','&quot;')
    html = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;overflow:hidden}}
.card{{width:1080px;height:1080px;position:relative;background-image:url('./images/{img_filename}');background-size:cover;background-position:center;display:flex;flex-direction:column;justify-content:flex-end}}
.overlay{{position:absolute;inset:0;background:linear-gradient(to top,rgba(18,14,10,.96) 0%,rgba(18,14,10,.78) 40%,rgba(18,14,10,.30) 75%,rgba(18,14,10,.10) 100%)}}
.accent{{position:absolute;top:0;left:0;bottom:0;width:4px;background:linear-gradient(180deg,rgba(212,168,67,.15) 0%,#D4A843 40%,rgba(212,168,67,.2) 100%)}}
.content{{position:relative;z-index:2;padding:0 88px 72px 92px}}
.tag{{display:inline-block;font-family:'Inter',sans-serif;font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:#D4A843;background:rgba(212,168,67,.12);border:1px solid rgba(212,168,67,.3);padding:7px 16px;border-radius:2px;margin-bottom:32px}}
.hook{{font-family:'Playfair Display',Georgia,serif;font-size:50px;font-weight:900;line-height:1.1;color:#FAF7F2;margin-bottom:20px;max-width:860px}}
.hook em{{font-style:italic;color:#D4A843}}
.sub{{font-family:'Inter',sans-serif;font-size:19px;font-weight:400;color:rgba(250,247,242,.55);line-height:1.5;max-width:680px;margin-bottom:44px}}
.divider{{width:48px;height:2px;background:rgba(212,168,67,.4);margin-bottom:32px}}
.bottom{{display:flex;align-items:center;justify-content:space-between}}
.brand{{font-family:'Playfair Display',Georgia,serif;font-size:18px;font-weight:700;color:rgba(212,168,67,.7)}}
.author{{font-family:'Inter',sans-serif;font-size:13px;color:rgba(250,247,242,.3)}}
</style></head>
<body><div class="card">
<div class="overlay"></div><div class="accent"></div>
<div class="content">
<div class="tag">{esc(tag)}</div>
<div class="hook">{esc(h1)}<br><em>{esc(h2)}</em></div>
<div class="divider"></div>
<div class="sub">{esc(sub)}</div>
<div class="bottom">
<span class="brand">Crosswalk Wisdom</span>
<span class="author">Sahawat — IMG, Crossing Guard, Founder</span>
</div></div></div></body></html>"""
    path = HTML_DIR / f"{slug}.html"
    path.write_text(html)
    return path


def render_png(html_file: Path, out_png: Path) -> Path:
    r = subprocess.run(
        ["shot-scraper", str(html_file), "-o", str(out_png), "--width", "1080", "--height", "1080"],
        cwd=str(HTML_DIR), capture_output=True, text=True
    )
    if r.returncode != 0:
        raise RuntimeError(f"shot-scraper: {r.stderr}")
    return out_png


def upload_image(filepath: Path) -> str:
    r = requests.post(f"{ZERNIO_BASE}/media/presign", headers=ZERNIO_HDR,
        json={"filename": filepath.name, "contentType": "image/png",
              "fileSize": filepath.stat().st_size})
    r.raise_for_status()
    d = r.json()
    with open(filepath, "rb") as f:
        requests.put(d["uploadUrl"], data=f, headers={"Content-Type": "image/png"}).raise_for_status()
    return d["publicUrl"]


def schedule_post(linkedin: str, short: str, img_url: str, slot: str, fc: str) -> str:
    body = {
        "content": linkedin,
        "mediaItems": [{"url": img_url, "type": "image"}],
        "platforms": [
            {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": linkedin,
             "scheduledFor": slot, "platformSpecificData": {"firstComment": fc}},
            {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": short, "scheduledFor": slot},
            {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": linkedin, "scheduledFor": slot},
            {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": short, "scheduledFor": slot},
        ],
        "scheduledFor": slot,
        "timezone": TIMEZONE,
    }
    r = requests.post(f"{ZERNIO_BASE}/posts", headers=ZERNIO_HDR, json=body)
    return r.json().get("post", {}).get("_id", f"ERROR:{r.status_code}:{r.text[:100]}")


def main():
    print("=== Retry: 8 failed posts ===\n")
    results = []

    for i, src in enumerate(RETRY_POSTS):
        slug = src["slug"]
        print(f"\n[{i+1}/{len(RETRY_POSTS)}]  {src['slot']}  |  {src['pillar']}")
        print(f"  {src['topic'][:75]}...")

        # 1. Write LinkedIn post
        print("  Writing post...")
        linkedin = write_post(src["topic"], src["pillar"])
        short    = write_short(linkedin)
        print(f"  Post: {len(linkedin)} chars")

        # 2. Image: reuse existing PNG or generate new
        final_png = IMAGES_DIR / f"{slug}-final.png"

        if src["existing_png"]:
            print(f"  Reusing existing PNG: {slug}-final.png")
            # Re-render HTML with fresh post text (hook may differ)
            raw_file = f"{slug}-raw.png"
            h1, h2 = extract_hook(linkedin)
            sub    = extract_sub(linkedin)
            html_f = write_html(slug, raw_file, h1, h2, sub, src["pillar"])
            render_png(html_f, final_png)
            print(f"  PNG re-rendered")
        else:
            # Full generation
            raw_png = IMAGES_DIR / f"{slug}-raw.png"
            generate_image(src["image_prompt"], f"{slug}-raw.png")
            h1, h2 = extract_hook(linkedin)
            sub    = extract_sub(linkedin)
            html_f = write_html(slug, f"{slug}-raw.png", h1, h2, sub, src["pillar"])
            render_png(html_f, final_png)
            print(f"  PNG rendered: {slug}-final.png")

        # 3. Upload + schedule (with delay to avoid 429)
        time.sleep(8)
        cdn_url = upload_image(final_png)
        print(f"  Uploaded: {cdn_url[:70]}")

        time.sleep(5)
        post_id = schedule_post(linkedin, short, cdn_url, src["slot"], src["first_comment"])
        status  = "OK" if not post_id.startswith("ERROR") else "FAIL"
        print(f"  [{status}] Scheduled: {post_id[:50]}")

        results.append({"slot": src["slot"], "pillar": src["pillar"], "id": post_id, "status": status})
        time.sleep(10)

    print(f"\n\n{'='*60}")
    print("RETRY RESULTS")
    print(f"{'='*60}")
    ok = 0
    for r in results:
        print(f"  [{r['status']}]  {r['slot']}  {r['pillar']:<30}  {r['id'][:30]}")
        if r["status"] == "OK":
            ok += 1
    print(f"\n{ok}/{len(results)} posts scheduled.\n")


if __name__ == "__main__":
    main()
