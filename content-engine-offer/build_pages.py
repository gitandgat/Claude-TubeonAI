"""
Render the hand-polished gap teasers (out/*-gap-teaser.md) into clean, host-agnostic
HTML pages (out/html/*.html). Neutral, professional B2B styling — the page is about the
coach, not any one brand — so it reads well wherever it's hosted.

Usage:  python build_pages.py
"""
from __future__ import annotations

import glob
import re
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "html"

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{title}</title>
<style>
  :root {{ --ink:#1a1a1a; --muted:#6b6b6b; --accent:#0b7; --line:#e6e6e6; --bg:#fafafa; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }}
  main {{ max-width:720px; margin:0 auto; padding:56px 22px 96px; }}
  h1 {{ font-size:1.9rem; line-height:1.2; margin:0 0 .2em; letter-spacing:-.02em; }}
  h2 {{ font-size:1.3rem; margin:2em 0 .5em; }}
  h3 {{ font-size:1.05rem; color:var(--muted); font-weight:600; margin:.2em 0 1.4em; }}
  blockquote {{ margin:1.4em 0; padding:.8em 1.1em; border-left:3px solid var(--accent);
    background:#fff; color:var(--muted); border-radius:0 8px 8px 0; }}
  ol, ul {{ padding-left:1.3em; }}
  li {{ margin:.5em 0; }}
  strong {{ color:var(--ink); }}
  hr {{ border:0; border-top:1px solid var(--line); margin:2.4em 0; }}
  a {{ color:var(--accent); }}
  details {{ background:#fff; border:1px solid var(--line); border-radius:8px; padding:.6em 1em; }}
  summary {{ cursor:pointer; color:var(--muted); }}
  em {{ color:var(--muted); }}
</style>
</head>
<body><main>
{body}
</main></body>
</html>
"""


def render(md_path: Path) -> Path:
    text = md_path.read_text()
    m = re.search(r"^#\s+(.+)$", text, re.M)
    title = m.group(1).strip() if m else md_path.stem
    html = markdown.markdown(text, extensions=["extra", "sane_lists"])
    out = OUT / (md_path.stem.replace("-gap-teaser", "") + ".html")
    out.write_text(TEMPLATE.format(title=title, body=html))
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pages = [render(Path(p)) for p in sorted(glob.glob(str(HERE / "out" / "*-gap-teaser.md")))]
    print(f"✓ built {len(pages)} pages in {OUT}")
    for p in pages:
        print(f"  out/html/{p.name}   →  suggested URL: /r/{p.stem}")


if __name__ == "__main__":
    main()
