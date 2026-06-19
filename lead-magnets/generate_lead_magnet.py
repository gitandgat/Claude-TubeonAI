#!/usr/bin/env python3
"""
Lead Magnet Generator — the Claude Code replacement for the Make.com scenario.

Two modes:
  1. RENDER (default): take a schema JSON and produce a branded PDF.
       python generate_lead_magnet.py crosswalk-img-pivot-map.json

  2. GENERATE + RENDER: take a topic/summary, write the JSON via the repo's
     AI client factory (Ollama free → Claude fallback), then render the PDF.
       python generate_lead_magnet.py --topic "..." --summary "..."

The JSON schema matches the Make scenario exactly (title, subheading, five
sections with escalating subheadings/paragraphs) so the same content drops
into any pipeline that expects that shape.

PDF rendering uses the `weasyprint` CLI (already installed), so this script
runs under any python3 — no extra imports needed for render mode.
"""

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _which(cmd):
    return shutil.which(cmd)

# --- Brand theme (mirrors crosswalk-remotion/src/theme.ts) --------------------
THEME = {
    "amber": "#D4A843",
    "charcoal": "#2C2C2C",
    "warmWhite": "#FAF7F2",
    "orange": "#E8834A",
    "teal": "#5B9A8B",
    "black": "#1A1A1A",
}
BRAND = "Crosswalk Wisdom"
TAGLINE = "From the Ward to the World"

# Section shapes: how many (subheading, paragraph) pairs per section.
SECTION_PAIRS = {"Two": 2, "Three": 3, "Four": 4, "Five": 6}
ORDINALS = ["One", "Two", "Three", "Four", "Five", "Six"]


# --- AI generation (replaces the GPT-4 step in the Make scenario) -------------
SYSTEM_PROMPT = "You are a helpful, intelligent writing assistant."

# Same field contract the Make scenario enforced, so output is pipeline-shaped.
REQUIRED_FIELDS = (
    "title, subheading, sectionOneHeading, sectionTwoHeading, sectionThreeHeading, "
    "sectionFourHeading, sectionFiveHeading, sectionOneParagraph, sectionOneBulletOne, "
    "sectionOneBulletTwo, sectionTwoSubheadingOne, sectionTwoSubheadingTwo, "
    "sectionTwoParagraphOne, sectionTwoParagraphTwo, sectionThreeSubheadingOne, "
    "sectionThreeSubheadingTwo, sectionThreeSubheadingThree, sectionThreeParagraphOne, "
    "sectionThreeParagraphTwo, sectionThreeParagraphThree, sectionFourSubheadingOne, "
    "sectionFourSubheadingTwo, sectionFourSubheadingThree, sectionFourSubheadingFour, "
    "sectionFourParagraphOne, sectionFourParagraphTwo, sectionFourParagraphThree, "
    "sectionFourParagraphFour, sectionFiveSubheadingOne, sectionFiveSubheadingTwo, "
    "sectionFiveSubheadingThree, sectionFiveSubheadingFour, sectionFiveSubheadingFive, "
    "sectionFiveSubheadingSix, sectionFiveParagraphOne, sectionFiveParagraphTwo, "
    "sectionFiveParagraphThree, sectionFiveParagraphFour, sectionFiveParagraphFive, "
    "sectionFiveParagraphSix"
)

USER_INSTRUCTION = (
    "Using the following input, generate high quality copy for a lead magnet in JSON. "
    "Write in a human, specific, contrarian voice — no AI cliches, no 'in today's world', "
    "no 'unlock/delve/navigate/elevate'. Use the reframe pattern 'X isn't the question, Y is' "
    "where it fits. Return ONLY raw JSON (no markdown fences). Ensure every one of these "
    f"variables is present: {REQUIRED_FIELDS}."
)


def extract_json(text):
    """Strip markdown fences / prose and parse the first JSON object.

    Guards against the 'Expecting value: line 1' failure mode where the model
    wraps JSON in ```json fences.
    """
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        brace = re.search(r"\{.*\}", text, re.DOTALL)
        if brace:
            text = brace.group(0)
    return json.loads(text)


def ai_generate(topic, summary, company=BRAND):
    """Generate schema JSON via the repo's AI client factory (free-first)."""
    sys.path.insert(0, str(HERE.parent))
    # Load repo .env so provider keys (ANTHROPIC/GROQ/OPENAI) are available.
    try:
        from dotenv import load_dotenv
        load_dotenv(HERE.parent / ".env")
    except ImportError:
        pass
    from ai_client_factory import get_ai_client  # noqa: E402

    payload = json.dumps({"topic": topic, "summary": summary, "yourCompanyName": company})
    messages = [
        {"role": "user", "content": USER_INSTRUCTION},
        {"role": "user", "content": payload},
    ]

    provider, client = get_ai_client()
    if provider == "claude":
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2500,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        raw = resp.content[0].text
    else:  # ollama / groq wrappers expose .create(messages, system, max_tokens)
        resp = client.create(messages=messages, system=SYSTEM_PROMPT, max_tokens=2500)
        raw = resp.content[0].text

    return _normalize(extract_json(raw))


def _normalize(data):
    """Strip AI-slop punctuation (em/en dashes) from all string values."""
    def fix(s):
        return (s.replace(" — ", ", ").replace("—", ", ")
                 .replace(" – ", ", ").replace("–", "-")) if isinstance(s, str) else s
    return {k: fix(v) for k, v in data.items()}


# --- HTML rendering -----------------------------------------------------------
def esc(value):
    return html.escape(str(value or "")).replace("\n", "<br>")


def section_block(data, num, ordinal, kicker):
    """Render one numbered content section (subheading/paragraph pairs)."""
    heading = data.get(f"section{ordinal}Heading", "")
    rows = []

    if ordinal == "One":
        rows.append(f'<p class="lede">{esc(data.get("sectionOneParagraph"))}</p>')
        bullets = [data.get("sectionOneBulletOne"), data.get("sectionOneBulletTwo")]
        bullets = "".join(f"<li>{esc(b)}</li>" for b in bullets if b)
        if bullets:
            rows.append(f'<ul class="takeaways">{bullets}</ul>')
    else:
        numbered = ordinal == "Five"  # final section reads as an action plan
        items = []
        for i in range(SECTION_PAIRS[ordinal]):
            sub = data.get(f"section{ordinal}Subheading{ORDINALS[i]}")
            para = data.get(f"section{ordinal}Paragraph{ORDINALS[i]}")
            if not (sub or para):
                continue
            step = f'<span class="step">{i + 1}</span>' if numbered else ""
            items.append(
                f'<div class="item{" numbered" if numbered else ""}">{step}'
                f'<div class="item-body"><h3>{esc(sub)}</h3><p>{esc(para)}</p></div></div>'
            )
        rows.append('<div class="items">' + "".join(items) + "</div>")

    return (
        f'<section class="content">'
        f'<div class="sec-head"><span class="sec-num">{num:02d}</span>'
        f'<span class="kicker">{kicker}</span></div>'
        f'<h2>{esc(heading)}</h2>'
        + "".join(rows)
        + "</section>"
    )


def build_html(data, cta=None):
    sections = [
        section_block(data, 1, "One", "The trap"),
        section_block(data, 2, "Two", "The reframe"),
        section_block(data, 3, "Three", "Your assets"),
        section_block(data, 4, "Four", "The paths"),
        section_block(data, 5, "Five", "The plan"),
    ]
    cta_html = ""
    if cta:
        cta_html = (
            f'<section class="cta"><h2>{esc(cta.get("heading", "Where to go next"))}</h2>'
            f'<p>{esc(cta.get("body", ""))}</p>'
            f'<p class="cta-link">{esc(cta.get("link", ""))}</p></section>'
        )

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;800&family=Inter:wght@400;500;600&display=swap');
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Inter', system-ui, sans-serif; color: {THEME['charcoal']};
  background: {THEME['warmWhite']}; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
h1, h2, h3 {{ font-family: 'Playfair Display', Georgia, serif; }}

/* Cover */
.cover {{ height: 297mm; padding: 30mm 24mm; background: {THEME['charcoal']};
  color: {THEME['warmWhite']}; display: flex; flex-direction: column;
  justify-content: space-between; page-break-after: always; }}
/* Logo lockup (mirrors crosswalk-remotion Logo.tsx: 4 amber stripes + wordmark) */
.logo {{ display: flex; align-items: center; gap: 11px; }}
.logo .stripes {{ display: flex; flex-direction: column; gap: 3px; }}
.logo .stripes span {{ display: block; width: 30px; height: 5.4px; border-radius: 2px;
  background: {THEME['amber']}; }}
.logo .stripes span:nth-child(even) {{ opacity: .6; }}
.logo .word {{ font-family: 'Playfair Display', serif; font-weight: 700; font-size: 18pt;
  letter-spacing: -0.02em; color: {THEME['amber']}; line-height: 1; }}
.cover .brand {{ font-size: 13pt; letter-spacing: .28em; text-transform: uppercase;
  color: {THEME['amber']}; font-weight: 600; }}
.cover .rule {{ width: 64px; height: 5px; background: {THEME['amber']}; margin: 0 0 22px; }}
.cover h1 {{ font-size: 46pt; line-height: 1.05; font-weight: 800; max-width: 15ch; }}
.cover .sub {{ font-size: 15pt; line-height: 1.5; margin-top: 20px; max-width: 44ch;
  color: rgba(250,247,242,0.88); }}
.cover .tagline {{ font-family: 'Playfair Display', serif; font-style: italic;
  font-size: 14pt; color: {THEME['amber']}; }}

/* Content */
.content {{ padding: 20mm 24mm; page-break-inside: avoid; }}
.sec-head {{ display: flex; align-items: baseline; gap: 14px; margin-bottom: 6px; }}
.sec-num {{ font-family: 'Playfair Display', serif; font-weight: 800; font-size: 30pt;
  color: {THEME['amber']}; line-height: 1; }}
.kicker {{ font-size: 10pt; letter-spacing: .22em; text-transform: uppercase;
  color: {THEME['teal']}; font-weight: 600; }}
.content h2 {{ font-size: 24pt; line-height: 1.15; font-weight: 700; max-width: 22ch;
  margin-bottom: 16px; }}
.content p {{ font-size: 11.5pt; line-height: 1.62; color: #3a3a3a; }}
.lede {{ font-size: 12.5pt !important; line-height: 1.66 !important; }}
.takeaways {{ list-style: none; margin-top: 16px; }}
.takeaways li {{ position: relative; padding-left: 26px; margin-bottom: 10px;
  font-size: 11.5pt; line-height: 1.55; }}
.takeaways li::before {{ content: ""; position: absolute; left: 0; top: 7px;
  width: 10px; height: 10px; background: {THEME['orange']}; border-radius: 2px;
  transform: rotate(45deg); }}
.items {{ margin-top: 4px; }}
.item {{ margin-top: 18px; border-left: 3px solid {THEME['amber']}; padding-left: 16px; }}
.item.numbered {{ display: flex; gap: 14px; border-left: none; padding-left: 0; }}
.step {{ flex: 0 0 auto; width: 30px; height: 30px; border-radius: 50%;
  background: {THEME['teal']}; color: {THEME['warmWhite']}; font-weight: 600;
  font-family: 'Inter'; font-size: 13pt; display: flex; align-items: center;
  justify-content: center; }}
.item h3 {{ font-size: 14pt; margin-bottom: 5px; color: {THEME['charcoal']}; }}

/* CTA */
.cta {{ margin: 8mm 24mm 20mm; padding: 14mm; background: {THEME['amber']};
  color: {THEME['charcoal']}; border-radius: 6px; page-break-inside: avoid; }}
.cta h2 {{ font-size: 22pt; margin-bottom: 10px; }}
.cta p {{ font-size: 12pt; line-height: 1.6; }}
.cta-link {{ margin-top: 12px; font-weight: 600; }}
.foot {{ text-align: center; padding: 0 0 16mm; font-size: 9pt; color: #8a8278;
  letter-spacing: .04em; }}
</style></head>
<body>
  <div class="cover">
    <div class="logo">
      <div class="stripes"><span></span><span></span><span></span><span></span></div>
      <div class="word">{esc(BRAND)}</div>
    </div>
    <div>
      <div class="rule"></div>
      <h1>{esc(data.get('title'))}</h1>
      <p class="sub">{esc(data.get('subheading'))}</p>
    </div>
    <div class="tagline">{esc(TAGLINE)}</div>
  </div>
  {''.join(sections)}
  {cta_html}
  <div class="foot">{esc(BRAND)} &nbsp;·&nbsp; {esc(TAGLINE)} &nbsp;·&nbsp; {date.today():%B %Y}</div>
</body></html>"""


def render_pdf(data, out_stem, cta=None):
    html_path = HERE / f"{out_stem}.html"
    pdf_path = HERE / f"{out_stem}.pdf"
    html_path.write_text(build_html(data, cta=cta), encoding="utf-8")

    # Prefer shot-scraper (headless Chromium) — renders web fonts + CSS faithfully
    # and prints backgrounds. Fall back to weasyprint if it isn't available.
    if _which("shot-scraper"):
        subprocess.run(
            ["shot-scraper", "pdf", str(html_path), "-o", str(pdf_path),
             "--format", "a4", "--print-background", "--wait", "1500", "--silent"],
            check=True,
        )
    elif _which("weasyprint"):
        subprocess.run(["weasyprint", str(html_path), str(pdf_path)], check=True)
    else:
        raise RuntimeError("No PDF renderer found. Install shot-scraper or weasyprint.")
    return pdf_path


# Default CTA for the Crosswalk IMG funnel.
DEFAULT_CTA = {
    "heading": "You've seen the map. Now make the call.",
    "body": ("The hard part isn't the plan — it's deciding, because deciding is exactly what "
             "sunk cost is built to stop. Take the Fear Audit to find which layer of the trap "
             "is holding you, then read The Courage to Choose for the full framework."),
    "link": "crosswalkwisdom.com",
}


def main():
    ap = argparse.ArgumentParser(description="Generate a branded lead-magnet PDF.")
    ap.add_argument("json_file", nargs="?", default="crosswalk-img-pivot-map.json",
                    help="Schema JSON to render (default: the IMG Pivot Map).")
    ap.add_argument("--topic", help="Generate fresh JSON for this topic via the AI factory.")
    ap.add_argument("--summary", default="", help="Summary of points to make (with --topic).")
    ap.add_argument("--company", default=BRAND, help="Company name for generated copy.")
    ap.add_argument("--out", help="Output filename stem (no extension).")
    ap.add_argument("--no-cta", action="store_true", help="Skip the closing CTA block.")
    args = ap.parse_args()

    if args.topic:
        print(f"Generating copy for: {args.topic}")
        data = ai_generate(args.topic, args.summary, company=args.company)
        stem = args.out or "lead-magnet-" + re.sub(r"[^a-z0-9]+", "-", args.topic.lower()).strip("-")
        (HERE / f"{stem}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"✓ Saved {stem}.json")
    else:
        path = Path(args.json_file)
        if not path.is_absolute():
            path = HERE / path
        data = json.loads(path.read_text(encoding="utf-8"))
        stem = args.out or path.stem

    cta = None if args.no_cta else DEFAULT_CTA
    pdf = render_pdf(data, stem, cta=cta)
    print(f"✓ PDF: {pdf}  ({pdf.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
