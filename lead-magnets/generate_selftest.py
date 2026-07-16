#!/usr/bin/env python3
"""The 60-Second Movement Self-Test — MoveAssess front-door lead magnet.

Renders two assets in the MoveAssess clinical brand (sage/beige, Fraunces +
IBM Plex Sans), via HTML -> shot-scraper (Chromium print), since weasyprint's
pango is broken on this machine:

  1. A4 PDF  -> ../physical-assessment-app/public/movement-self-test.pdf
                (hosted at physical-assessment-app.vercel.app/movement-self-test.pdf)
  2. 1080^2 PNG cover card -> ./movement-self-test-card.png (for social posts)

Content is authored here in a clinician's register — no marketing verbs, no
exclamation, no AI slop. Each test maps to a MoveAssess case that has a clean
hero image, so the deep link lands on an illustrated result.

Usage:
    python3 generate_selftest.py
"""

import html
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC = HERE.parent / "physical-assessment-app" / "public"
APP_URL = "https://physical-assessment-app.vercel.app"
PROGRAM_URL = "https://glute.crosswalkwisdom.com"

# --- Content ------------------------------------------------------------------
# Each: number, name, the test (how), the tell (a positive/fail sign), what it
# means (compensation + longevity stake), and the case id for the deep link.
TESTS = [
    {
        "n": "01",
        "name": "The Wall Head Test",
        "region": "Neck & upper back",
        "test": "Stand with your heels, backside, and shoulder blades touching a wall. "
                "Keep your chin level and try to touch the back of your head to the wall "
                "without tipping your face up.",
        "tell": "Your head won't reach the wall without craning your chin skyward.",
        "means": "Your head is living forward of your spine. Every inch forward multiplies "
                 "the load your neck carries all day — the pattern behind the stiff neck, "
                 "the tension headaches, and the rounded upper back that ages a silhouette.",
        "case": "forward-head-posture",
    },
    {
        "n": "02",
        "name": "The Overhead Squat",
        "region": "Knees & hips",
        "test": "Feet shoulder-width, arms straight overhead. Squat as low as you "
                "comfortably can, watching your knees in a mirror or on video.",
        "tell": "One or both knees drift inward, tracking inside the line of your big toe.",
        "means": "Your hip isn't controlling the knee, so the knee collapses to compensate. "
                 "This is the single most common driver of the knee pain that quietly ends "
                 "people's running, hiking, and stairs in their fifties.",
        "case": "patellofemoral-pain",
    },
    {
        "n": "03",
        "name": "The Single-Leg Stand",
        "region": "Hips & pelvis",
        "test": "Stand on one leg, hands on hips, and hold for ten seconds. Watch the "
                "hip of the lifted leg.",
        "tell": "The hip on the lifted side drops, or your torso lurches to stay upright.",
        "means": "The stance-side glute has gone quiet, so the pelvis can't stay level. "
                 "This is the leak behind low-back ache, IT-band pain, and the widening, "
                 "unsteady gait that reads as 'getting old' long before it has to.",
        "case": "right-hip-drop-left-shoulder",
    },
    {
        "n": "04",
        "name": "The Belt-Line Check",
        "region": "Low back & pelvis",
        "test": "Stand relaxed and sideways to a mirror. Look at the line of your "
                "waistband or belt from the side.",
        "tell": "The front of your belt line tips down and forward, with a pronounced arch "
                "in your lower back.",
        "means": "Your pelvis is tilted forward — tight hip flexors pulling, quiet glutes "
                 "and core letting go. It compresses the lower back with every step and is "
                 "the most common posture behind chronic morning stiffness.",
        "case": "apt-tight-hamstrings",
    },
    {
        "n": "05",
        "name": "The Arch Test",
        "region": "Feet & ankles",
        "test": "Stand barefoot, feet hip-width, and look down at your inner arches "
                "and ankles.",
        "tell": "The inner arches flatten toward the floor and the ankles roll inward.",
        "means": "The foundation is collapsing inward, and everything above it — knee, hip, "
                 "low back — rotates to follow. Overlooked for decades, it's the quiet "
                 "origin of pain three joints away.",
        "case": "pes-planus",
    },
    {
        "n": "06",
        "name": "The Wall Reach",
        "region": "Shoulders",
        "test": "Stand with your back to the wall, low back flat against it. Raise both "
                "arms overhead and try to touch the wall with the backs of your hands, "
                "keeping the low back flat.",
        "tell": "Your hands won't reach the wall, or your low back peels off to let them.",
        "means": "Your shoulders can't get overhead cleanly, so the low back cheats to "
                 "finish the motion. It's the pattern behind the shoulder that 'catches' "
                 "reaching for a seatbelt or a high shelf.",
        "case": "upper-crossed",
    },
    {
        "n": "07",
        "name": "The Chair Rise",
        "region": "Hips & core",
        "test": "Sit in a normal chair. Stand up without using your hands and without "
                "rocking forward for momentum.",
        "tell": "You need your hands, a rock forward, or a push off your thighs to get up.",
        "means": "The glutes and core aren't producing the power, so momentum stands in. "
                 "The ability to rise from a chair unaided is one of the strongest known "
                 "predictors of staying independent into your seventies and beyond.",
        "case": "flat-back-posture",
    },
]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
:root {
  --surface-0: #faf7f2; --surface-1: #f3eee5; --surface-2: #e8e0d2;
  --sage-400: #8ea085; --sage-500: #6f8768; --sage-600: #57694f; --sage-700: #435442;
  --terra: #c2503d; --ink: #232b24; --ink-soft: #4a544b;
  --hairline: rgba(35, 43, 36, 0.16);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
@page { size: A4; margin: 0; }
body {
  font-family: 'IBM Plex Sans', -apple-system, sans-serif;
  background: var(--surface-0); color: var(--ink);
  font-size: 10pt; line-height: 1.5; -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
.page { padding: 14mm 16mm 12mm; page-break-after: always; min-height: 297mm; position: relative; }
.page:last-child { page-break-after: auto; }
.brandbar {
  display: flex; justify-content: space-between; align-items: baseline;
  border-bottom: 1px solid var(--hairline); padding-bottom: 4mm; margin-bottom: 7mm;
}
.wordmark { font-family: 'Fraunces', Georgia, serif; font-weight: 600; letter-spacing: 0.02em; font-size: 12pt; }
.label { font-size: 7.5pt; text-transform: uppercase; letter-spacing: 0.14em; color: var(--sage-600); font-weight: 500; }

/* Cover masthead */
.kicker { font-size: 8pt; text-transform: uppercase; letter-spacing: 0.22em; color: var(--sage-600); font-weight: 600; }
h1 { font-family: 'Fraunces', Georgia, serif; font-size: 34pt; font-weight: 700; line-height: 1.02; margin: 4mm 0 4mm; max-width: 18ch; }
.standfirst { font-size: 12pt; line-height: 1.55; color: var(--ink-soft); max-width: 58ch; margin-bottom: 7mm; }
.how { background: var(--surface-1); border: 1px solid var(--hairline); padding: 5mm 6mm; max-width: 62ch; }
.how .label { margin-bottom: 2mm; }
.how p { color: var(--ink-soft); font-size: 9.5pt; }
.how b { color: var(--ink); }

/* Test blocks */
.test { display: grid; grid-template-columns: 16mm 1fr; gap: 5mm; padding: 5mm 0; border-top: 1px solid var(--hairline); page-break-inside: avoid; }
.test:first-of-type { border-top: none; }
.numeral { font-family: 'Fraunces', Georgia, serif; font-size: 30pt; line-height: 0.9; color: var(--sage-500); font-weight: 600; }
.test-region { font-size: 7pt; text-transform: uppercase; letter-spacing: 0.12em; color: var(--sage-400); margin-top: 2mm; }
.test-name { font-family: 'Fraunces', Georgia, serif; font-size: 15pt; font-weight: 600; margin-bottom: 2.5mm; }
.test-body p { margin-bottom: 2mm; max-width: 66ch; }
.test-body .do { color: var(--ink-soft); }
.tell { border-left: 2px solid var(--terra); padding-left: 4mm; margin: 2.5mm 0; }
.tell .lab { font-size: 7pt; text-transform: uppercase; letter-spacing: 0.12em; color: var(--terra); font-weight: 600; display: block; margin-bottom: 0.5mm; }
.tell p { font-weight: 500; color: var(--ink); }
.means { color: var(--ink-soft); font-size: 9.5pt; }
.means .lab { font-size: 7pt; text-transform: uppercase; letter-spacing: 0.12em; color: var(--sage-600); font-weight: 600; }

/* Scoring + CTA */
.score { background: var(--surface-1); border: 1px solid var(--hairline); padding: 6mm 7mm; margin-top: 6mm; max-width: 64ch; page-break-inside: avoid; }
.score h2 { font-family: 'Fraunces', Georgia, serif; font-size: 15pt; font-weight: 600; margin-bottom: 2.5mm; }
.score p { color: var(--ink-soft); font-size: 9.5pt; margin-bottom: 2mm; }
.cta { background: var(--sage-700); color: var(--surface-0); padding: 7mm 8mm; margin-top: 6mm; max-width: 64ch; page-break-inside: avoid; }
.cta .label { color: var(--sage-400); }
.cta h2 { font-family: 'Fraunces', Georgia, serif; font-size: 17pt; font-weight: 600; margin: 2mm 0 3mm; color: var(--surface-0); }
.cta p { font-size: 10pt; line-height: 1.55; color: rgba(250,247,242,0.9); margin-bottom: 3mm; }
.cta a { color: var(--surface-0); font-weight: 600; }
footer {
  position: absolute; bottom: 8mm; left: 16mm; right: 16mm;
  border-top: 1px solid var(--hairline); padding-top: 3mm;
  display: flex; justify-content: space-between; font-size: 8pt; color: var(--ink-soft);
}
footer a { color: var(--sage-700); text-decoration: none; }
"""


def esc(value: str) -> str:
    return html.escape(value, quote=False)


def test_block(t: dict) -> str:
    return f"""<div class="test">
  <div><div class="numeral">{esc(t['n'])}</div><div class="test-region">{esc(t['region'])}</div></div>
  <div class="test-body">
    <div class="test-name">{esc(t['name'])}</div>
    <p class="do"><b>The test.</b> {esc(t['test'])}</p>
    <div class="tell"><span class="lab">The tell</span><p>{esc(t['tell'])}</p></div>
    <p class="means"><span class="lab">What it means · </span>{esc(t['means'])}</p>
  </div>
</div>"""


def build_pdf_html() -> str:
    first = "".join(test_block(t) for t in TESTS[:4])
    rest = "".join(test_block(t) for t in TESTS[4:])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="page">
  <div class="brandbar"><span class="wordmark">MOVEASSESS</span><span class="label">Crosswalk Wisdom · Movement Diagnostics</span></div>
  <p class="kicker">The Free Self-Assessment</p>
  <h1>The 60-Second Movement Self-Test</h1>
  <p class="standfirst">Seven quick checks a clinician uses to find where a body will break down first.
  No equipment, no floor work — a wall, a chair, and a mirror. Each one you fail points to a specific
  pattern you can still change.</p>
  <div class="how"><p class="label">How to use this</p><p>Work through all seven. For each, note whether
  you see <b>the tell</b>. Fewer than three: you're moving well — keep the reserve. <b>Three or more:
  you're carrying measurable movement debt</b>, and it compounds every year you leave it. The last page
  tells you what to do with your score.</p></div>
  {first}
  <footer><span>Crosswalk Wisdom — From the Ward to the World</span><a href="{PROGRAM_URL}">{PROGRAM_URL.replace('https://','')}</a></footer>
</div>
<div class="page">
  <div class="brandbar"><span class="wordmark">MOVEASSESS</span><span class="label">The 60-Second Movement Self-Test</span></div>
  {rest}
  <div class="score">
    <h2>What your score means</h2>
    <p><b>0–2 tells.</b> You have movement in reserve. The goal now is to keep it — the same patterns
    creep back in with another decade at a desk.</p>
    <p><b>3–5 tells.</b> Movement debt is accumulating. Each tell is one joint compensating for another,
    and the bill usually arrives as pain somewhere else entirely.</p>
    <p><b>6–7 tells.</b> Multiple links in the chain are offline. This is eminently fixable, but it
    won't resolve on its own — it needs the right sequence, in the right order.</p>
  </div>
  <div class="cta">
    <p class="label">The next 60 seconds</p>
    <h2>See exactly which pattern is yours — and the fix for it</h2>
    <p>The tells above tell you <i>that</i> something's off. The free MoveAssess assessment shows you
    <i>which</i> pattern, in 3D, with the specific muscles that have gone quiet and the ones doing their
    job — then sends you the corrective protocol built for it. Do it for 14 days and retest.</p>
    <p>Start free: <a href="{APP_URL}">{APP_URL.replace('https://','')}</a><br>
    The 6-week program, if you'd rather be coached through it: <a href="{PROGRAM_URL}">{PROGRAM_URL.replace('https://','')}</a></p>
  </div>
  <footer><span>Crosswalk Wisdom — From the Ward to the World</span><a href="{PROGRAM_URL}">{PROGRAM_URL.replace('https://','')}</a></footer>
</div>
</body></html>"""


CARD_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
body { width: 1080px; height: 1080px; overflow: hidden;
  font-family: 'IBM Plex Sans', sans-serif; background: #faf7f2; color: #232b24;
  -webkit-print-color-adjust: exact; }
.card { width: 1080px; height: 1080px; padding: 96px 88px; display: flex; flex-direction: column; justify-content: space-between; position: relative; }
.card::before { content: ""; position: absolute; inset: 40px; border: 1px solid rgba(35,43,36,0.16); pointer-events: none; }
.top { display: flex; justify-content: space-between; align-items: baseline; }
.wm { font-family: 'Fraunces', serif; font-weight: 600; font-size: 30px; letter-spacing: 0.02em; }
.lab { font-size: 17px; text-transform: uppercase; letter-spacing: 0.22em; color: #57694f; font-weight: 600; }
.mid { }
.kick { font-size: 20px; text-transform: uppercase; letter-spacing: 0.24em; color: #6f8768; font-weight: 600; margin-bottom: 26px; }
h1 { font-family: 'Fraunces', serif; font-weight: 700; font-size: 104px; line-height: 0.98; letter-spacing: -0.01em; }
h1 .n { color: #6f8768; }
.sub { font-size: 30px; line-height: 1.45; color: #4a544b; margin-top: 34px; max-width: 20ch; }
.strip { display: flex; gap: 10px; margin-top: 46px; }
.strip span { height: 8px; flex: 1; background: #e8e0d2; border-radius: 4px; }
.strip span:nth-child(-n+5) { background: #6f8768; }
.bottom { display: flex; justify-content: space-between; align-items: flex-end; }
.bottom .foot { font-size: 20px; color: #4a544b; }
.bottom .cue { font-family: 'Fraunces', serif; font-style: italic; font-size: 24px; color: #57694f; }
"""


def build_card_html() -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CARD_CSS}</style></head><body>
<div class="card">
  <div class="top"><span class="wm">MOVEASSESS</span><span class="lab">Free Self-Test</span></div>
  <div class="mid">
    <div class="kick">7 checks · no equipment</div>
    <h1>The <span class="n">60-Second</span><br>Movement<br>Self-Test</h1>
    <p class="sub">Find where your body breaks down first — before it costs you a decade of mobility.</p>
    <div class="strip"><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
  </div>
  <div class="bottom">
    <span class="foot">Crosswalk Wisdom — From the Ward to the World</span>
    <span class="cue">A wall. A chair. A mirror.</span>
  </div>
</div>
</body></html>"""


def render_pdf(out_pdf: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as tmp:
        tmp.write(build_pdf_html())
        tmp_path = tmp.name
    subprocess.run(["shot-scraper", "pdf", tmp_path, "-o", str(out_pdf),
                    "--wait", "1500", "--print-background"], check=True, capture_output=True)
    Path(tmp_path).unlink()


def render_card(out_png: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as tmp:
        tmp.write(build_card_html())
        tmp_path = tmp.name
    subprocess.run(["shot-scraper", "shot", tmp_path, "-o", str(out_png),
                    "--width", "1080", "--height", "1080", "--wait", "1500"],
                   check=True, capture_output=True)
    Path(tmp_path).unlink()


def main() -> int:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    pdf = PUBLIC / "movement-self-test.pdf"
    card = HERE / "movement-self-test-card.png"
    render_pdf(pdf)
    render_card(card)
    print(f"  PDF  {pdf}  ({pdf.stat().st_size // 1024} KB)")
    print(f"  CARD {card}  ({card.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
