"""Email sender: application emails from Outlook + digest to Gmail."""

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


import re
from datetime import date, datetime

NOTIFY_TO = "totomakus@gmail.com"
NOTIFY_FROM = "totomakus@gmail.com"
APPLY_FROM = "Sahawat.nil@outlook.com"


def _fmt_deadline(job: dict) -> str:
    """Format the deadline informatively. Never shows expired (already filtered)."""
    deadline = job.get("deadline")
    if not deadline:
        return "not stated on the posting"
    m = re.search(r"\d{4}-\d{2}-\d{2}", str(deadline))
    if not m:
        return str(deadline)
    try:
        dl = datetime.strptime(m.group(), "%Y-%m-%d").date()
        days = (dl - date.today()).days
        return f"{m.group()}  (closes in {days} day{'s' if days != 1 else ''})"
    except ValueError:
        return str(deadline)


def _gmail_smtp():
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(NOTIFY_FROM, os.environ["GMAIL_APP_PASSWORD"])
    return s


def _outlook_smtp():
    s = smtplib.SMTP("smtp-mail.outlook.com", 587)
    s.starttls()
    s.login(APPLY_FROM, os.environ["OUTLOOK_APP_PASSWORD"])
    return s


def _attach_file(msg: MIMEMultipart, pdf_path: str):
    if not pdf_path or not Path(pdf_path).exists():
        return
    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    filename = Path(pdf_path).name
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)


def send_application(job: dict, cover_letter: str, resume_pdf: str, subject: str):
    """Send the application email from Sahawat's Outlook account."""
    apply_email = job.get("apply_email")
    if not apply_email:
        return False

    msg = MIMEMultipart()
    msg["From"] = f"Sahawat Nilwatcharamanee <{APPLY_FROM}>"
    msg["To"] = apply_email
    msg["Subject"] = subject

    body = f"""{cover_letter}

---
Sahawat Nilwatcharamanee
Phone: 416-616-9589
Email: {APPLY_FROM}
LinkedIn: linkedin.com/in/sahawatcrosswalkwisdom
"""
    msg.attach(MIMEText(body, "plain"))
    _attach_file(msg, resume_pdf)

    try:
        with _outlook_smtp() as s:
            s.sendmail(APPLY_FROM, apply_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[email_sender] Failed to send application to {apply_email}: {e}")
        return False


def _digest_body(
    applied: list, notify: list, total_found: int,
    skipped: int = 0, newly_ghosted: list = None, alerts: list = None,
) -> tuple:
    """Build the (subject, body) of the daily summary. Pure function, no I/O.

    The agent is fully autonomous: everything here is a report of what already
    happened, never a to-do list. Jobs it couldn't apply to are listed FYI-only
    with the reason and the link, in case the reader ever wants to follow up."""
    newly_ghosted = newly_ghosted or []
    alerts = alerts or []

    if not applied and not notify:
        subject = "Job Agent — quiet day, nothing new"
    else:
        subject = f"Job Agent — {len(applied)} applied for you, {len(notify)} couldn't be auto-applied"
    if alerts:
        subject = "⚠ " + subject

    lines = [
        "=== OTTAWA JOB AGENT — DAILY SUMMARY ===",
        "",
        f"Scanned: {total_found} | Applied: {len(applied)} | "
        f"Couldn't auto-apply: {len(notify)} | Skipped (low fit): {skipped}",
        "",
        "Everything below is FYI only — applications go out automatically, "
        "nothing here needs action.",
        "",
    ]

    if alerts:
        lines.append("─── ⚠ ALERTS " + "─" * 40)
        for a in alerts:
            lines.append(f"  ! {a}")
        lines.append("")

    if not applied and not notify:
        lines += ["No new relevant jobs today.", ""]

    if applied:
        lines.append(f"─── APPLIED ({len(applied)}) " + "─" * 30)
        for j in sorted(applied, key=lambda x: x.get("score", 0), reverse=True):
            applied_via = (
                f"email → {j['apply_email']}" if j.get("apply_email")
                else f"company website ({j.get('web_apply_ats', 'unknown')} form)"
            )
            if j.get("rare_category"):
                lines.append("\n★ RARE POSTING — applied automatically:")
            lines += [
                f"\n✓ {j['title']} — {j['company']}  (fit {j.get('score', '?')}/10)",
                f"    via:      {applied_via}",
                f"    location: {j['location']}",
                f"    deadline: {_fmt_deadline(j)}",
                f"    posting:  {j['url']}",
            ]
            if j.get("microsite_url"):
                lines.append(f"    pitch page sent along: {j['microsite_url']}")
        lines.append("")

    if notify:
        lines.append(f"─── COULDN'T AUTO-APPLY ({len(notify)}) — FYI " + "─" * 15)
        for j in sorted(notify, key=lambda x: x.get("score", 0), reverse=True):
            if j.get("rare_category"):
                lines.append("\n★ RARE POSTING:")
            lines += [
                f"\n✗ {j['title']} — {j['company']}  (fit {j.get('score', '?')}/10)",
                f"    why:      {j.get('no_apply_reason', 'unknown')}",
                f"    deadline: {_fmt_deadline(j)}",
                f"    posting:  {j['url']}",
            ]
        lines.append("")

    if newly_ghosted:
        lines.append(f"─── AUTO-MARKED GHOSTED ({len(newly_ghosted)}) — no response in 21+ days " + "─" * 5)
        for g in newly_ghosted:
            lines.append(f"  - {g['title']} @ {g['company']}")
        lines.append("")

    lines.append("Full tracker attached. The dashboard picks up today's data automatically.")

    return subject, "\n".join(lines)


def send_digest(
    applied: list, notify: list, total_found: int,
    tracker_html: str = None, newly_ghosted: list = None, skipped: int = 0,
    alerts: list = None,
):
    """Send the daily summary to Sahawat's Gmail. Always sends — even on quiet days —
    so there's a reliable daily confirmation the agent ran."""
    subject, body = _digest_body(applied, notify, total_found, skipped, newly_ghosted, alerts)

    msg = MIMEMultipart()
    msg["From"] = NOTIFY_FROM
    msg["To"] = NOTIFY_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if tracker_html and Path(tracker_html).exists():
        _attach_file(msg, tracker_html)

    try:
        with _gmail_smtp() as s:
            s.sendmail(NOTIFY_FROM, NOTIFY_TO, msg.as_string())
        print(f"[email_sender] Digest sent to {NOTIFY_TO}")
    except Exception as e:
        print(f"[email_sender] Failed to send digest: {e}")
