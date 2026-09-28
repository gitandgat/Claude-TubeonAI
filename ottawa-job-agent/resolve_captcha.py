"""On-demand, human-in-the-loop captcha resolver.

The daily pipeline runs headless, so any form it fills in never survives long
enough for a human to open the link and see it pre-filled (the browser closes
before that). This script re-does the fill in a *visible* browser instead: it
opens the real posting, fills the form fresh, and — if a captcha blocks the
submit it already attempted — pauses so you can solve the captcha and click
Submit yourself in that same window. Nothing is transmitted to the employer
until you do.

Usage:
    python3 resolve_captcha.py <job_id>

<job_id> is the id shown in the captcha_gate digest entry (also the key in
applications.json).
"""
import json
import sys
from pathlib import Path

from content_generator import write_cover_letter
from resume_builder import build_pdf
from tracker import record_application
from web_applier import apply_on_website

BASE = Path(__file__).parent
APPLICATIONS_FILE = BASE / "applications.json"


def _load_job(job_id: str) -> dict:
    data = json.loads(APPLICATIONS_FILE.read_text())
    record = data.get(job_id)
    if not record:
        raise SystemExit(f"No application record found for job id '{job_id}' in {APPLICATIONS_FILE.name}")
    return {**record, "id": job_id}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    job = _load_job(sys.argv[1])

    print(f"=== {job['title']} @ {job['company']} ===")
    print(f"URL: {job['url']}")

    resume_pdf = str(BASE / "resumes" / f"resume_{job['category']}_{job['id']}.pdf")
    if not Path(resume_pdf).exists():
        print("Tailored resume not found on disk — rebuilding plain category resume...")
        resume_pdf = build_pdf(job["category"])

    print("Generating cover letter...")
    cover_letter = write_cover_letter(job)

    print("Opening visible browser — filling the form now...")
    result = apply_on_website(job, cover_letter, resume_pdf, headless=False)

    print(f"\nResult: {result['status']} ({result['ats']})")
    if result.get("screenshot"):
        print(f"Screenshot: {result['screenshot']}")

    if result["status"] == "submitted":
        record_application(job, f"web:{result['ats']} (human-resolved captcha)")
        print("Recorded as applied in applications.json.")
    else:
        print("Not recorded as applied — rerun this script to try again.")


if __name__ == "__main__":
    main()
