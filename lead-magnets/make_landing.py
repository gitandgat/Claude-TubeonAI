#!/usr/bin/env python3
"""
Stamp out a branded lead-magnet landing page (Vite public/ static HTML) from a
magnet's schema JSON + a small config. Posts to the website's /api/lead-capture
with a tag; reveals an instant PDF download on success.

    python make_landing.py --json lm-inner-voices.json --slug inner-voices \
      --badge "If you feel stuck" --lead "You're not lazy." --emph "You're out-argued by your own mind." \
      --pdf the-5-inner-voices.pdf --tag lead-magnet-inner-voices --out /tmp/inner-voices.html
"""

import argparse
import html
import json
from pathlib import Path

TH = {"amber": "#D4A843", "charcoal": "#2C2C2C", "warm": "#FAF7F2", "orange": "#E8834A", "teal": "#5B9A8B"}


def esc(v):
    return html.escape(str(v or ""))


def build(data, slug, badge, lead, emph, pdf, tag):
    # "What's inside" = the four section headings of the guide.
    inside = [data.get(f"section{n}Heading", "") for n in ("Two", "Three", "Four", "Five")]
    inside_li = "".join(f"<li>{esc(x)}</li>" for x in inside if x)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(data.get('title'))} — Crosswalk Wisdom</title>
<meta name="description" content="{esc(data.get('subheading'))}">
<link rel="canonical" href="https://www.crosswalkwisdom.com/{esc(slug)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--amber:{TH['amber']};--charcoal:{TH['charcoal']};--warm:{TH['warm']};--orange:{TH['orange']};--teal:{TH['teal']};
--serif:"Playfair Display",Georgia,serif;--sans:"Inter",system-ui,sans-serif;--space:clamp(1.5rem,1rem + 3vw,4rem);}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:var(--sans);background:var(--charcoal);color:var(--warm);line-height:1.6}}
.wrap{{max-width:1080px;margin:0 auto;padding:var(--space)}}
header{{display:flex;align-items:center;gap:12px;padding:clamp(1rem,2vw,2rem) var(--space)}}
.stripes{{display:flex;flex-direction:column;gap:3px}}
.stripes span{{display:block;width:32px;height:6px;border-radius:2px;background:var(--amber)}}
.stripes span:nth-child(even){{opacity:.6}}
.wordmark{{font-family:var(--serif);font-weight:700;font-size:1.25rem;color:var(--amber);letter-spacing:-.02em}}
.hero{{display:grid;grid-template-columns:1.2fr 1fr;gap:clamp(2rem,4vw,4rem);align-items:center}}
@media(max-width:820px){{.hero{{grid-template-columns:1fr}}}}
.badge{{display:inline-block;background:var(--teal);color:var(--warm);font-weight:600;font-size:.8rem;letter-spacing:.14em;
text-transform:uppercase;padding:.5rem 1rem;border-radius:999px;margin-bottom:1.25rem}}
h1{{font-family:var(--serif);font-weight:800;line-height:1.05;font-size:clamp(2.2rem,1.4rem + 4vw,3.8rem)}}
h1 .accent{{color:var(--amber);display:block}}
.sub{{font-size:clamp(1.05rem,1rem + .4vw,1.25rem);color:rgba(250,247,242,.85);margin-top:1.25rem;max-width:46ch}}
.inside{{list-style:none;margin-top:1.75rem;display:grid;gap:.75rem}}
.inside li{{position:relative;padding-left:1.75rem}}
.inside li::before{{content:"";position:absolute;left:0;top:.55em;width:10px;height:10px;background:var(--orange);border-radius:2px;transform:rotate(45deg)}}
.card{{background:var(--warm);color:var(--charcoal);border-radius:14px;padding:clamp(1.5rem,3vw,2.5rem);box-shadow:0 24px 60px rgba(0,0,0,.35)}}
.card h2{{font-family:var(--serif);font-size:1.6rem;line-height:1.2;margin-bottom:.5rem}}
.card p.lead{{color:#5a5346;font-size:.98rem;margin-bottom:1.25rem}}
.field{{margin-bottom:.9rem}}
label{{display:block;font-size:.82rem;font-weight:600;margin-bottom:.35rem;color:#4a443a}}
input{{width:100%;padding:.85rem 1rem;border:1.5px solid #e0d8c9;border-radius:8px;font-size:1rem;font-family:var(--sans);background:#fff;transition:border-color 150ms}}
input:focus{{outline:none;border-color:var(--amber)}}
.btn{{width:100%;margin-top:.5rem;background:var(--amber);color:var(--charcoal);border:none;border-radius:8px;padding:1rem;font-size:1.05rem;font-weight:700;font-family:var(--sans);cursor:pointer;transition:transform 150ms,filter 150ms}}
.btn:hover{{transform:translateY(-1px);filter:brightness(1.05)}}
.btn:disabled{{opacity:.6;cursor:default;transform:none}}
.reassure{{font-size:.78rem;color:#8a8278;margin-top:.9rem;text-align:center}}
.msg{{margin-top:1rem;font-size:.95rem;border-radius:8px;padding:.85rem 1rem;display:none}}
.msg.ok{{display:block;background:#eaf3f0;color:#2f6b5b}}
.msg.err{{display:block;background:#fbeae6;color:#b4452b}}
.download{{display:none;width:100%;margin-top:1rem;text-align:center;background:var(--teal);color:var(--warm);text-decoration:none;font-weight:700;padding:.9rem 1rem;border-radius:8px;box-sizing:border-box}}
.download:hover{{filter:brightness(1.05)}}
footer{{text-align:center;padding:2rem var(--space) 3rem;color:rgba(250,247,242,.55);font-size:.82rem}}
.tagline{{font-family:var(--serif);font-style:italic;color:var(--amber)}}
</style></head>
<body>
<header><div class="stripes" aria-hidden="true"><span></span><span></span><span></span><span></span></div><span class="wordmark">Crosswalk Wisdom</span></header>
<main class="wrap">
  <section class="hero" aria-labelledby="h">
    <div>
      <span class="badge">{esc(badge)}</span>
      <h1 id="h">{esc(lead)} <span class="accent">{esc(emph)}</span></h1>
      <p class="sub">{esc(data.get('subheading'))}</p>
      <ul class="inside">{inside_li}</ul>
    </div>
    <div class="card">
      <h2>Get the free guide</h2>
      <p class="lead">Enter your details and download it instantly.</p>
      <form id="f" novalidate>
        <div class="field"><label for="firstName">First name</label><input id="firstName" type="text" autocomplete="given-name" required></div>
        <div class="field"><label for="email">Email</label><input id="email" type="email" autocomplete="email" required></div>
        <button class="btn" type="submit" id="b">Send me the guide</button>
        <p class="reassure">No spam. Unsubscribe anytime.</p>
        <div class="msg" id="m" role="status" aria-live="polite"></div>
        <a class="download" id="d" href="/{esc(pdf)}" download>Download the guide (PDF) &rarr;</a>
      </form>
    </div>
  </section>
</main>
<footer><p class="tagline">From the Ward to the World</p><p>&copy; <span id="y"></span> Crosswalk Wisdom · 2 Kingsdale Ave, North York, ON M2N 3W1</p></footer>
<script>
document.getElementById('y').textContent=new Date().getFullYear();
const f=document.getElementById('f'),b=document.getElementById('b'),m=document.getElementById('m');
f.addEventListener('submit',async e=>{{
  e.preventDefault();
  const firstName=document.getElementById('firstName').value.trim();
  const email=document.getElementById('email').value.trim();
  m.className='msg';
  if(!firstName||!email||!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)){{m.textContent='Please enter your first name and a valid email.';m.classList.add('err');return;}}
  b.disabled=true;b.textContent='Sending…';
  try{{
    const r=await fetch('/api/lead-capture',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email,firstName,tag:'{esc(tag)}'}})}});
    if(!r.ok)throw new Error('failed');
    await r.json();
    m.textContent=`You're in, ${{firstName}}. Your guide is ready below.`;m.classList.add('ok');
    document.getElementById('d').style.display='block';f.reset();
  }}catch(err){{m.textContent='Something went wrong. Please try again, or email hello@crosswalkwisdom.com.';m.classList.add('err');}}
  finally{{b.disabled=false;b.textContent='Send me the guide';}}
}});
</script>
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--badge", required=True)
    ap.add_argument("--lead", required=True)
    ap.add_argument("--emph", required=True)
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    data = json.loads(Path(a.json).read_text(encoding="utf-8"))
    Path(a.out).write_text(build(data, a.slug, a.badge, a.lead, a.emph, a.pdf, a.tag), encoding="utf-8")
    print(f"✓ {a.out}")


if __name__ == "__main__":
    main()
