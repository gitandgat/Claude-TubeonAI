"""Build a premium, self-contained branded microsite (one HTML file) per job.

Crosswalk Wisdom brand: editorial / light-luxury. Playfair Display + Inter,
amber/charcoal/warm-white palette, crosswalk-dawn hero imagery.
"""

import html
import re
import shutil
from pathlib import Path

from content_generator import write_30_day_plan, write_video_script, write_why_them
from resume_data import PROFILE

BASE = Path(__file__).resolve().parent
OUTPUT_DIR = BASE / "microsites"
OUTPUT_DIR.mkdir(exist_ok=True)

HERO_SRC = (
    BASE.parent / "crosswalk-remotion" / "public" / "assets" / "bg-gen-05-crosswalk-dawn.jpg"
)
HERO_NAME = "hero.jpg"

BOOK_CALL_URL = "https://www.crosswalkwisdom.com/start"


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60]


def _ensure_hero():
    dest = OUTPUT_DIR / HERO_NAME
    if not dest.exists() and HERO_SRC.exists():
        shutil.copy(HERO_SRC, dest)


def build_microsite(job: dict, why_them: str = None, plan: list = None, video_script: str = None) -> dict:
    """Build the microsite HTML for a job. Returns {path, slug, video_script}."""
    _ensure_hero()

    why_them = why_them or write_why_them(job)
    plan = plan or write_30_day_plan(job)
    video_script = video_script or write_video_script(job)

    slug = slugify(f"{job['company']}-{job['title']}")
    company = html.escape(job["company"])
    title = html.escape(job["title"])

    plan_cards = "\n".join(
        f"""        <li class="plan-card" style="--i:{i}">
          <span class="plan-num">{i + 1:02d}</span>
          <p>{html.escape(item)}</p>
        </li>"""
        for i, item in enumerate(plan)
    )

    cert_chips = "\n".join(
        f'          <li>{html.escape(c)}</li>' for c in PROFILE["certifications"][:4]
    )

    video_path = f"{slug}.mp4"

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Sahawat Nilwatcharamanee — for {company}</title>
<meta name="description" content="A personal note from Sahawat to the {company} team about the {title} role." />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
<style>
  :root {{
    --amber: #D4A843;
    --charcoal: #2C2C2C;
    --warm-white: #FAF7F2;
    --orange: #E8834A;
    --teal: #5B9A8B;
    --black: #1A1A1A;
    --serif: "Playfair Display", Georgia, serif;
    --sans: "Inter", system-ui, sans-serif;
    --space-section: clamp(4rem, 3rem + 5vw, 9rem);
    --ease: cubic-bezier(0.16, 1, 0.3, 1);
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    font-family: var(--sans);
    color: var(--charcoal);
    background: var(--warm-white);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }}

  .hero {{
    position: relative;
    min-height: 100svh;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: clamp(2rem, 6vw, 6rem);
    color: var(--warm-white);
    overflow: hidden;
  }}
  .hero::before {{
    content: "";
    position: absolute; inset: 0;
    background: url("{HERO_NAME}") center/cover no-repeat;
    transform: scale(1.05);
    animation: kenburns 20s var(--ease) infinite alternate;
    z-index: -2;
  }}
  .hero::after {{
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(26,26,26,0.55) 0%, rgba(26,26,26,0.35) 40%, rgba(26,26,26,0.85) 100%);
    z-index: -1;
  }}
  @keyframes kenburns {{ to {{ transform: scale(1.18); }} }}

  .eyebrow {{
    font-size: 0.78rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--amber);
    font-weight: 600;
    margin-bottom: 1.25rem;
    opacity: 0; animation: rise 0.9s var(--ease) 0.1s forwards;
  }}
  .hero h1 {{
    font-family: var(--serif);
    font-weight: 700;
    font-size: clamp(2.6rem, 1rem + 7vw, 6rem);
    line-height: 1.02;
    max-width: 16ch;
    opacity: 0; animation: rise 0.9s var(--ease) 0.25s forwards;
  }}
  .hero h1 em {{ color: var(--amber); font-style: italic; }}
  .hero .path {{
    margin-top: 1.75rem;
    font-size: clamp(1rem, 0.9rem + 0.5vw, 1.35rem);
    font-weight: 500;
    color: rgba(250,247,242,0.92);
    opacity: 0; animation: rise 0.9s var(--ease) 0.4s forwards;
  }}
  .hero .path b {{ color: var(--warm-white); }}
  .scroll-hint {{
    margin-top: 2.5rem; font-size: 0.8rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: rgba(250,247,242,0.7);
    opacity: 0; animation: rise 0.9s var(--ease) 0.6s forwards;
  }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(24px); }} to {{ opacity: 1; transform: none; }} }}

  section {{ padding: var(--space-section) clamp(1.5rem, 6vw, 8rem); }}
  .section-label {{
    font-size: 0.78rem; letter-spacing: 0.24em; text-transform: uppercase;
    color: var(--orange); font-weight: 600; margin-bottom: 1.5rem;
  }}
  .lead {{
    font-family: var(--serif);
    font-size: clamp(1.5rem, 1rem + 2vw, 2.6rem);
    line-height: 1.25; font-weight: 500; max-width: 22ch;
  }}

  /* Video */
  .video-section {{ background: var(--charcoal); color: var(--warm-white); }}
  .video-wrap {{
    max-width: 820px; margin: 2rem auto 0; border-radius: 14px; overflow: hidden;
    box-shadow: 0 30px 80px rgba(0,0,0,0.45); aspect-ratio: 16/9;
    background: linear-gradient(135deg, #232323, #1a1a1a);
    display: flex; align-items: center; justify-content: center; position: relative;
  }}
  .video-wrap video {{ width: 100%; height: 100%; object-fit: cover; }}
  .video-placeholder {{ text-align: center; padding: 2rem; color: rgba(250,247,242,0.6); }}
  .video-placeholder .play {{
    width: 72px; height: 72px; border-radius: 50%; margin: 0 auto 1rem;
    background: var(--amber); display: grid; place-items: center;
  }}
  .video-placeholder .play::after {{
    content: ""; border-left: 20px solid var(--charcoal);
    border-top: 12px solid transparent; border-bottom: 12px solid transparent; margin-left: 5px;
  }}
  .video-section .section-label {{ color: var(--amber); }}

  /* Why them */
  .why p {{
    font-size: clamp(1.05rem, 0.95rem + 0.6vw, 1.4rem);
    max-width: 60ch; line-height: 1.7; color: #3a3a3a;
  }}

  /* 30-day plan */
  .plan {{ background: var(--black); color: var(--warm-white); }}
  .plan .section-label {{ color: var(--teal); }}
  .plan ul {{ list-style: none; display: grid; gap: 1.25rem; margin-top: 2.5rem;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }}
  .plan-card {{
    background: rgba(250,247,242,0.04); border: 1px solid rgba(212,168,67,0.25);
    border-radius: 12px; padding: 2rem 1.75rem; transition: transform 0.3s var(--ease), border-color 0.3s;
  }}
  .plan-card:hover {{ transform: translateY(-6px); border-color: var(--amber); }}
  .plan-num {{ font-family: var(--serif); font-size: 2.5rem; color: var(--amber); display: block; margin-bottom: 0.75rem; }}
  .plan-card p {{ font-size: 1rem; color: rgba(250,247,242,0.88); }}

  /* Credentials */
  .creds ul {{ list-style: none; display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 2rem; }}
  .creds li {{
    background: #fff; border: 1px solid rgba(44,44,44,0.12); border-radius: 999px;
    padding: 0.6rem 1.25rem; font-size: 0.9rem; font-weight: 500;
    box-shadow: 0 2px 10px rgba(44,44,44,0.05);
  }}

  /* CTA */
  .cta {{ background: var(--amber); color: var(--charcoal); text-align: center; }}
  .cta h2 {{ font-family: var(--serif); font-size: clamp(1.8rem, 1rem + 4vw, 3.5rem); font-weight: 700; max-width: 18ch; margin: 0 auto 2rem; }}
  .buttons {{ display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }}
  .btn {{
    display: inline-block; padding: 1rem 2rem; border-radius: 999px; font-weight: 600;
    text-decoration: none; font-size: 1rem; transition: transform 0.25s var(--ease), box-shadow 0.25s;
  }}
  .btn-primary {{ background: var(--charcoal); color: var(--warm-white); }}
  .btn-secondary {{ background: transparent; color: var(--charcoal); border: 2px solid var(--charcoal); }}
  .btn:hover {{ transform: translateY(-3px); box-shadow: 0 12px 30px rgba(0,0,0,0.2); }}
  footer {{ background: var(--charcoal); color: rgba(250,247,242,0.7); text-align: center; padding: 2.5rem 1rem; font-size: 0.85rem; }}
  footer a {{ color: var(--amber); text-decoration: none; }}

  @media (prefers-reduced-motion: reduce) {{
    .hero::before {{ animation: none; }}
    .eyebrow, .hero h1, .hero .path, .scroll-hint {{ animation: none; opacity: 1; }}
  }}
</style>
</head>
<body>
  <header class="hero">
    <p class="eyebrow">A personal note for the {company} team</p>
    <h1>I'd like to be your next <em>{title}</em>.</h1>
    <p class="path"><b>Sahawat Nilwatcharamanee</b> &nbsp;·&nbsp; Doctor &rarr; Crossing Guard &rarr; Coach</p>
    <p class="scroll-hint">Scroll &darr;</p>
  </header>

  <section class="video-section">
    <p class="section-label">A 30-second hello</p>
    <h2 class="lead">It felt right to say this to your face, not just on paper.</h2>
    <div class="video-wrap">
      <video controls poster="{HERO_NAME}" preload="none" onerror="this.style.display='none';this.nextElementSibling.style.display='block'">
        <source src="{video_path}" type="video/mp4" />
      </video>
      <div class="video-placeholder" style="display:none">
        <div class="play"></div>
        <p>Personal video message</p>
      </div>
    </div>
  </section>

  <section class="why">
    <p class="section-label">Why {company}</p>
    <p>{html.escape(why_them)}</p>
  </section>

  <section class="plan">
    <p class="section-label">My first 30 days</p>
    <h2 class="lead">Less about my past. More about what I'd do for you.</h2>
    <ul>
{plan_cards}
    </ul>
  </section>

  <section class="creds">
    <p class="section-label">What I bring</p>
    <h2 class="lead">A physician's eye, a coach's warmth, a crossing guard's reliability.</h2>
    <ul>
{cert_chips}
    </ul>
  </section>

  <section class="cta">
    <h2>One honest conversation is all I'm asking for.</h2>
    <div class="buttons">
      <a class="btn btn-primary" href="mailto:{PROFILE['email']}?subject=Re:%20{title}%20at%20{company}">Email Sahawat</a>
      <a class="btn btn-secondary" href="{BOOK_CALL_URL}">Book a call</a>
    </div>
  </section>

  <footer>
    Sahawat Nilwatcharamanee &nbsp;·&nbsp; {PROFILE['phone']} &nbsp;·&nbsp;
    <a href="mailto:{PROFILE['email']}">{PROFILE['email']}</a> &nbsp;·&nbsp;
    <a href="https://{PROFILE['linkedin']}">LinkedIn</a>
  </footer>
</body>
</html>"""

    path = OUTPUT_DIR / f"{slug}.html"
    path.write_text(html_doc, encoding="utf-8")

    _record_manifest(slug, job["title"], job["company"], job.get("url", ""))

    return {"path": str(path), "slug": slug, "video_script": video_script}


def _record_manifest(slug: str, title: str, company: str, url: str):
    import json
    manifest_path = OUTPUT_DIR / "_manifest.json"
    data = {}
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text())
        except Exception:
            data = {}
    data[slug] = {"title": title, "company": company, "url": url}
    manifest_path.write_text(json.dumps(data, indent=2))


def build_index() -> str:
    """Build a private hub page listing every generated pitch microsite."""
    import json
    manifest_path = OUTPUT_DIR / "_manifest.json"
    if not manifest_path.exists():
        return ""
    data = json.loads(manifest_path.read_text())

    cards = "\n".join(
        f"""      <a class="card" href="{slug}">
        <span class="company">{html.escape(info['company'])}</span>
        <span class="title">{html.escape(info['title'])}</span>
        <span class="go">Open pitch &rarr;</span>
      </a>"""
        for slug, info in sorted(data.items(), key=lambda kv: kv[1]["company"])
    )

    index_html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="robots" content="noindex" />
<title>Sahawat — application pitches</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
<style>
  :root {{ --amber:#D4A843; --charcoal:#2C2C2C; --warm-white:#FAF7F2; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:"Inter",sans-serif; background:var(--charcoal); color:var(--warm-white); padding:clamp(2rem,6vw,6rem); }}
  h1 {{ font-family:"Playfair Display",serif; font-size:clamp(2rem,1rem+4vw,3.5rem); margin-bottom:0.5rem; }}
  h1 em {{ color:var(--amber); font-style:italic; }}
  .sub {{ color:rgba(250,247,242,0.6); margin-bottom:3rem; }}
  .grid {{ display:grid; gap:1.25rem; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); }}
  .card {{ display:flex; flex-direction:column; gap:0.4rem; padding:1.75rem; border-radius:12px;
    background:rgba(250,247,242,0.04); border:1px solid rgba(212,168,67,0.25); text-decoration:none;
    color:var(--warm-white); transition:transform 0.25s, border-color 0.25s; }}
  .card:hover {{ transform:translateY(-5px); border-color:var(--amber); }}
  .company {{ color:var(--amber); font-weight:600; font-size:0.85rem; letter-spacing:0.05em; }}
  .title {{ font-size:1.15rem; font-weight:600; }}
  .go {{ color:rgba(250,247,242,0.55); font-size:0.85rem; margin-top:0.5rem; }}
</style></head>
<body>
  <h1>Sahawat's <em>pitches</em></h1>
  <p class="sub">A personal application page for each role. Private — not indexed.</p>
  <div class="grid">
{cards}
  </div>
</body></html>"""

    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    return str(index_path)
