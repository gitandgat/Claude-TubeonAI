"""
Generate TikTok carousel slides for the rebel campaign (9:16, 1080x1920).
Each reel becomes 6 PNG slides, output to rebel-campaign/carousels/<reel_key>/.

Usage:
  python3 rebel-campaign/generate_carousel.py          # all reels
  python3 rebel-campaign/generate_carousel.py reel1    # single reel
"""
import os
import sys
import subprocess

OUT_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carousels")
os.makedirs(OUT_BASE, exist_ok=True)

# Brand colours (Crosswalk Wisdom)
BG = "#0d0d0d"
AMBER = "#e8a838"
TEAL = "#3db8b0"
WHITE = "#f5f0e8"
MUTED = "#8a8a8a"

# Two aspect ratios:
#   9:16 (1080x1920) for TikTok photo carousels
#   4:5  (1080x1350) for Instagram carousels (max portrait allowed)
FORMATS = {
    "tiktok": (1080, 1920),
    "instagram": (1080, 1350),
}
SLIDE_W, SLIDE_H = 1080, 1920  # default; overridden per format in generate_reel()

REELS = {
    "reel1": {
        "slides": [
            # 1 — hook
            {"type": "hook", "line1": "WHOSE", "line2": "DREAM", "line3": "WAS IT,\nREALLY?"},
            # 2 — setup
            {"type": "body", "text": "Nobody tells you this part:\n\nThe career that made your family proud was never actually about you."},
            # 3 — the cut
            {"type": "body_accent", "label": "IT BOUGHT THEM:", "items": ["Status", "Access", "Never paying for a consultation again"]},
            # 4 — the mechanism
            {"type": "list", "label": "The system ran exactly as designed:", "items": ["You got in.", "You got through.", "You got licensed."]},
            # 5 — the close
            {"type": "statement", "text": "Mission accomplished —\nfor them.", "sub": "So here's the question that was never yours to answer:"},
            # 6 — CTA
            {"type": "cta", "question": "Now that you're safe —\nwhat do YOU want?"},
        ]
    },
    "reel2": {
        "slides": [
            {"type": "hook", "line1": "YOU'RE 35.", "line2": "YOU'RE\nLICENSED.", "line3": "YOU'RE\nNOT FREE."},
            {"type": "body", "text": "Walk the timeline:\n\nHigh school sciences → MCAT → Med school → Residency → Licensed."},
            {"type": "statement", "text": "Notice what's missing\nfrom every single step?", "sub": "You."},
            {"type": "split", "left_label": "YOUR FRAMEWORK", "left": ["Happiness", "Flourishing", "Your choices"], "right_label": "THEIR FRAMEWORK", "right": ["Stability", "Status", "Survival"]},
            {"type": "statement", "text": "Stability ≠ flourishing.", "sub": "Nobody told you there was a difference. You kept running the checklist. The feeling never caught up."},
            {"type": "cta", "question": "What would change if you knew\nthose were different objectives?"},
        ]
    },
    "reel3": {
        "slides": [
            {"type": "hook", "line1": "1985.", "line2": "THE YEAR YOUR", "line3": "CODE WAS\nWRITTEN."},
            {"type": "body", "text": "Your parents needed safety, status, belonging.\n\nMedicine was the only program that delivered all three at once.\n\nSo they installed it. In you."},
            {"type": "body_accent", "label": "THE PROGRAM DELIVERED:", "items": ["Safety", "Status", "Belonging"]},
            {"type": "statement", "text": "The code worked.\nYou became a doctor.", "sub": "There's just one problem."},
            {"type": "body", "text": "It was written for their threat environment.\n\nNot yours."},
            {"type": "cta", "question": "Wrong era.\nRight person."},
        ]
    },
    "reel4": {
        "slides": [
            {"type": "hook", "line1": "THE SACRIFICE", "line2": "WAS NEVER\nMEANT TO BE", "line3": "YOUR CAGE."},
            {"type": "body", "text": "They came with nothing.\n\nA suitcase. A passport. They built something so you'd have choices they never had."},
            {"type": "split", "left_label": "WHAT IT WAS", "left": ["Freedom", "Options", "Permission to choose"], "right_label": "WHAT IT BECAME", "right": ["Obligation", "Guilt", "Can't leave"]},
            {"type": "body", "text": "That inversion isn't your fault.\n\nAnd it isn't theirs either.\n\nNobody planned for the gift to calcify into a debt."},
            {"type": "statement", "text": "Leaving isn't betraying\nthe sacrifice.", "sub": "Leaving IS the mission completing."},
            {"type": "cta", "question": "Options, not obligations.\nThat was always the point."},
        ]
    },
    "reel5": {
        "slides": [
            {"type": "hook", "line1": "WRONG", "line2": "QUESTION.", "line3": "RIGHT\nQUESTION."},
            {"type": "split", "left_label": "WRONG QUESTION", "left": ["Can I leave?", "Am I allowed?", "What will they think?"], "right_label": "RIGHT QUESTION", "right": ["What am I built for?", "Where do my skills go?", "What do I choose?"]},
            {"type": "body", "text": "Your training gave you:\n\nPrecision. Capacity for complexity. The ability to hold high stakes without falling apart."},
            {"type": "statement", "text": "The system said those skills\nare only for clinical work.", "sub": "The system was wrong."},
            {"type": "body", "text": "What you can do with what you have —\n\nthat's a much more interesting question than whether you're allowed to stop."},
            {"type": "cta", "question": "Ready to ask\nthe right question?"},
        ]
    },
}

CTA_URL = "crosswalkwisdom.com/img/calculator"


def css_vars() -> str:
    return f"""
    :root {{
        --bg: {BG};
        --amber: {AMBER};
        --teal: {TEAL};
        --white: {WHITE};
        --muted: {MUTED};
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        background: var(--bg);
        color: var(--white);
        font-family: 'Georgia', serif;
        width: {SLIDE_W}px;
        height: {SLIDE_H}px;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .slide {{
        width: {SLIDE_W}px;
        height: {SLIDE_H}px;
        padding: 100px 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
    }}
    """


def brand_bar(accent: str = AMBER) -> str:
    return f"""<div style="position:absolute;top:0;left:0;width:100%;height:12px;background:{accent}"></div>
<div style="position:absolute;bottom:80px;left:90px;right:90px;display:flex;align-items:center;gap:16px;">
  <div style="width:8px;height:8px;border-radius:50%;background:{AMBER}"></div>
  <span style="font-family:system-ui,sans-serif;font-size:26px;letter-spacing:0.12em;color:{MUTED};text-transform:uppercase;">Crosswalk Wisdom</span>
</div>"""


def render_hook(slide: dict) -> str:
    l1 = slide["line1"].replace("\n", "<br>")
    l2 = slide["line2"].replace("\n", "<br>")
    l3 = slide["line3"].replace("\n", "<br>")
    return f"""<!doctype html><html><head><style>{css_vars()}</style></head><body>
<div class="slide">
  {brand_bar(AMBER)}
  <div style="margin-top:-80px;">
    <div style="font-family:system-ui,sans-serif;font-size:32px;letter-spacing:0.18em;color:{AMBER};text-transform:uppercase;margin-bottom:40px;">THE FIRST GENERATION TO CHOOSE</div>
    <div style="font-size:140px;font-weight:900;font-family:Georgia,serif;line-height:0.95;color:{WHITE};letter-spacing:-2px;">{l1}</div>
    <div style="font-size:130px;font-weight:900;font-family:Georgia,serif;line-height:0.95;color:{AMBER};letter-spacing:-2px;margin-top:8px;">{l2}</div>
    <div style="font-size:100px;font-weight:900;font-family:Georgia,serif;line-height:0.95;color:{WHITE};letter-spacing:-2px;margin-top:8px;">{l3}</div>
  </div>
</div></body></html>"""


def render_body(slide: dict) -> str:
    text = slide["text"].replace("\n", "<br>")
    return f"""<!doctype html><html><head><style>{css_vars()}</style></head><body>
<div class="slide">
  {brand_bar(TEAL)}
  <div style="margin-top:-40px;">
    <div style="font-size:64px;font-family:Georgia,serif;line-height:1.35;color:{WHITE};">{text}</div>
  </div>
</div></body></html>"""


def render_body_accent(slide: dict) -> str:
    label = slide["label"]
    items_html = "".join(
        f'<div style="font-size:72px;font-weight:700;color:{AMBER};font-family:Georgia,serif;line-height:1.2;margin-bottom:16px;">{it}</div>'
        for it in slide["items"]
    )
    return f"""<!doctype html><html><head><style>{css_vars()}</style></head><body>
<div class="slide">
  {brand_bar(AMBER)}
  <div style="margin-top:-40px;">
    <div style="font-family:system-ui,sans-serif;font-size:30px;letter-spacing:0.14em;color:{TEAL};text-transform:uppercase;margin-bottom:56px;">{label}</div>
    {items_html}
  </div>
</div></body></html>"""


def render_list(slide: dict) -> str:
    label = slide["label"]
    items_html = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:28px;margin-bottom:40px;">'
        f'<span style="font-size:54px;color:{AMBER};font-weight:700;flex-shrink:0;">→</span>'
        f'<span style="font-size:60px;font-family:Georgia,serif;line-height:1.25;color:{WHITE};">{it}</span>'
        f'</div>'
        for it in slide["items"]
    )
    return f"""<!doctype html><html><head><style>{css_vars()}</style></head><body>
<div class="slide">
  {brand_bar(AMBER)}
  <div style="margin-top:-40px;">
    <div style="font-family:system-ui,sans-serif;font-size:30px;letter-spacing:0.14em;color:{MUTED};text-transform:uppercase;margin-bottom:64px;">{label}</div>
    {items_html}
  </div>
</div></body></html>"""


def render_split(slide: dict) -> str:
    def col(label: str, items: list, accent: str) -> str:
        items_html = "".join(
            f'<div style="font-size:48px;font-family:Georgia,serif;color:{WHITE};line-height:1.3;margin-bottom:16px;">• {it}</div>'
            for it in items
        )
        return f"""<div style="flex:1;padding:40px 44px;background:rgba(255,255,255,0.04);border-top:6px solid {accent};">
  <div style="font-family:system-ui,sans-serif;font-size:26px;letter-spacing:0.14em;color:{accent};text-transform:uppercase;margin-bottom:40px;">{label}</div>
  {items_html}
</div>"""
    left = col(slide["left_label"], slide["left"], MUTED)
    right = col(slide["right_label"], slide["right"], AMBER)
    return f"""<!doctype html><html><head><style>{css_vars()}</style></head><body>
<div class="slide">
  {brand_bar(AMBER)}
  <div style="display:flex;gap:20px;width:100%;margin-top:-40px;">{left}{right}</div>
</div></body></html>"""


def render_statement(slide: dict) -> str:
    text = slide["text"].replace("\n", "<br>")
    sub = slide.get("sub", "").replace("\n", "<br>")
    sub_html = f'<div style="font-size:52px;font-family:Georgia,serif;color:{AMBER};line-height:1.35;margin-top:48px;">{sub}</div>' if sub else ""
    return f"""<!doctype html><html><head><style>{css_vars()}</style></head><body>
<div class="slide">
  {brand_bar(TEAL)}
  <div style="margin-top:-60px;">
    <div style="font-size:80px;font-weight:700;font-family:Georgia,serif;line-height:1.15;color:{WHITE};">{text}</div>
    {sub_html}
  </div>
</div></body></html>"""


def render_cta(slide: dict) -> str:
    q = slide["question"].replace("\n", "<br>")
    return f"""<!doctype html><html><head><style>{css_vars()}</style></head><body>
<div class="slide" style="background:linear-gradient(160deg,#1a1200 0%,{BG} 60%);">
  {brand_bar(AMBER)}
  <div style="margin-top:-80px;">
    <div style="font-family:system-ui,sans-serif;font-size:28px;letter-spacing:0.16em;color:{TEAL};text-transform:uppercase;margin-bottom:48px;">READY TO FIND OUT?</div>
    <div style="font-size:76px;font-weight:700;font-family:Georgia,serif;line-height:1.2;color:{WHITE};margin-bottom:64px;">{q}</div>
    <div style="display:inline-block;padding:28px 56px;border:3px solid {AMBER};border-radius:4px;">
      <div style="font-family:system-ui,sans-serif;font-size:32px;letter-spacing:0.08em;color:{AMBER};">→ {CTA_URL}</div>
    </div>
  </div>
</div></body></html>"""


RENDERERS = {
    "hook": render_hook,
    "body": render_body,
    "body_accent": render_body_accent,
    "list": render_list,
    "split": render_split,
    "statement": render_statement,
    "cta": render_cta,
}


def generate_reel(reel_key: str, fmt: str = "tiktok") -> list[str]:
    global SLIDE_W, SLIDE_H
    SLIDE_W, SLIDE_H = FORMATS[fmt]
    reel = REELS[reel_key]
    out_dir = os.path.join(OUT_BASE, reel_key, fmt)
    os.makedirs(out_dir, exist_ok=True)

    paths = []
    for i, slide in enumerate(reel["slides"], 1):
        kind = slide["type"]
        html = RENDERERS[kind](slide)
        html_path = os.path.join(out_dir, f"slide_{i:02d}.html")
        png_path = os.path.join(out_dir, f"slide_{i:02d}.png")

        with open(html_path, "w") as f:
            f.write(html)

        result = subprocess.run(
            ["shot-scraper", html_path, "-o", png_path,
             "--width", str(SLIDE_W), "--height", str(SLIDE_H)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  [WARN] shot-scraper error on slide {i}: {result.stderr[:200]}")
        else:
            print(f"  [OK] {png_path}")
        paths.append(png_path)

    return paths


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "all"
    fmt = sys.argv[2] if len(sys.argv) > 2 else "all"
    keys = list(REELS.keys()) if key == "all" else [key]
    fmts = list(FORMATS.keys()) if fmt == "all" else [fmt]
    for k in keys:
        for f in fmts:
            print(f"\n--- Generating {k} [{f}] ---")
            generate_reel(k, f)
    print("\nDone.")
