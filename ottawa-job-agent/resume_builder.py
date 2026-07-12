"""Generate a PDF resume tailored to a job category (and optionally one specific
job posting, via content_generator.tailor_resume) using fpdf2."""

from pathlib import Path

from fpdf import FPDF

from resume_data import INVOLVEMENT_CATEGORIES, PROFILE, SUMMARIES

OUTPUT_DIR = Path(__file__).resolve().parent / "resumes"
OUTPUT_DIR.mkdir(exist_ok=True)

# Brand colours (RGB)
CHARCOAL = (26, 26, 46)
TEAL = (22, 160, 133)
GRAY = (100, 100, 100)
LIGHT = (240, 240, 240)
WHITE = (255, 255, 255)

# Map common unicode chars to latin-1-safe equivalents (core fonts are latin-1)
_UNICODE_MAP = {
    "–": "-",   # en dash
    "—": "-",   # em dash
    "‘": "'",   # left single quote
    "’": "'",   # right single quote
    "“": '"',   # left double quote
    "”": '"',   # right double quote
    "…": "...",  # ellipsis
    "·": "-",   # middot
    "•": "-",   # bullet
}


def _safe(text: str) -> str:
    for uni, repl in _UNICODE_MAP.items():
        text = text.replace(uni, repl)
    return text.encode("latin-1", "replace").decode("latin-1")


class ResumePDF(FPDF):
    def header(self):
        pass  # custom header drawn per page

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 10, _safe(f"{PROFILE['name']} - {PROFILE['email']} - {PROFILE['phone']}"), align="C")

    def section_title(self, title: str):
        self.ln(4)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*TEAL)
        self.cell(0, 6, _safe(title.upper()), ln=True)
        self.set_draw_color(*TEAL)
        self.set_line_width(0.4)
        self.line(self.get_x(), self.get_y(), self.get_x() + 175, self.get_y())
        self.ln(2)
        self.set_text_color(*CHARCOAL)

    def job_entry(self, title: str, company: str, location: str, dates: str):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*CHARCOAL)
        self.cell(0, 5, _safe(title), ln=True)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 4, _safe(f"{company}  -  {location}  -  {dates}"), ln=True)
        self.set_text_color(*CHARCOAL)
        self.ln(1)

    def bullet(self, text: str):
        self.set_font("Helvetica", "", 8.5)
        self.cell(5, 5, chr(149))  # latin-1 bullet
        self.multi_cell(0, 5, _safe(text))
        self.ln(0.5)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 8.5)
        self.multi_cell(0, 5, _safe(text))


def build_pdf(category: str, *, summary: str = None, skills: list = None, job_id: str = None) -> str:
    """Build a PDF resume for the given category. Returns the file path.

    Pass `summary`/`skills` (from content_generator.tailor_resume) to emphasize the
    content for one specific job posting; omit them for the plain per-category resume.
    `job_id` keeps per-job PDFs from overwriting the shared per-category file.
    """
    filename = f"resume_{category}_{job_id}.pdf" if job_id else f"resume_{category}.pdf"
    path = str(OUTPUT_DIR / filename)

    pdf = ResumePDF()
    pdf.set_margins(18, 16, 18)
    pdf.add_page()

    # ── Name & Contact ────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*CHARCOAL)
    pdf.cell(0, 10, _safe(PROFILE["name"]), ln=True)

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*GRAY)
    contact = f"{PROFILE['phone']}  -  {PROFILE['email']}  -  {PROFILE['linkedin']}  -  {PROFILE['address_display']}"
    pdf.cell(0, 5, _safe(contact), ln=True)
    pdf.ln(1)

    # Teal rule
    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(1.0)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(3)

    # ── Profile Summary ───────────────────────────────────────────────────
    pdf.section_title("Profile")
    pdf.body_text(summary or SUMMARIES.get(category, SUMMARIES["outreach_sales"]))

    # ── Experience ────────────────────────────────────────────────────────
    pdf.section_title("Experience")
    for exp in PROFILE["experience"]:
        pdf.job_entry(exp["title"], exp["company"], exp["location"], exp["dates"])
        for b in exp["bullets"]:
            pdf.bullet(b)
        pdf.ln(2)

    # ── Education ─────────────────────────────────────────────────────────
    pdf.section_title("Education")
    for edu in PROFILE["education"]:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*CHARCOAL)
        pdf.cell(0, 5, _safe(edu["degree"]), ln=True)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*GRAY)
        pdf.cell(0, 4, _safe(f"{edu['school']}  -  {edu['dates']}"), ln=True)
        pdf.ln(2)

    # ── Skills ────────────────────────────────────────────────────────────
    pdf.section_title("Skills & Qualifications")
    pdf.set_text_color(*CHARCOAL)
    resolved_skills = skills or PROFILE["skills"].get(category, PROFILE["skills"]["outreach_sales"])
    for skill in resolved_skills:
        pdf.bullet(skill)
    pdf.ln(2)

    # ── Certifications ────────────────────────────────────────────────────
    pdf.section_title("Certifications")
    for cert in PROFILE["certifications"]:
        pdf.bullet(cert)
    pdf.ln(2)

    # ── Community Involvement (only for relevant role types) ──────────────
    if category in INVOLVEMENT_CATEGORIES and PROFILE.get("involvement"):
        pdf.section_title("Community Involvement & Leadership")
        for item in PROFILE["involvement"]:
            pdf.bullet(item)
        pdf.ln(2)

    # ── Languages ─────────────────────────────────────────────────────────
    pdf.section_title("Languages")
    pdf.body_text(", ".join(PROFILE["languages"]))

    pdf.output(path)
    return path
