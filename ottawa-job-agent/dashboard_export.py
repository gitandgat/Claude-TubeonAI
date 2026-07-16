"""Regenerate the Job-agent dashboard's src/data/*.ts files from real data.

Reads:
  - applications.json          (via tracker._load())      -> src/data/applications.ts
  - microsites/_manifest.json  + microsites/<slug>.html    -> src/data/microsites.ts
  - automation_runs.jsonl      (via run_history.load_runs) -> src/data/automation.ts
  - application_autofill.json                              -> src/data/reference.ts

Never fabricates content: sections with no real backing data (resume summary,
STAR answers, cover letter openers, references) are emitted empty rather than
invented. Run manually:

    python3 dashboard_export.py
"""

import json
from datetime import date, datetime
from pathlib import Path

import tracker
from run_history import load_runs

BASE = Path(__file__).resolve().parent
JOB_AGENT_REPO = BASE.parent.parent / "Job-agent"
DATA_DIR = JOB_AGENT_REPO / "src" / "data"

MICROSITES_DIR = BASE / "microsites"
MANIFEST_FILE = MICROSITES_DIR / "_manifest.json"
AUTOFILL_FILE = BASE / "application_autofill.json"

LIVE_BASE = "https://microsites-gitandgats-projects.vercel.app"

MAX_RUNS = 50

STATUS_MAP = {
    "applied": "Applied",
    "interview_scheduled": "Interview",
    "offer": "Offer",
    "rejected_after_application": "RejectedApplication",
    "rejected_after_interview": "RejectedInterview",
    "ghosted": "Ghosted",
    "withdrawn": "Withdrawn",
}


def _write_ts(filename: str, header: str, exports: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / filename).write_text(header + exports + "\n", encoding="utf-8")


def _drop_none(d: dict) -> dict:
    """Optional TS fields (e.g. `micrositeId?: string`) accept undefined, not null —
    omit the key entirely rather than emit `null` so generated .ts files type-check."""
    return {k: v for k, v in d.items() if v is not None}


def export_applications() -> None:
    data = tracker._load()
    manifest = json.loads(MANIFEST_FILE.read_text()) if MANIFEST_FILE.exists() else {}

    apps = []
    for job_id, entry in data.items():
        history = entry.get("history", [])
        last_updated = history[-1]["date"] if history else entry.get("applied_date", "")

        microsite_id = None
        for slug, m in manifest.items():
            if m.get("company", "").lower() == entry.get("company", "").lower() and \
               m.get("title", "").lower() == entry.get("title", "").lower():
                microsite_id = slug
                break

        timeline = [
            _drop_none({
                "id": f"t{i + 1}",
                "date": h.get("date", ""),
                "event": tracker.STATUS_LABELS.get(h.get("status"), h.get("status", "")),
                "note": h.get("note") or None,
            })
            for i, h in enumerate(history)
        ]

        apps.append(_drop_none({
            "id": job_id,
            "company": entry.get("company", ""),
            "role": entry.get("title", ""),
            "location": entry.get("location") or "",
            "source": entry.get("source") or "",
            "status": STATUS_MAP.get(entry.get("status"), "Applied"),
            "appliedDate": entry.get("applied_date", ""),
            "lastUpdated": last_updated,
            "jobPostingUrl": entry.get("url"),
            "notes": entry.get("notes", ""),
            "micrositeId": microsite_id,
            "timeline": timeline,
        }))

    _write_ts(
        "applications.ts",
        "import { Application } from '../types';\n\n",
        f"export const applications: Application[] = {json.dumps(apps, indent=2)};",
    )


def export_microsites() -> None:
    manifest = json.loads(MANIFEST_FILE.read_text()) if MANIFEST_FILE.exists() else {}
    apps = tracker._load()

    sites = []
    for slug, m in manifest.items():
        html_path = MICROSITES_DIR / f"{slug}.html"
        is_live = html_path.exists()

        application_id = None
        for job_id, entry in apps.items():
            if entry.get("company", "").lower() == m.get("company", "").lower() and \
               entry.get("title", "").lower() == m.get("title", "").lower():
                application_id = job_id
                break

        if is_live:
            stat = html_path.stat()
            created = date.fromtimestamp(getattr(stat, "st_birthtime", stat.st_ctime)).isoformat()
            updated = date.fromtimestamp(stat.st_mtime).isoformat()
        else:
            created = updated = ""

        sites.append(_drop_none({
            "id": slug,
            "title": m.get("title", ""),
            "company": m.get("company", ""),
            "applicationId": application_id,
            "status": "Live" if is_live else "Draft",
            "url": f"{LIVE_BASE}/{slug}",
            "createdDate": created,
            "lastUpdated": updated,
        }))

    _write_ts(
        "microsites.ts",
        "import { Microsite } from '../types';\n\n",
        f"export const microsites: Microsite[] = {json.dumps(sites, indent=2)};",
    )


def export_automation() -> None:
    runs = load_runs()[-MAX_RUNS:]
    runs.reverse()  # most recent first

    out = [
        _drop_none({
            "id": f"run-{i + 1:03d}",
            "automationName": r.get("automation_name", ""),
            "targetJob": r.get("target", ""),
            "lastRun": r.get("timestamp", ""),
            "status": r.get("status", "Skipped"),
            "message": r.get("message", ""),
            "durationMs": r.get("duration_ms"),
        })
        for i, r in enumerate(runs)
    ]

    _write_ts(
        "automation.ts",
        "import { AutomationRun } from '../types';\n\n",
        f"export const automationRuns: AutomationRun[] = {json.dumps(out, indent=2)};",
    )


def _split_cert(raw: str) -> dict:
    """Certifications are flat strings like 'X – Y (Z)'. Split on the first
    en/em dash to recover a real issuer where the source text has one;
    never invent a year — none is tracked in the source data."""
    for dash in (" – ", " — "):
        if dash in raw:
            name, issuer = raw.split(dash, 1)
            return {"name": name.strip(), "issuer": issuer.strip(), "year": ""}
    return {"name": raw.strip(), "issuer": "", "year": ""}


def export_reference() -> None:
    autofill = json.loads(AUTOFILL_FILE.read_text()) if AUTOFILL_FILE.exists() else {}
    personal = autofill.get("personal", {})
    screening = autofill.get("screening", {})
    certifications = autofill.get("certifications", [])

    contact_info = {
        "fullName": personal.get("Full name", ""),
        "email": personal.get("Email", ""),
        "phone": personal.get("Phone", ""),
        "address": personal.get("Full address", ""),
        "linkedin": personal.get("LinkedIn", ""),
        "website": personal.get("Website", ""),
        "workStatus": personal.get("Work status", ""),
    }

    certs = [_split_cert(c) for c in certifications]

    snippets = [
        {
            "id": f"screening-{i + 1}",
            "category": "Screening Questions",
            "label": question,
            "content": answer,
        }
        for i, (question, answer) in enumerate(screening.items())
    ]

    lines = [
        "import { ReferenceSnippet, Certification } from '../types';\n\n",
        f"export const contactInfo = {json.dumps(contact_info, indent=2)};\n\n",
        f"export const certifications: Certification[] = {json.dumps(certs, indent=2)};\n\n",
        # No real resume summary exists yet — ship empty rather than fabricating one.
        "export const resumeSummary = '';\n\n",
        f"export const snippets: ReferenceSnippet[] = {json.dumps(snippets, indent=2)};",
    ]
    (DATA_DIR / "reference.ts").write_text("".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not JOB_AGENT_REPO.exists():
        raise SystemExit(f"Job-agent repo not found at {JOB_AGENT_REPO}")
    export_applications()
    export_microsites()
    export_automation()
    export_reference()
    print(f"Exported real data into {DATA_DIR}")


if __name__ == "__main__":
    main()
