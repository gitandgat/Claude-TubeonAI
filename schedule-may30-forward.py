"""
Schedule May 30+ posts with proper 2-hour spacing (8am, 10am, 12pm, 2pm, 4pm ET).
Respects Zernio 5/day per-slot limit and minimum 2-hour gaps between posts.
"""
from __future__ import annotations
import os, time, subprocess, requests
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI

load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_KEY    = os.getenv("OPENAI_API_KEY")
ZERNIO_KEY    = os.getenv("ZERNIO_API_KEY")

ZERNIO_BASE = "https://zernio.com/api/v1"
ZERNIO_HDR  = {"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TIMEZONE     = "America/New_York"

IMAGES_DIR = Path("/Users/toto/Claude TubeonAI/social-assets/linkedin-may/images")
HTML_DIR   = Path("/Users/toto/Claude TubeonAI/social-assets/linkedin-may")

anthropic = Anthropic(api_key=ANTHROPIC_KEY)
openai = OpenAI(api_key=OPENAI_KEY)

SYSTEM_PROMPT = """\
You write LinkedIn posts for Crosswalk Wisdom, a brand by Sahawat Nilwatcharamanee — a former physician who left medicine, became a crossing guard, and now helps unmatched IMGs in Canada navigate career transitions.

AUDIENCE: A 34-year-old IMG from India. Passed MCCQE Part 1. Failed CaRMS twice. Working as a lab assistant at $48K/year. Family thinks he's "almost a doctor in Canada." Googles "IMG unmatched career options" at midnight.

STRUCTURE — follow exactly:
1. HOOK (2 lines max): Status-drop or vulnerability contrast.
2. REFRAME: "The question isn't X. It's Y."
3. SENSORY LIST (✨): 3 lines. Specific details — Tim Hortons, lab coat, midnight Google, parking lot tears, WhatsApp family chat, yellow vest.
4. LESSONS LIST (👣): 3 lines. Short infinitive phrases.
5. BRAND REVEAL (mid-post): "I call it Crosswalk Wisdom — [one-line description]."
6. CTA: "5 minutes. 📬 Link in the comments."
7. ENGAGEMENT QUESTION: One universal question.
8. HASHTAGS: 4 only. Always #CrosswalkWisdom #IMGCanada plus 2 contextual.

Under 1500 characters. Write as lived experience. Output ONLY the post."""

# 5 posts/day × 6 days (May 30-31, June 1-3) = 30 posts
POSTS = [
    # May 30 (5 posts with 2-hour spacing: 8am, 10am, 12pm, 2pm, 4pm)
    {
        "slug": "may-37", "slot": "2026-05-30T08:00:00",
        "topic": "The midnight panic attack — why IMGs freeze when they see a job posting that matches their dreams",
        "pillar": "Identity Cage",
        "image_prompt": "Cinematic close-up of hands trembling over a laptop screen at 2am, blue light reflecting in eyes, cold coffee beside keyboard, out-of-focus job listing visible",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
    {
        "slug": "may-38", "slot": "2026-05-30T10:00:00",
        "topic": "CaRMS rejection isn't about clinical skill — it's about visibility politics and timeline luck",
        "pillar": "Courage to Choose",
        "image_prompt": "Moody office scene: CaRMS portal screen with rejection email, stack of case files, stethoscope coiled on desk, soft dramatic lighting from window",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
    },
    {
        "slug": "may-39", "slot": "2026-05-30T12:00:00",
        "topic": "The $48K salary lie — what it costs an IMG besides money when they're stuck in non-clinical limbo",
        "pillar": "Identity Cage",
        "image_prompt": "Dramatic split-screen: one side shows laptop with paystub, other side shows medical school diploma on wall, high contrast lighting, somber mood",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
    {
        "slug": "may-40", "slot": "2026-05-30T14:00:00",
        "topic": "4 roles in Canada where IMG credentials are an *asset*, not a barrier — and the salary ranges you should expect",
        "pillar": "Courage to Choose",
        "image_prompt": "Collage of 4 professional settings: lab, hospital hallway, research office, clinic. Warm, hopeful lighting, diverse professionals at work",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
    },
    {
        "slug": "may-41", "slot": "2026-05-30T16:00:00",
        "topic": "The yellow vest taught me something MD credentials never could — permission to be imperfect",
        "pillar": "Crossing Guard Philosophy",
        "image_prompt": "Sahawat in yellow crossing guard vest on street, peaceful expression, early morning light, cars blurred in background, serene and purposeful",
        "first_comment": "Here's the Crossing Guard Philosophy — finding purpose outside the residency trap: https://crosswalkwisdom.com/philosophy",
    },
    # May 31 (5 posts)
    {
        "slug": "may-42", "slot": "2026-05-31T08:00:00",
        "topic": "What unmatched IMGs don't tell their parents — the invisible grief of reaching a credential nobody values",
        "pillar": "Identity Cage",
        "image_prompt": "Intimate scene: person on phone, blurred WhatsApp chat visible on screen, family photos on wall, dim bedroom lighting, weight of expectation visible",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
    {
        "slug": "may-43", "slot": "2026-05-31T10:00:00",
        "topic": "The one question that breaks the pivot paralysis — and why IMGs never ask it",
        "pillar": "Courage to Choose",
        "image_prompt": "Person sitting at kitchen table, hand on chin in contemplative pose, morning light, blank journal nearby, expression of realization dawning",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
    },
    {
        "slug": "may-44", "slot": "2026-05-31T12:00:00",
        "topic": "Tim Hortons at 6am — the unspoken ritual where IMGs process their choices",
        "pillar": "Crossing Guard Philosophy",
        "image_prompt": "Tim Hortons counter, steam rising from coffee cup, IMG worker in scrubs across the table, warm interior lighting, vulnerable quiet moment",
        "first_comment": "Here's the Crossing Guard Philosophy — finding purpose outside the residency trap: https://crosswalkwisdom.com/philosophy",
    },
    {
        "slug": "may-45", "slot": "2026-05-31T14:00:00",
        "topic": "Why PhD-track research is the path nobody tells unmatched IMGs exists — $75K salary, no residency required",
        "pillar": "Courage to Choose",
        "image_prompt": "Research lab: IMG in lab coat examining test tubes, microscope, data charts on wall, collaborative colleagues in background, modern clean setting",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
    },
    {
        "slug": "may-46", "slot": "2026-05-31T16:00:00",
        "topic": "The real cost of 'almosts' — what happens when you chase a residency that won't come",
        "pillar": "Identity Cage",
        "image_prompt": "Burned-out IMG at desk, multiple rejection letters visible, tired eyes, weak afternoon light, sense of depletion, reality check moment",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
    # June 1 (5 posts)
    {
        "slug": "jun-01", "slot": "2026-06-01T08:00:00",
        "topic": "The bridge nobody talks about — how to go from 'failed IMG' to 'unmatched IMG who chose differently'",
        "pillar": "Courage to Choose",
        "image_prompt": "Symbolic bridge scene: person standing at crossroads, one path toward hospital, other path toward different opportunity, hopeful dawn lighting",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
    },
    {
        "slug": "jun-02", "slot": "2026-06-01T10:00:00",
        "topic": "Sunk cost isn't a number — it's the weight you carry at 34, stuck between two countries, two identities",
        "pillar": "Identity Cage",
        "image_prompt": "Silhouette of person with weight on shoulders, facing sunset over city skyline, emotional depth, global perspective merging Canadian and Indian elements",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
    {
        "slug": "jun-03", "slot": "2026-06-01T12:00:00",
        "topic": "The clinical role that *won't* require another exam — and why you have zero idea it exists",
        "pillar": "Courage to Choose",
        "image_prompt": "Professional IMG in clinical setting without white coat, engaging with patient in non-surgical role, warm collaborative atmosphere, modern healthcare",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
    },
    {
        "slug": "jun-04", "slot": "2026-06-01T14:00:00",
        "topic": "Yellow vest wisdom — why standing still on the corner taught me more than residency ever did",
        "pillar": "Crossing Guard Philosophy",
        "image_prompt": "Sahawat in yellow vest directing traffic, serene focus, safe and purposeful, community visible, redemptive moment of finding meaning in unexpected role",
        "first_comment": "Here's the Crossing Guard Philosophy — finding purpose outside the residency trap: https://crosswalkwisdom.com/philosophy",
    },
    {
        "slug": "jun-05", "slot": "2026-06-01T16:00:00",
        "topic": "What 'pivot' really means for an IMG — it's not failure, it's recalibration at the right time",
        "pillar": "Courage to Choose",
        "image_prompt": "IMG at turning point, looking at two directions, one showing residency lab, other showing broader healthcare career path, balanced perspective",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
    },
    # June 2 (5 posts)
    {
        "slug": "jun-06", "slot": "2026-06-02T08:00:00",
        "topic": "The family chat that nobody answers — why your parents' expectations are 10 years behind your reality",
        "pillar": "Identity Cage",
        "image_prompt": "WhatsApp chat visible on phone screen, family emojis, misunderstood comments, person alone with phone, cultural disconnect visualized, emotional weight",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
    {
        "slug": "jun-07", "slot": "2026-06-02T10:00:00",
        "topic": "Ultrasound technician path in Canada — $65K starting, full credential recognition, zero additional exams",
        "pillar": "Courage to Choose",
        "image_prompt": "Ultrasound tech performing scan, IMG professional in clinical setting, modern equipment, confident clinical presence, respected role visualized",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
    },
    {
        "slug": "jun-08", "slot": "2026-06-02T12:00:00",
        "topic": "What I learned standing in the rain at 6am on the corner — permission doesn't come from a credential",
        "pillar": "Crossing Guard Philosophy",
        "image_prompt": "Crossing guard in rain with umbrella, focused and purposeful in bad weather, dignified and calm, finding meaning in simple service, redemptive atmosphere",
        "first_comment": "Here's the Crossing Guard Philosophy — finding purpose outside the residency trap: https://crosswalkwisdom.com/philosophy",
    },
    {
        "slug": "jun-09", "slot": "2026-06-02T14:00:00",
        "topic": "The IMG paradox — overqualified for every job that doesn't require a residency, invisible for the ones that do",
        "pillar": "Identity Cage",
        "image_prompt": "Split perspective: IMG looking at job postings on one screen, credentials highlighted, invisible barriers visualized, frustration and clarity moment",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
    {
        "slug": "jun-10", "slot": "2026-06-02T16:00:00",
        "topic": "Lab director, research lead, education coordinator — 3 IMG-friendly roles paying $70K+ that nobody mentors you toward",
        "pillar": "Courage to Choose",
        "image_prompt": "Composite of 3 professional roles: lab director overseeing team, researcher presenting findings, education coordinator teaching, diverse IMG professionals thriving",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
    },
    # June 3 (5 posts)
    {
        "slug": "jun-11", "slot": "2026-06-03T08:00:00",
        "topic": "The question nobody asks — what if failing CaRMS was the best thing that happened to you?",
        "pillar": "Courage to Choose",
        "image_prompt": "IMG looking back at CaRMS rejection with new perspective, sunlight on face, hopeful realization, path forward visible, growth moment captured",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
    },
    {
        "slug": "jun-12", "slot": "2026-06-03T10:00:00",
        "topic": "Immigrant weight — the invisible tax of leaving your country, passing exams, and still not being 'enough'",
        "pillar": "Identity Cage",
        "image_prompt": "Contemplative IMG looking at globe or map, showing India and Canada, weight of migration, family separation, dual identity conflict visualized",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
    {
        "slug": "jun-13", "slot": "2026-06-03T12:00:00",
        "topic": "Regulatory coordinator for medical boards — $68K, IMG-credentialed, nobody mentions this path",
        "pillar": "Courage to Choose",
        "image_prompt": "Professional in regulatory office, IMG working with medical documentation, confident in role, modern institutional setting, meaningful healthcare contribution",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator",
    },
    {
        "slug": "jun-14", "slot": "2026-06-03T14:00:00",
        "topic": "What Sahawat learned on the crossing — that safety isn't about status, it's about presence",
        "pillar": "Crossing Guard Philosophy",
        "image_prompt": "Crossing guard creating safe passage for children and adults, protective presence, dignified service, community care visualized, purpose found moment",
        "first_comment": "Here's the Crossing Guard Philosophy — finding purpose outside the residency trap: https://crosswalkwisdom.com/philosophy",
    },
    {
        "slug": "jun-15", "slot": "2026-06-03T16:00:00",
        "topic": "Two years into 'maybe next time' — at what point does a dream become a sunk cost that won't return?",
        "pillar": "Identity Cage",
        "image_prompt": "Clock showing passage of time, IMG looking exhausted, at crossroads between continuing to wait or making decisive change, reality check moment",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
]


def write_post(topic: str, pillar: str) -> str:
    msg = anthropic.messages.create(
        model="claude-opus-4-7", max_tokens=800, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content":
            f"Topic: {topic}\nPillar: {pillar}\n\nWrite as Sahawat's lived experience."}]
    )
    return msg.content[0].text.strip()


def write_short(post: str) -> str:
    msg = anthropic.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=300,
        messages=[{"role": "user", "content":
            "Compress to 250-300 char Instagram caption. Keep hook and hashtags. Output only caption.\n\n" + post}]
    )
    return msg.content[0].text.strip()


def generate_image(prompt: str) -> str:
    """Generate image with DALL-E 3."""
    response = openai.images.generate(
        model="dall-e-3",
        prompt=f"{prompt} Cinematic, professional photography, high quality, warm and hopeful mood.",
        size="1024x1024",
        quality="hd",
        n=1
    )
    return response.data[0].url


def extract_hook(post: str):
    lines = [l.strip() for l in post.split("\n") if l.strip()]
    return lines[0] if lines else "", lines[1] if len(lines) > 1 else ""


def extract_sub(post: str) -> str:
    lines = [l.strip() for l in post.split("\n") if l.strip()]
    return lines[2] if len(lines) > 2 else ""


def rerender_html(slug: str, post: str, pillar: str) -> Path:
    h1, h2 = extract_hook(post)
    sub = extract_sub(post)

    def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace('"','&quot;')
    html = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{width:1080px;height:1080px;overflow:hidden}}
.card{{width:1080px;height:1080px;position:relative;background:linear-gradient(135deg,#1a1a1a 0%,#2d2d2d 100%);display:flex;flex-direction:column;justify-content:flex-end}}
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
</style></head><body><div class="card">
<div class="overlay"></div><div class="accent"></div>
<div class="content">
<div class="tag">{esc(pillar)}</div>
<div class="hook">{esc(h1)}<br><em>{esc(h2)}</em></div>
<div class="divider"></div>
<div class="sub">{esc(sub)}</div>
<div class="bottom">
<span class="brand">Crosswalk Wisdom</span>
<span class="author">Sahawat — IMG, Crossing Guard, Founder</span>
</div></div></div></body></html>"""

    html_path = HTML_DIR / f"{slug}-final.html"
    html_path.write_text(html)
    out_png = IMAGES_DIR / f"{slug}-final.png"
    r = subprocess.run(
        ["shot-scraper", str(html_path), "-o", str(out_png), "--width", "1080", "--height", "1080"],
        cwd=str(HTML_DIR), capture_output=True, text=True
    )
    if r.returncode != 0:
        raise RuntimeError(f"shot-scraper: {r.stderr}")
    return out_png


def upload(filepath: Path) -> str:
    r = requests.post(f"{ZERNIO_BASE}/media/presign", headers=ZERNIO_HDR,
        json={"filename": filepath.name, "contentType": "image/png",
              "fileSize": filepath.stat().st_size})
    r.raise_for_status()
    d = r.json()
    with open(filepath, "rb") as f:
        requests.put(d["uploadUrl"], data=f, headers={"Content-Type": "image/png"}).raise_for_status()
    return d["publicUrl"]


def schedule(linkedin: str, short: str, img_url: str, slot: str, fc: str) -> str:
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
    print("=== May 30+ Content: 30 posts across 6 days with 2-hour spacing ===\n")
    results = []

    for i, src in enumerate(POSTS):
        print(f"\n[{i+1}/30]  {src['slot']}  |  {src['pillar']}")
        print(f"  {src['topic'][:70]}...")

        try:
            linkedin = write_post(src["topic"], src["pillar"])
            short    = write_short(linkedin)
            print(f"  Post: {len(linkedin)} chars")

            print(f"  Generating image...")
            img_url = generate_image(src["image_prompt"])
            print(f"  Image: {img_url[:70]}")

            # Download and save locally
            img_response = requests.get(img_url)
            img_path = IMAGES_DIR / f"{src['slug']}-dalle.png"
            img_path.write_bytes(img_response.content)

            print(f"  Rendering HTML...")
            final_png = rerender_html(src["slug"], linkedin, src["pillar"])
            print(f"  PNG: {final_png.name}")

            time.sleep(3)
            cdn_url = upload(final_png)
            print(f"  Uploaded: {cdn_url[:70]}")

            time.sleep(5)
            post_id = schedule(linkedin, short, cdn_url, src["slot"], src["first_comment"])
            ok = not post_id.startswith("ERROR")
            print(f"  [{'OK' if ok else 'FAIL'}] {post_id[:50]}")

            results.append({"slot": src["slot"], "slug": src["slug"], "id": post_id, "ok": ok})
            time.sleep(6)  # 6s between posts

        except Exception as e:
            print(f"  ERROR: {str(e)[:100]}")
            results.append({"slot": src["slot"], "slug": src["slug"], "id": f"ERROR:{str(e)[:30]}", "ok": False})
            time.sleep(10)

    print(f"\n{'='*60}")
    ok_count = sum(1 for r in results if r["ok"])
    print(f"\nSummary: {ok_count}/{len(POSTS)} posts scheduled successfully\n")
    for r in results:
        status = "✓" if r["ok"] else "✗"
        print(f"  {status}  {r['slot']}  {r['slug']}  {r['id'][:40]}")
    print(f"\n")


if __name__ == "__main__":
    main()
