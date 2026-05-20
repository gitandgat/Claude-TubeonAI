"""Retry the single post that failed due to Anthropic 529 overload."""
from __future__ import annotations
import time, subprocess, requests
from pathlib import Path
from anthropic import Anthropic

ANTHROPIC_KEY = "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"
OPENAI_KEY    = "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"
ZERNIO_KEY    = "sk_d1c977cc304ec9685c24f22c7e3b868abd5a10b9db8f7648b2b74384ab1ca399"
ZERNIO_BASE   = "https://zernio.com/api/v1"
ZERNIO_HDR    = {"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"}
OPENAI_HDR    = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
LINKEDIN_ID   = "690940455f6fbb9ef8323070"
INSTAGRAM_ID  = "690940655f6fbb9ef8323072"
FACEBOOK_ID   = "6909409a5f6fbb9ef8323074"
TIKTOK_ID     = "690941425f6fbb9ef8323078"
TIMEZONE      = "America/New_York"
IMAGES_DIR    = Path("/Users/toto/Claude TubeonAI/social-assets/linkedin-may/images")
HTML_DIR      = Path("/Users/toto/Claude TubeonAI/social-assets/linkedin-may")

anthropic = Anthropic(api_key=ANTHROPIC_KEY)

SYSTEM_PROMPT = """\
You write LinkedIn posts for Crosswalk Wisdom by Sahawat — a former physician who left medicine, became a crossing guard, and helps unmatched IMGs in Canada pivot careers.
AUDIENCE: 34yo Indian IMG, failed CaRMS twice, lab assistant $48K/year, Googles career options at midnight.
STRUCTURE: 1) HOOK 2 lines max 2) REFRAME "The question isn't X. It's Y." 3) SENSORY LIST ✨ 3 lines 4) LESSONS 👣 3 lines 5) BRAND REVEAL mid-post 6) CTA "5 minutes. 📬 Link in the comments." 7) QUESTION 8) 4 HASHTAGS #CrosswalkWisdom #IMGCanada + 2 more.
Under 1500 chars. Lived experience only. Output ONLY the post."""

TOPIC  = "4 non-clinical roles unmatched IMGs in Canada can start applying for this week — with salary ranges"
PILLAR = "Courage to Choose"
SLOT   = "2026-05-29T08:00:00"
FC     = "Here's the free IMG Reality Calculator — see the actual math before you decide: https://crosswalkwisdom.com/calculator"
SLUG   = "may-34"

def write_post_with_retry():
    for attempt in range(5):
        try:
            msg = anthropic.messages.create(
                model="claude-opus-4-7", max_tokens=800, system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content":
                    f"Topic: {TOPIC}\nPillar: {PILLAR}\n\nWrite as Sahawat's lived experience."}]
            )
            return msg.content[0].text.strip()
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}. Waiting 30s...")
            time.sleep(30)
    raise RuntimeError("All retries exhausted")

def write_short(post):
    msg = anthropic.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=300,
        messages=[{"role": "user", "content":
            "Compress to 250-300 char Instagram caption. Keep hook and hashtags.\n\n" + post}]
    )
    return msg.content[0].text.strip()

def rerender(post):
    lines = [l.strip() for l in post.split("\n") if l.strip()]
    h1 = lines[0] if lines else ""
    h2 = lines[1] if len(lines) > 1 else ""
    sub = lines[2] if len(lines) > 2 else ""
    def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace('"','&quot;')
    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{width:1080px;height:1080px;overflow:hidden}}
.card{{width:1080px;height:1080px;position:relative;background-image:url('./images/{SLUG}-raw.png');background-size:cover;background-position:center;display:flex;flex-direction:column;justify-content:flex-end}}
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
.author{{font-family:'Inter',sans-serif;font-size:13px;color:rgba(250,247,242,.3)}}</style></head>
<body><div class="card"><div class="overlay"></div><div class="accent"></div>
<div class="content"><div class="tag">{esc(PILLAR)}</div>
<div class="hook">{esc(h1)}<br><em>{esc(h2)}</em></div>
<div class="divider"></div><div class="sub">{esc(sub)}</div>
<div class="bottom"><span class="brand">Crosswalk Wisdom</span>
<span class="author">Sahawat — IMG, Crossing Guard, Founder</span>
</div></div></div></body></html>"""
    html_path = HTML_DIR / f"{SLUG}-last.html"
    html_path.write_text(html)
    out = IMAGES_DIR / f"{SLUG}-final.png"
    r = subprocess.run(["shot-scraper", str(html_path), "-o", str(out), "--width", "1080", "--height", "1080"],
        cwd=str(HTML_DIR), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"shot-scraper: {r.stderr}")
    return out

def upload(fp):
    r = requests.post(f"{ZERNIO_BASE}/media/presign", headers=ZERNIO_HDR,
        json={"filename": fp.name, "contentType": "image/png", "fileSize": fp.stat().st_size})
    r.raise_for_status()
    d = r.json()
    with open(fp, "rb") as f:
        requests.put(d["uploadUrl"], data=f, headers={"Content-Type": "image/png"}).raise_for_status()
    return d["publicUrl"]

print(f"Scheduling: {TOPIC[:60]}...")
print(f"Slot: {SLOT}")

linkedin = write_post_with_retry()
short    = write_short(linkedin)
print(f"Post written ({len(linkedin)} chars)")

png = rerender(linkedin)
print(f"PNG rendered: {png.name}")

cdn = upload(png)
print(f"Uploaded: {cdn[:70]}")

body = {
    "content": linkedin,
    "mediaItems": [{"url": cdn, "type": "image"}],
    "platforms": [
        {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": linkedin,
         "scheduledFor": SLOT, "platformSpecificData": {"firstComment": FC}},
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": short, "scheduledFor": SLOT},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": linkedin, "scheduledFor": SLOT},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": short, "scheduledFor": SLOT},
    ],
    "scheduledFor": SLOT, "timezone": TIMEZONE,
}
r = requests.post(f"{ZERNIO_BASE}/posts", headers=ZERNIO_HDR, json=body)
post_id = r.json().get("post", {}).get("_id", f"ERROR:{r.status_code}:{r.text[:100]}")
print(f"{'OK' if not post_id.startswith('ERROR') else 'FAIL'}: {post_id}")
