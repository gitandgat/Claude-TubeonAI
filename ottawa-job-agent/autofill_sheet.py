"""Generate a one-click 'application autofill' cheat sheet.

Produces two artifacts you reuse on EVERY job form so you never retype
certifications, education, or screening answers:
  - application_autofill.html : copy-each-field page with one-click buttons
  - application_autofill.json : machine-readable (for browser extensions / future automation)
"""

import html
import json
from pathlib import Path

from resume_data import PROFILE

BASE = Path(__file__).resolve().parent

# Common screening questions every job form asks — answered once, reused forever.
SCREENING = {
    "Legally authorized to work in Canada?": "Yes — Canadian Permanent Resident",
    "Do you require sponsorship?": "No",
    "Available start date": "October 13, 2026",
    "Located in Ottawa?": "Yes — based in Ottawa (214 Metcalfe St)",
    "Valid driver's licence?": "Yes — valid Ontario driver's licence",
    "Languages": ", ".join(PROFILE["languages"]),
    "Highest education": "Doctor of Medicine (MD), Thammasat University",
    "Years of experience (healthcare/coaching)": "6+ years",
    "How did you hear about us?": "Online job posting",
}

REFERENCES_NOTE = "Available on request"


def _autofill_data() -> dict:
    return {
        "personal": {
            "Full name": PROFILE["name"],
            "First name": "Sahawat",
            "Last name": "Nilwatcharamanee",
            "Email": PROFILE["email"],
            "Phone": PROFILE["phone"],
            "Street address": PROFILE["address_components"]["street"],
            "Full address": PROFILE["address"],
            "City": PROFILE["address_components"]["city"],
            "Province": PROFILE["address_components"]["province"],
            "Postal code": PROFILE["address_components"]["postal_code"],
            "Country": PROFILE["address_components"]["country"],
            "LinkedIn": f"https://{PROFILE['linkedin']}",
            "Website": f"https://{PROFILE['website']}",
            "Work status": PROFILE["status"],
        },
        "screening": SCREENING,
        "certifications": PROFILE["certifications"],
        "education": [
            {
                "Degree": e["degree"],
                "School": e["school"],
                "Dates": e["dates"],
            }
            for e in PROFILE["education"]
        ],
        "experience": [
            {
                "Title": x["title"],
                "Company": x["company"],
                "Location": x["location"],
                "Dates": x["dates"],
                "Responsibilities": " ".join(x["bullets"]),
            }
            for x in PROFILE["experience"]
        ],
        "references": REFERENCES_NOTE,
    }


def _field_row(label: str, value: str) -> str:
    safe_val = html.escape(value)
    js_val = json.dumps(value)  # safely quoted for the onclick attr
    return f"""    <div class="row">
      <div class="label">{html.escape(label)}</div>
      <div class="value">{safe_val}</div>
      <button class="copy" onclick='copyText({js_val}, this)'>Copy</button>
    </div>"""


def build_autofill_sheet() -> dict:
    data = _autofill_data()

    sections = []

    # Personal
    rows = "\n".join(_field_row(k, v) for k, v in data["personal"].items())
    sections.append(("Personal & contact", rows))

    # Screening
    rows = "\n".join(_field_row(k, v) for k, v in data["screening"].items())
    sections.append(("Screening questions", rows))

    # Certifications (each one copyable + a 'copy all' line)
    cert_rows = "\n".join(_field_row(f"Certification {i+1}", c) for i, c in enumerate(data["certifications"]))
    all_certs = "; ".join(data["certifications"])
    cert_rows = _field_row("ALL certifications (one line)", all_certs) + "\n" + cert_rows
    sections.append(("Certifications", cert_rows))

    # Education
    edu_rows = []
    for e in data["education"]:
        edu_rows.append(_field_row("Degree", e["Degree"]))
        edu_rows.append(_field_row("School", e["School"]))
        edu_rows.append(_field_row("Dates", e["Dates"]))
    sections.append(("Education", "\n".join(edu_rows)))

    # Experience
    exp_rows = []
    for x in data["experience"]:
        exp_rows.append(_field_row("Job title", x["Title"]))
        exp_rows.append(_field_row("Employer", x["Company"]))
        exp_rows.append(_field_row("Dates", x["Dates"]))
        exp_rows.append(_field_row("Responsibilities", x["Responsibilities"]))
    sections.append(("Work experience", "\n".join(exp_rows)))

    sections.append(("References", _field_row("References", data["references"])))

    sections_html = "\n".join(
        f"""  <section>
    <h2>{html.escape(title)}</h2>
{rows}
  </section>"""
        for title, rows in sections
    )

    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="robots" content="noindex" />
<title>Application autofill — Sahawat</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
<style>
  :root {{ --amber:#D4A843; --charcoal:#2C2C2C; --warm-white:#FAF7F2; --teal:#5B9A8B; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:"Inter",sans-serif; background:var(--warm-white); color:var(--charcoal); padding:clamp(1.5rem,5vw,4rem); }}
  h1 {{ font-family:"Playfair Display",serif; font-size:clamp(1.8rem,1rem+3vw,3rem); }}
  .sub {{ color:#666; margin:0.5rem 0 2.5rem; max-width:60ch; }}
  section {{ background:#fff; border-radius:14px; padding:1.5rem 1.75rem; margin-bottom:1.5rem;
    box-shadow:0 4px 20px rgba(44,44,44,0.06); border:1px solid rgba(44,44,44,0.08); }}
  h2 {{ font-size:0.8rem; letter-spacing:0.18em; text-transform:uppercase; color:var(--teal);
    margin-bottom:1.25rem; }}
  .row {{ display:grid; grid-template-columns:200px 1fr auto; gap:1rem; align-items:center;
    padding:0.65rem 0; border-top:1px solid rgba(44,44,44,0.07); }}
  .row:first-of-type {{ border-top:none; }}
  .label {{ font-weight:600; font-size:0.85rem; color:#555; }}
  .value {{ font-size:0.92rem; word-break:break-word; }}
  .copy {{ background:var(--charcoal); color:var(--warm-white); border:none; border-radius:999px;
    padding:0.45rem 1.1rem; font-size:0.8rem; font-weight:600; cursor:pointer; transition:background 0.2s; }}
  .copy:hover {{ background:var(--amber); color:var(--charcoal); }}
  .copy.done {{ background:var(--teal); }}
  @media (max-width:640px) {{ .row {{ grid-template-columns:1fr auto; }} .label {{ grid-column:1/-1; }} }}
</style></head>
<body>
  <h1>Application autofill</h1>
  <p class="sub">Keep this open in a tab while filling any job form. Click <b>Copy</b> on any field, then paste. No more retyping certifications, dates, or screening answers.</p>
{sections_html}
<script>
  function copyText(text, btn) {{
    navigator.clipboard.writeText(text).then(() => {{
      const old = btn.textContent; btn.textContent = "Copied!"; btn.classList.add("done");
      setTimeout(() => {{ btn.textContent = old; btn.classList.remove("done"); }}, 1200);
    }});
  }}
</script>
</body></html>"""

    html_path = BASE / "application_autofill.html"
    json_path = BASE / "application_autofill.json"
    html_path.write_text(page, encoding="utf-8")
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {"html": str(html_path), "json": str(json_path)}


if __name__ == "__main__":
    out = build_autofill_sheet()
    print("Autofill sheet:", out["html"])
    print("JSON:", out["json"])
