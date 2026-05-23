"""
Schedules the 4 posts that hit the 5/day Zernio limit.
Moved to May 26-29 at 8am ET — those dates are currently empty.
Existing PNGs (may-08, may-09, may-14) are reused; may-34 was already rendered.
"""
from __future__ import annotations
import os, time, subprocess, requests
from pathlib import Path
from anthropic import Anthropic

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
OPENAI_KEY    = os.getenv("OPENAI_KEY")
ZERNIO_KEY    = os.getenv("ZERNIO_KEY")

ZERNIO_BASE = "https://zernio.com/api/v1"
ZERNIO_HDR  = {"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"}
OPENAI_HDR  = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TIMEZONE     = "America/New_York"

IMAGES_DIR = Path("/Users/toto/Claude TubeonAI/social-assets/linkedin-may/images")
HTML_DIR   = Path("/Users/toto/Claude TubeonAI/social-assets/linkedin-may")

anthropic = Anthropic(api_key=ANTHROPIC_KEY)

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

POSTS = [
    {
        "slug": "may-08", "slot": "2026-05-26T08:00:00",
        "topic": "The WhatsApp family group lie — what unmatched IMGs tell their parents vs. what they feel at midnight",
        "pillar": "Identity Cage",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
    {
        "slug": "may-09", "slot": "2026-05-27T08:00:00",
        "topic": "Clinical research in Canada for IMGs — a $75K career path that doesn't require residency",
        "pillar": "Courage to Choose",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: www.crosswalkwisdom.com/img/calculator",
    },
    {
        "slug": "may-14", "slot": "2026-05-28T08:00:00",
        "topic": "The $48K salary slip — what no one tells unmatched IMGs about income while they wait for residency",
        "pillar": "Identity Cage",
        "first_comment": "Here's the Fear Audit — 5 minutes to name what's holding you in the loop: https://fear-audit.vercel.app",
    },
    {
        "slug": "may-34", "slot": "2026-05-29T08:00:00",
        "topic": "4 non-clinical roles unmatched IMGs in Canada can start applying for this week — with salary ranges",
        "pillar": "Courage to Choose",
        "first_comment": "Here's the free IMG Reality Calculator — see the actual math before you decide: www.crosswalkwisdom.com/img/calculator",
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


def extract_hook(post: str):
    lines = [l.strip() for l in post.split("\n") if l.strip()]
    return lines[0] if lines else "", lines[1] if len(lines) > 1 else ""


def extract_sub(post: str) -> str:
    lines = [l.strip() for l in post.split("\n") if l.strip()]
    return lines[2] if len(lines) > 2 else ""


def rerender_png(slug: str, post: str, pillar: str) -> Path:
    h1, h2 = extract_hook(post)
    sub     = extract_sub(post)
    raw_img = f"{slug}-raw.png"

    def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace('"','&quot;')
    html = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{width:1080px;height:1080px;overflow:hidden}}
.card{{width:1080px;height:1080px;position:relative;background-image:url('./images/{raw_img}');background-size:cover;background-position:center;display:flex;flex-direction:column;justify-content:flex-end}}
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

    html_path = HTML_DIR / f"{slug}-overflow.html"
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
    print("=== Overflow: 4 posts → May 26-29 8am ===\n")
    results = []

    for i, src in enumerate(POSTS):
        print(f"\n[{i+1}/4]  {src['slot']}  |  {src['pillar']}")
        print(f"  {src['topic'][:70]}...")

        linkedin = write_post(src["topic"], src["pillar"])
        short    = write_short(linkedin)
        print(f"  Post: {len(linkedin)} chars")

        final_png = rerender_png(src["slug"], linkedin, src["pillar"])
        print(f"  PNG: {final_png.name}")

        time.sleep(5)
        cdn_url = upload(final_png)
        print(f"  Uploaded: {cdn_url[:70]}")

        time.sleep(8)
        post_id = schedule(linkedin, short, cdn_url, src["slot"], src["first_comment"])
        ok = not post_id.startswith("ERROR")
        print(f"  [{'OK' if ok else 'FAIL'}] {post_id[:50]}")

        results.append({"slot": src["slot"], "id": post_id, "ok": ok})
        time.sleep(12)

    print(f"\n{'='*50}")
    ok_count = sum(1 for r in results if r["ok"])
    for r in results:
        print(f"  {'OK' if r['ok'] else 'FAIL'}  {r['slot']}  {r['id'][:30]}")
    print(f"\n{ok_count}/4 posts scheduled.\n")


if __name__ == "__main__":
    main()
