#!/usr/bin/env python3
"""
Social promo visual for a lead magnet — 1080x1080 PNG, on the Crosswalk theme.

Renders an HTML card via shot-scraper (headless Chromium), matching the rule
that every social post ships with a 1080x1080 visual in the brand theme.

    python generate_social_visual.py                       # uses the IMG Pivot Map
    python generate_social_visual.py --json other.json --hook "Custom hook line."
"""

import argparse
import html
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent

THEME = {
    "amber": "#D4A843",
    "charcoal": "#2C2C2C",
    "warmWhite": "#FAF7F2",
    "orange": "#E8834A",
    "teal": "#5B9A8B",
}
BRAND = "Crosswalk Wisdom"
TAGLINE = "From the Ward to the World"

# Default scroll-stopping hook for the IMG Pivot Map. The first clause is plain,
# the emphasized clause is the reframe.
DEFAULT_HOOK_LEAD = "You didn't waste those years in medicine."
DEFAULT_HOOK_EMPHASIS = "You just haven't been shown what they're worth."


def esc(value):
    return html.escape(str(value or ""))


def build_html(title, hook_lead, hook_emphasis, badge):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;800&family=Inter:wght@400;500;600;700&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1080px; }}
body {{ font-family: 'Inter', system-ui, sans-serif; background: {THEME['charcoal']};
  color: {THEME['warmWhite']}; -webkit-print-color-adjust: exact;
  padding: 84px 80px; display: flex; flex-direction: column; justify-content: space-between;
  position: relative; overflow: hidden; }}
/* amber glow accent, top-right */
body::before {{ content: ""; position: absolute; top: -180px; right: -180px; width: 520px;
  height: 520px; border-radius: 50%;
  background: radial-gradient(circle, rgba(212,168,67,0.18), transparent 70%); }}

.logo {{ display: flex; align-items: center; gap: 16px; z-index: 1; }}
.logo .stripes {{ display: flex; flex-direction: column; gap: 6px; }}
.logo .stripes span {{ display: block; width: 56px; height: 11px; border-radius: 3px;
  background: {THEME['amber']}; }}
.logo .stripes span:nth-child(even) {{ opacity: .6; }}
.logo .word {{ font-family: 'Playfair Display', serif; font-weight: 700; font-size: 38px;
  letter-spacing: -0.02em; color: {THEME['amber']}; }}

.badge {{ display: inline-block; align-self: flex-start; margin-bottom: 30px;
  background: {THEME['teal']}; color: {THEME['warmWhite']}; font-weight: 600;
  font-size: 22px; letter-spacing: .14em; text-transform: uppercase;
  padding: 12px 22px; border-radius: 999px; z-index: 1; }}
.hook {{ font-family: 'Playfair Display', serif; font-weight: 800; line-height: 1.04;
  z-index: 1; }}
.hook .lead {{ font-size: 78px; color: {THEME['warmWhite']}; display: block; }}
.hook .emph {{ font-size: 78px; color: {THEME['amber']}; display: block; margin-top: 8px; }}
.offer {{ z-index: 1; }}
.offer .label {{ font-size: 24px; letter-spacing: .2em; text-transform: uppercase;
  color: {THEME['orange']}; font-weight: 600; margin-bottom: 12px; }}
.offer .title {{ font-family: 'Playfair Display', serif; font-size: 40px; font-weight: 600;
  color: {THEME['warmWhite']}; }}

.foot {{ display: flex; align-items: center; justify-content: space-between; z-index: 1; }}
.foot .tagline {{ font-family: 'Playfair Display', serif; font-style: italic; font-size: 30px;
  color: {THEME['amber']}; }}
.foot .cta {{ background: {THEME['amber']}; color: {THEME['charcoal']}; font-weight: 700;
  font-size: 28px; padding: 16px 30px; border-radius: 8px; }}
/* crosswalk stripe motif, bottom edge */
.stripe-motif {{ position: absolute; left: 0; bottom: 0; width: 100%; height: 14px;
  display: flex; }}
.stripe-motif span {{ flex: 1; background: {THEME['amber']}; }}
.stripe-motif span:nth-child(even) {{ background: transparent; }}
</style></head>
<body>
  <div class="logo">
    <div class="stripes"><span></span><span></span><span></span><span></span></div>
    <div class="word">{esc(BRAND)}</div>
  </div>

  <div>
    <span class="badge">{esc(badge)}</span>
    <div class="hook">
      <span class="lead">{esc(hook_lead)}</span>
      <span class="emph">{esc(hook_emphasis)}</span>
    </div>
  </div>

  <div class="offer">
    <div class="label">Free guide</div>
    <div class="title">{esc(title)}</div>
  </div>

  <div class="foot">
    <span class="tagline">{esc(TAGLINE)}</span>
    <span class="cta">Get the free PDF &rarr;</span>
  </div>

  <div class="stripe-motif">
    {''.join('<span></span>' for _ in range(20))}
  </div>
</body></html>"""


def render(html_str, out_stem):
    html_path = HERE / f"{out_stem}.html"
    png_path = HERE / f"{out_stem}.png"
    html_path.write_text(html_str, encoding="utf-8")
    subprocess.run(
        ["shot-scraper", "shot", str(html_path), "-o", str(png_path),
         "--width", "1080", "--height", "1080", "--wait", "1500", "--silent"],
        check=True,
    )
    return png_path


def main():
    ap = argparse.ArgumentParser(description="Generate a 1080x1080 social promo PNG.")
    ap.add_argument("--json", default="crosswalk-img-pivot-map.json",
                    help="Schema JSON to pull the title from.")
    ap.add_argument("--hook-lead", default=DEFAULT_HOOK_LEAD)
    ap.add_argument("--hook-emphasis", default=DEFAULT_HOOK_EMPHASIS)
    ap.add_argument("--badge", default="For unmatched IMGs")
    ap.add_argument("--out", help="Output filename stem.")
    args = ap.parse_args()

    json_path = Path(args.json)
    if not json_path.is_absolute():
        json_path = HERE / json_path
    data = json.loads(json_path.read_text(encoding="utf-8"))

    stem = args.out or json_path.stem + "-social"
    html_str = build_html(data.get("title", ""), args.hook_lead, args.hook_emphasis, args.badge)
    png = render(html_str, stem)
    print(f"✓ Social visual: {png}  ({png.stat().st_size // 1024} KB, 1080x1080)")


if __name__ == "__main__":
    main()
