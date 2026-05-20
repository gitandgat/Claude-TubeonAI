"""
Claude → DALL-E → shot-scraper → Zernio
May 19 11am through May 24 (29 slots, 5 posts/day)

Generates posts directly from topic descriptions — no TubeonAI file needed.
Claude writes in Crosswalk Wisdom voice from lived IMG experience.
"""

from __future__ import annotations
import os, re, time, json, subprocess, textwrap, requests
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

# ── Schedule slots: May 19 11am → May 24 ──────────────────────────────────────
SLOTS = [
    # May 19 (remaining 4)
    "2026-05-19T11:00:00", "2026-05-19T14:00:00",
    "2026-05-19T17:00:00", "2026-05-19T20:00:00",
    # May 20 (5)
    "2026-05-20T08:00:00", "2026-05-20T11:00:00", "2026-05-20T14:00:00",
    "2026-05-20T17:00:00", "2026-05-20T20:00:00",
    # May 21 (5)
    "2026-05-21T08:00:00", "2026-05-21T11:00:00", "2026-05-21T14:00:00",
    "2026-05-21T17:00:00", "2026-05-21T20:00:00",
    # May 22 (5)
    "2026-05-22T08:00:00", "2026-05-22T11:00:00", "2026-05-22T14:00:00",
    "2026-05-22T17:00:00", "2026-05-22T20:00:00",
    # May 23 (5)
    "2026-05-23T08:00:00", "2026-05-23T11:00:00", "2026-05-23T14:00:00",
    "2026-05-23T17:00:00", "2026-05-23T20:00:00",
    # May 24 (5)
    "2026-05-24T08:00:00", "2026-05-24T11:00:00", "2026-05-24T14:00:00",
    "2026-05-24T17:00:00", "2026-05-24T20:00:00",
    # May 25 (1 — bonus)
    "2026-05-25T08:00:00",
]

FC_FEAR   = "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app"
FC_START  = "This is where Crosswalk Wisdom starts. If the crosswalk is calling you: https://crosswalkwisdom.com/start"
FC_CALC   = "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator"

SOURCE_FILES = [
    # ── May 19 ──────────────────────────────────────────────────────────────────
    {
        "topic": "The moment you stop calling yourself 'Doctor' — what that silence costs an IMG and what it opens",
        "pillar": "Identity Cage",
        "first_comment": FC_FEAR,
        "image_prompt": "Young South Asian man in business casual clothes at a coffee shop, hesitating to write his name tag, pen in hand, warm amber lighting, cinematic 35mm film grain, shallow depth of field, quiet emotional weight",
    },
    {
        "topic": "The WhatsApp family group lie — what unmatched IMGs tell their parents vs. what they feel at midnight",
        "pillar": "Identity Cage",
        "first_comment": FC_FEAR,
        "image_prompt": "Person lying in bed in the dark, phone screen illuminating their face, WhatsApp chat visible, city lights outside the window, cinematic 35mm film grain, moody blue-amber contrast, emotional isolation",
    },
    {
        "topic": "Clinical research in Canada for IMGs — a $75K career path that doesn't require residency",
        "pillar": "Courage to Choose",
        "first_comment": FC_CALC,
        "image_prompt": "Young South Asian professional in smart casual clothes reviewing data on a laptop in a bright modern office, warm natural light, cinematic 35mm film grain, focused and calm, sense of quiet success",
    },
    {
        "topic": "The CaRMS rank order list — how a number defines an IMG's worth and why that's the cruelest part",
        "pillar": "Identity Cage",
        "first_comment": FC_FEAR,
        "image_prompt": "Computer screen showing a numbered list in a dark room, hands on keyboard, tense posture, cold blue monitor light against warm amber background, cinematic 35mm film grain, dread and anticipation",
    },
    # ── May 20 ──────────────────────────────────────────────────────────────────
    {
        "topic": "What a yellow safety vest taught me about professional identity — losing a title, finding a self",
        "pillar": "Crossing Guard Philosophy",
        "first_comment": FC_START,
        "image_prompt": "Man in a bright yellow safety vest standing at an empty crosswalk at sunrise, fog in the background, amber morning light, cinematic 35mm film grain, peaceful solitude, wide shot",
    },
    {
        "topic": "Medical writing for IMGs: how to use your MD to land your first contract in 90 days",
        "pillar": "Courage to Choose",
        "first_comment": FC_CALC,
        "image_prompt": "Young professional writing at a standing desk by a large window, morning light, coffee nearby, laptop open, calm productive atmosphere, cinematic 35mm film grain, warm tones",
    },
    {
        "topic": "The crosswalk paradox: why stopping on purpose is the bravest thing an unmatched IMG can do",
        "pillar": "Crossing Guard Philosophy",
        "first_comment": FC_START,
        "image_prompt": "Person standing still at a busy intersection while people rush past them in motion blur, calm in the chaos, amber streetlights, cinematic 35mm film grain, contemplative mood",
    },
    {
        "topic": "The $48K salary slip — what no one tells unmatched IMGs about income while they wait for residency",
        "pillar": "Identity Cage",
        "first_comment": FC_FEAR,
        "image_prompt": "Close-up of a pay stub on a kitchen table, half-eaten Tim Hortons coffee cup nearby, warm kitchen lamp light, cinematic 35mm film grain, quiet domestic reality, shallow depth of field",
    },
    {
        "topic": "The ROI calculation: 3 more CaRMS cycles vs. one career pivot — what the math actually says",
        "pillar": "Courage to Choose",
        "first_comment": FC_CALC,
        "image_prompt": "Person doing calculations on a notepad at a late-night desk, phone beside them, warm lamp light, papers spread out, cinematic 35mm film grain, quiet determination, shallow depth of field",
    },
    # ── May 21 ──────────────────────────────────────────────────────────────────
    {
        "topic": "The identity grief of not matching CaRMS — it is not failure, it is mourning a version of yourself",
        "pillar": "Identity Cage",
        "first_comment": FC_FEAR,
        "image_prompt": "Person sitting quietly on a park bench in autumn, fallen leaves around them, looking into the distance, warm golden light, cinematic 35mm film grain, melancholy but not hopeless, wide shot",
    },
    {
        "topic": "What the kid crossing the road every morning taught me about trust — a Crosswalk Wisdom reflection",
        "pillar": "Crossing Guard Philosophy",
        "first_comment": FC_START,
        "image_prompt": "Crossing guard helping a child cross a street in early morning light, warm amber sunrise, safety vest, caring gesture, cinematic 35mm film grain, tender moment, shallow depth of field",
    },
    {
        "topic": "Pharmaceutical industry jobs IMGs can apply for this month — no residency, no certification needed",
        "pillar": "Courage to Choose",
        "first_comment": FC_CALC,
        "image_prompt": "Modern pharmaceutical office lobby, professional in smart casual attire walking confidently, glass walls, warm interior lighting, cinematic 35mm film grain, sense of entry and possibility",
    },
    {
        "topic": "Why IMGs stay stuck: the 6 mental blocks that keep them applying to CaRMS past the point of return",
        "pillar": "Identity Cage",
        "first_comment": FC_FEAR,
        "image_prompt": "Person standing in front of a maze entrance at dusk, amber light filtering through, looking at multiple paths, cinematic 35mm film grain, contemplative and slightly overwhelmed, rear view",
    },
    {
        "topic": "Morning rush and midnight Google searches — two kinds of waiting, only one moves you forward",
        "pillar": "Crossing Guard Philosophy",
        "first_comment": FC_START,
        "image_prompt": "Split image feeling: crossing guard in morning rush on the left, person at laptop late at night on the right, amber tones both sides, cinematic 35mm film grain, contrast of stillness and anxiety",
    },
    {
        "topic": "How to reframe your medical CV for non-clinical roles in Canada — what recruiters actually look for",
        "pillar": "Courage to Choose",
        "first_comment": FC_CALC,
        "image_prompt": "Person reviewing and editing a resume at a clean modern desk, warm afternoon light, focused expression, coffee cup nearby, cinematic 35mm film grain, professional energy, shallow depth of field",
    },
    # ── May 22 ──────────────────────────────────────────────────────────────────
    {
        "topic": "When your parents fly from India and you still cannot explain why you are 'still waiting' in Canada",
        "pillar": "Identity Cage",
        "first_comment": FC_FEAR,
        "image_prompt": "Airport arrivals terminal, elderly South Asian couple looking around hopefully, adult child standing awkwardly nearby, warm airport lighting, cinematic 35mm film grain, emotional weight, shallow depth of field",
    },
    {
        "topic": "Stopping traffic on purpose — why choosing to pause your career loop is not giving up",
        "pillar": "Crossing Guard Philosophy",
        "first_comment": FC_START,
        "image_prompt": "Crossing guard holding a stop sign with quiet authority, cars paused, clear morning light, amber vest, confident posture, cinematic 35mm film grain, sense of command from a humble role",
    },
    {
        "topic": "Health informatics for IMGs — the technical career path that values your medical training and pays well",
        "pillar": "Courage to Choose",
        "first_comment": FC_CALC,
        "image_prompt": "Professional working on health data dashboards on two monitors, modern office, warm desk lamp, focused calm, cinematic 35mm film grain, slight lean forward, sense of engagement and mastery",
    },
    {
        "topic": "The sunk cost trap: why the years you invested in medicine should never decide your next 10 years",
        "pillar": "Courage to Choose",
        "first_comment": FC_CALC,
        "image_prompt": "Person at a fork in a misty road at dawn, one path continues straight, one turns toward light on the horizon, rear view, amber light breaking through, cinematic 35mm film grain, symbolic and quiet",
    },
    {
        "topic": "Flow state in a yellow vest — I found purpose in a low-status job before I built a second career",
        "pillar": "Crossing Guard Philosophy",
        "first_comment": FC_START,
        "image_prompt": "Person in yellow safety vest, eyes closed for a moment in early morning quiet, crosswalk empty, warm sunrise behind them, cinematic 35mm film grain, peaceful contentment, close-up portrait",
    },
    {
        "topic": "The LinkedIn pivot — how unmatched IMGs signal a career transition without looking like they gave up",
        "pillar": "Courage to Choose",
        "first_comment": FC_CALC,
        "image_prompt": "Person typing thoughtfully on a laptop, LinkedIn profile open on screen, warm room light, slight smile, cinematic 35mm film grain, sense of quiet confidence in self-presentation, shallow depth of field",
    },
    # ── May 23 ──────────────────────────────────────────────────────────────────
    {
        "topic": "The Ontario IMG policy reality check — what the 88% who don't match are never told about their options",
        "pillar": "Identity Cage",
        "first_comment": FC_FEAR,
        "image_prompt": "Ontario government building at dusk, stone facade, lone figure walking away from entrance, amber streetlights just turning on, cinematic 35mm film grain, institutional exclusion, quiet defiance",
    },
    {
        "topic": "The shift handover — what crossing guards know about letting go of who you were professionally",
        "pillar": "Crossing Guard Philosophy",
        "first_comment": FC_START,
        "image_prompt": "Two crossing guards doing a handover at end of shift, vests glowing in late afternoon light, friendly exchange, cinematic 35mm film grain, warm tones, dignity in the transition, candid moment",
    },
    {
        "topic": "Healthcare consulting for IMGs — what firms want and how to position your medical degree as an asset",
        "pillar": "Courage to Choose",
        "first_comment": FC_CALC,
        "image_prompt": "Professional presenting at a whiteboard in a small meeting room, smart casual attire, engaged colleagues, warm office light, cinematic 35mm film grain, confident and articulate presence, shallow depth of field",
    },
    {
        "topic": "The MCCQE Part 2 loop — how many IMGs are retaking the same exam hoping for a different outcome",
        "pillar": "Identity Cage",
        "first_comment": FC_FEAR,
        "image_prompt": "Person sitting alone in an exam hall, pencil in hand, papers spread on desk, fluorescent light, cinematic 35mm film grain, sense of repetition and quiet exhaustion, wide shot from behind",
    },
    {
        "topic": "The calm after the crossing — why peace feels unfamiliar when you have been in survival mode for years",
        "pillar": "Crossing Guard Philosophy",
        "first_comment": FC_START,
        "image_prompt": "Person sitting on steps outside in late afternoon sun, eyes closed, relaxed posture, warm golden light on face, crosswalk in background, cinematic 35mm film grain, earned stillness, close-up portrait",
    },
    # ── May 24 ──────────────────────────────────────────────────────────────────
    {
        "topic": "The parking lot cry after a CaRMS rejection — what it means and what the person who had it went on to do",
        "pillar": "Identity Cage",
        "first_comment": FC_FEAR,
        "image_prompt": "Empty hospital parking lot at dusk, single car, person sitting inside with head resting on steering wheel, amber parking lot lights, cinematic 35mm film grain, emotional privacy, cinematic wide shot",
    },
    {
        "topic": "4 non-clinical roles unmatched IMGs in Canada can start applying for this week — with salary ranges",
        "pillar": "Courage to Choose",
        "first_comment": FC_CALC,
        "image_prompt": "Confident professional walking into a modern office building, business casual attire, briefcase, glass doors, morning light, cinematic 35mm film grain, forward momentum, sense of new beginning",
    },
    {
        "topic": "The crosswalk moment — the exact point when an IMG stops waiting for permission and starts crossing",
        "pillar": "Crossing Guard Philosophy",
        "first_comment": FC_START,
        "image_prompt": "Person mid-step crossing a crosswalk in early morning light, looking forward not back, amber sunrise ahead, motion slightly blurred, cinematic 35mm film grain, decisive and free, hopeful energy",
    },
    {
        "topic": "What the free IMG calculator revealed — the number that finally made 300 people choose to cross",
        "pillar": "Courage to Choose",
        "first_comment": FC_CALC,
        "image_prompt": "Person looking at a smartphone screen, slight relief and recognition on their face, warm interior lighting, sitting at a kitchen table, cinematic 35mm film grain, moment of clarity, shallow depth of field",
    },
]

assert len(SLOTS) == len(SOURCE_FILES), f"Mismatch: {len(SLOTS)} slots vs {len(SOURCE_FILES)} sources"

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
        model="claude-opus-4-7",
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


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=== Crosswalk Wisdom — May 19–24 Content Pipeline ===\n")
    print(f"Scheduling {len(SOURCE_FILES)} posts across {len(SLOTS)} slots\n")
    results = []

    for i, src in enumerate(SOURCE_FILES):
        slot = SLOTS[i]
        slug = f"may-{i+7:02d}"
        img_raw   = f"{slug}-raw.png"
        img_final = f"{slug}-final.png"

        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(SOURCE_FILES)}]  {slot}  |  {src['pillar']}")
        print(f"Topic: {src['topic'][:80]}...")

        # 1. Write LinkedIn post directly from topic
        linkedin = write_linkedin_post(src["topic"], src["pillar"])
        short    = write_short_copy(linkedin)
        print(f"  Post written ({len(linkedin)} chars)")

        # 2. Generate DALL-E image
        raw_path = generate_image(src["image_prompt"], img_raw)

        # 3. Build HTML overlay + render
        h1, h2  = extract_hook(linkedin)
        sub     = extract_sub(linkedin)
        html_f  = write_html(slug, img_raw, h1, h2, sub, src["pillar"])
        final_p = IMAGES_DIR / img_final
        render_png(html_f, final_p)
        print(f"  PNG rendered: {img_final}")

        # 4. Upload to Zernio CDN
        cdn_url = upload_image(final_p)
        print(f"  Uploaded: {cdn_url[:70]}")

        # 5. Schedule post
        post_id = schedule_post(linkedin, short, cdn_url, slot, src["first_comment"])
        print(f"  Scheduled: {post_id}")

        results.append({
            "slot": slot, "pillar": src["pillar"],
            "post_id": post_id, "cdn_url": cdn_url,
        })

        time.sleep(2)

    print(f"\n\n{'='*60}")
    print("FINAL SCHEDULE")
    print(f"{'='*60}")
    for r in results:
        status = "OK" if not r["post_id"].startswith("ERROR") else "FAIL"
        print(f"  [{status}]  {r['slot']}  {r['pillar']:<30}  {r['post_id'][:30]}")

    ok = sum(1 for r in results if not r["post_id"].startswith("ERROR"))
    print(f"\nDone. {ok}/{len(results)} posts scheduled to Zernio.\n")


if __name__ == "__main__":
    main()
