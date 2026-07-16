#!/usr/bin/env python3
"""MoveAssess corrective-protocol PDFs.

Reads the JSON exported by physical-assessment-app/scripts/export-protocols.ts
and renders one branded PDF per featured case plus a combined library PDF.
Rendering is HTML -> shot-scraper pdf (Chromium print), since weasyprint's
pango is broken on this machine.

Usage:
    python3 generate_protocol_pdfs.py <protocols.json>

Output:
    ../physical-assessment-app/public/protocols/<case-id>.pdf
    ../physical-assessment-app/public/protocols/protocol-library.pdf
"""

import html
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent / "physical-assessment-app" / "public" / "protocols"
APP_URL = "https://physical-assessment-app.vercel.app"
PROGRAM_URL = "https://glute.crosswalkwisdom.com"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500&display=swap');

:root {
  --surface-0: #faf7f2; --surface-1: #f3eee5;
  --sage-500: #6f8768; --sage-600: #57694f; --sage-700: #435442;
  --ink: #232b24; --ink-soft: #4a544b;
  --hairline: rgba(35, 43, 36, 0.16);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
@page { size: A4; margin: 0; }
body {
  font-family: 'IBM Plex Sans', -apple-system, sans-serif;
  background: var(--surface-0); color: var(--ink);
  font-size: 10.5pt; line-height: 1.55;
}
.page { padding: 15mm 17mm 12mm; page-break-after: always; min-height: 297mm; position: relative; }
.page:last-child { page-break-after: auto; }
.brandbar {
  display: flex; justify-content: space-between; align-items: baseline;
  border-bottom: 1px solid var(--hairline); padding-bottom: 4mm; margin-bottom: 8mm;
}
.wordmark { font-family: 'Fraunces', Georgia, serif; font-weight: 600; letter-spacing: 0.02em; }
.label {
  font-size: 7.5pt; text-transform: uppercase; letter-spacing: 0.14em;
  color: var(--sage-600); font-weight: 500;
}
.numeral {
  font-family: 'Fraunces', Georgia, serif; font-size: 42pt; line-height: 1;
  color: var(--sage-500); font-weight: 500;
}
h1 { font-family: 'Fraunces', Georgia, serif; font-size: 20pt; font-weight: 600; margin: 2mm 0 3mm; }
.desc { color: var(--ink-soft); max-width: 62ch; margin-bottom: 7mm; }
h2.label { margin: 7mm 0 3mm; border-top: 1px solid var(--hairline); padding-top: 4mm; }
.logic p { max-width: 68ch; margin-bottom: 2.5mm; color: var(--ink-soft); }
.phase { margin-bottom: 5mm; }
.phase-head { display: flex; align-items: baseline; gap: 3mm; margin-bottom: 2mm; }
.phase-num {
  width: 6mm; height: 6mm; border: 1px solid var(--sage-500); border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 8.5pt; color: var(--sage-600); flex: none;
}
.phase-title { font-family: 'Fraunces', Georgia, serif; font-size: 13.5pt; font-weight: 600; }
.phase-intent { font-style: italic; color: var(--ink-soft); font-size: 9.5pt; margin-bottom: 3mm; padding-left: 9mm; }
table { width: 100%; border-collapse: collapse; margin-left: 9mm; width: calc(100% - 9mm); }
td { padding: 2mm 0; border-top: 1px solid var(--hairline); vertical-align: top; }
td.ex-name { font-weight: 500; width: 34%; padding-right: 4mm; }
td.ex-dosage { color: var(--sage-600); font-size: 9pt; width: 20%; padding-right: 4mm; white-space: nowrap; }
td.ex-cue { color: var(--ink-soft); font-size: 9.5pt; }
.retest {
  background: var(--surface-1); border: 1px solid var(--hairline);
  padding: 5mm 6mm; margin-top: 8mm; max-width: 68ch;
}
.retest .label { margin-bottom: 1.5mm; }
.retest p { font-size: 9.5pt; color: var(--ink-soft); }
.retest a { color: var(--sage-700); }
footer {
  position: absolute; bottom: 8mm; left: 17mm; right: 17mm;
  border-top: 1px solid var(--hairline); padding-top: 3mm;
  display: flex; justify-content: space-between;
  font-size: 8pt; color: var(--ink-soft);
}
footer a { color: var(--sage-700); text-decoration: none; }
.cover { display: flex; flex-direction: column; justify-content: center; }
.cover h1 { font-size: 30pt; max-width: 20ch; }
.cover .desc { font-size: 12pt; }
.toc { margin-top: 10mm; }
.toc li {
  list-style: none; border-top: 1px solid var(--hairline);
  padding: 2.5mm 0; display: flex; gap: 5mm; max-width: 68ch;
}
.toc .numeral { font-size: 14pt; width: 12mm; flex: none; }
"""


def esc(value: str) -> str:
    return html.escape(value, quote=False)


def case_page(case: dict) -> str:
    logic = "".join(f"<p>{esc(p)}</p>" for p in case["diagnosticLogic"])
    phases = []
    for i, phase in enumerate(case["protocol"], 1):
        rows = "".join(
            f"<tr><td class='ex-name'>{esc(ex['name'])}</td>"
            f"<td class='ex-dosage'>{esc(ex['dosage'])}</td>"
            f"<td class='ex-cue'>{esc(ex['cue'])}</td></tr>"
            for ex in phase["exercises"]
        )
        phases.append(
            f"""<div class="phase">
  <div class="phase-head"><span class="phase-num">{i}</span>
    <span class="phase-title">{esc(phase['title'])}</span></div>
  <p class="phase-intent">{esc(phase['intent'])}</p>
  <table>{rows}</table>
</div>"""
        )
    return f"""<div class="page">
  <div class="brandbar"><span class="wordmark">MOVEASSESS</span>
    <span class="label">Corrective Protocol · Case {esc(case['index'])}</span></div>
  <div class="numeral">{esc(case['index'])}</div>
  <h1>{esc(case['name'])}</h1>
  <p class="desc">{esc(case['shortDescription'])}</p>
  <h2 class="label">Diagnostic Logic</h2>
  <div class="logic">{logic}</div>
  <h2 class="label">The 3-Phase Protocol</h2>
  {''.join(phases)}
  <div class="retest">
    <p class="label">Retest in 14 Days</p>
    <p>Run the same assessment again and compare: <a href="{APP_URL}/?case={esc(case['id'])}">{APP_URL}/?case={esc(case['id'])}</a>.
    If the pattern is improving, keep going. If it isn't, the missing piece is usually
    programming and accountability — that's what the Glute Longevity program is for:
    <a href="{PROGRAM_URL}">{PROGRAM_URL}</a></p>
  </div>
  <footer><span>Crosswalk Wisdom — From the Ward to the World</span>
    <a href="{PROGRAM_URL}">{PROGRAM_URL.replace('https://', '')}</a></footer>
</div>"""


def cover_page(cases: list) -> str:
    toc = "".join(
        f"<li><span class='numeral'>{esc(c['index'])}</span>"
        f"<span><strong>{esc(c['name'])}</strong><br>"
        f"<span style='color:var(--ink-soft);font-size:9.5pt'>{esc(c['shortDescription'])}</span></span></li>"
        for c in cases
    )
    return f"""<div class="page cover">
  <div class="brandbar"><span class="wordmark">MOVEASSESS</span>
    <span class="label">Clinical Protocol Library</span></div>
  <p class="label">Eight Patterns · Eight Protocols</p>
  <h1>The Corrective Protocol Library</h1>
  <p class="desc">Every protocol in this library follows the same clinical arc —
  release what is overworking, activate what has gone quiet, then integrate the
  pattern under load. Find your pattern with the free assessment, run its
  protocol for 14 days, then retest.</p>
  <ul class="toc">{toc}</ul>
  <footer><span>Crosswalk Wisdom — From the Ward to the World</span>
    <a href="{PROGRAM_URL}">{PROGRAM_URL.replace('https://', '')}</a></footer>
</div>"""


def render_pdf(html_body: str, out_pdf: Path) -> None:
    doc = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as tmp:
        tmp.write(doc)
        tmp_path = tmp.name
    subprocess.run(
        ["shot-scraper", "pdf", tmp_path, "-o", str(out_pdf), "--wait", "1500"],
        check=True,
        capture_output=True,
    )
    Path(tmp_path).unlink()


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    cases = json.loads(Path(sys.argv[1]).read_text())
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for case in cases:
        out = OUT_DIR / f"{case['id']}.pdf"
        render_pdf(case_page(case), out)
        print(f"  {out.name} ({out.stat().st_size // 1024} KB)")

    library = cover_page(cases) + "".join(case_page(c) for c in cases)
    out = OUT_DIR / "protocol-library.pdf"
    render_pdf(library, out)
    print(f"  {out.name} ({out.stat().st_size // 1024} KB)")
    print(f"\n{len(cases) + 1} PDFs -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
