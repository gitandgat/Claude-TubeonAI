"""Generate a PDF cover letter using fpdf2, matching resume_builder's brand style.

content_generator.write_cover_letter() produces per-job letter TEXT for email
bodies and web form fields — there's no per-posting upload step to put a file
into on Job Bank's Direct Apply. This module instead builds a single, honest,
job-agnostic letter as an actual PDF file, for one-time upload to Job Bank's
account-level cover letter storage (see jobbank_apply.py's docstring for why
Direct Apply can't be tailored per posting).
"""

from pathlib import Path

from fpdf import FPDF

from resume_builder import CHARCOAL, GRAY, TEAL, _safe
from resume_data import PROFILE

OUTPUT_DIR = Path(__file__).resolve().parent / "cover_letters"
OUTPUT_DIR.mkdir(exist_ok=True)

UNIVERSAL_COVER_LETTER = """Dear Hiring Team,

My name is Sahawat Nilwatcharamanee. I trained and worked as a physician in Thailand, then moved to Canada and spent the next stage of my career as a crossing guard — a job that taught me how much steady, reliable, everyday care matters, and it's part of why I'm now pursuing work that lets me combine that care with practical, hands-on responsibility.

Since then I've earned my NASM Certified Personal Trainer certification, completed postgraduate diplomas in Health Informatics and Health Care Administration & Management, and taken part in several community and environmental leadership programs, including the Canada Service Corps and LEAF's Young Urban Forest Leaders program. I'm bilingual in English and Thai, comfortable in administrative and public-facing settings, and reliable in physically demanding, in-person work.

I'm a Canadian Permanent Resident based in Ottawa, available to start October 13, 2026. I don't have prior experience in every field I apply to, and I won't pretend otherwise — but I learn quickly, show up consistently, and bring a genuine, calm, people-first approach to any role.

I'd welcome the opportunity to discuss how my background could be useful to your team. Thank you for your time and consideration.

Sincerely,
Sahawat Nilwatcharamanee"""


class CoverLetterPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 10, _safe(f"{PROFILE['name']} - {PROFILE['email']} - {PROFILE['phone']}"), align="C")


def build_pdf(text: str, *, filename: str = "cover_letter_universal.pdf") -> str:
    """Build a PDF cover letter from plain text (blank-line-separated paragraphs).
    Returns the file path."""
    path = str(OUTPUT_DIR / filename)

    pdf = CoverLetterPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*CHARCOAL)
    pdf.cell(0, 9, _safe(PROFILE["name"]), ln=True)

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*GRAY)
    contact = f"{PROFILE['phone']}  -  {PROFILE['email']}  -  {PROFILE['address_display']}"
    pdf.cell(0, 5, _safe(contact), ln=True)
    pdf.ln(1)

    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(1.0)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(*CHARCOAL)
    for para in text.strip().split("\n\n"):
        pdf.multi_cell(0, 6, _safe(para.strip()))
        pdf.ln(4)

    pdf.output(path)
    return path


if __name__ == "__main__":
    out = build_pdf(UNIVERSAL_COVER_LETTER)
    print(f"Wrote {out}")
