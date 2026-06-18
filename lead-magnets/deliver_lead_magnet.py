#!/usr/bin/env python3
"""
Deliver a lead magnet: tag the lead in Encharge + email the PDF.

This is the local replacement for the Make scenario's final two steps
(share + email). It reuses the repo's EnchargeClient and the SMTP config
from ReportMailer (keychain-backed — no .env reads here).

Flow for one lead:
  1. Upsert the person into Encharge with the lead-magnet tag (fires the flow).
  2. Email them the PDF as an attachment, branded with logo + CAN-SPAM footer.

Safety:
  --check    Read-only Encharge ping (GET /fields) + SMTP login test. No writes,
             no email sent. Use this to confirm both integrations work.
  --dry-run  Print exactly what would happen. No Encharge write, no email.
  (no flag)  Live: tags the lead AND sends the email. Requires --email.

Usage:
  python deliver_lead_magnet.py --check
  python deliver_lead_magnet.py --email "lead@x.com" --name "Dr. Asha" --dry-run
  python deliver_lead_magnet.py --email "lead@x.com" --name "Dr. Asha"
"""

import argparse
import os
import smtplib
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # import repo modules

from encharge_client import EnchargeClient  # noqa: E402
from report_mailer import ReportMailer  # noqa: E402

# --- Config -------------------------------------------------------------------
LEAD_TAG = "lead-magnet-pivot-map"
DEFAULT_PDF = "crosswalk-img-pivot-map.pdf"
GUIDE_TITLE = "The Unmatched Doctor's Pivot Map"
CTA_URL = os.getenv("CROSSWALK_CTA_URL", "https://www.crosswalkwisdom.com/img/calculator")
CTA_LABEL = "Run the Reality Calculator"  # MCCQE Reality Calculator
UNSUB_MAILTO = os.getenv("CROSSWALK_UNSUB_EMAIL", "totomakus@gmail.com")
# CAN-SPAM physical postal address (env override available).
MAILING_ADDRESS = os.getenv("CROSSWALK_MAILING_ADDRESS", "2 Kingsdale Ave, North York, ON M2N 3W1")
SOCIALS = {
    "Website": "https://crosswalkwisdom.com",
    "LinkedIn": "https://www.linkedin.com/in/sahawat-crosswalkwisdom/",
    "Instagram": "https://www.instagram.com/crosswalkwisdom",
}

AMBER = "#D4A843"
CHARCOAL = "#2C2C2C"
WARM = "#FAF7F2"


HONORIFICS = {"dr", "dr.", "mr", "mr.", "ms", "ms.", "mrs", "mrs.", "prof", "prof.", "miss"}


def first_name(name: str) -> str:
    """First given name, skipping a leading honorific (audience is mostly doctors)."""
    tokens = [t for t in (name or "").split() if t]
    for tok in tokens:
        if tok.lower() not in HONORIFICS:
            return tok
    return "there"


def email_html(name: str) -> str:
    """Branded delivery email: logo header, body, social buttons, CAN-SPAM footer."""
    fn = first_name(name)
    social_links = " &nbsp;|&nbsp; ".join(
        f'<a href="{url}" style="color:{AMBER};text-decoration:none;">{label}</a>'
        for label, url in SOCIALS.items()
    )
    # Crosswalk stripes rendered as a stack of amber bars (email-safe inline styles).
    stripes = "".join(
        f'<div style="width:34px;height:6px;border-radius:2px;background:{AMBER};'
        f'opacity:{0.6 if i % 2 else 1};margin-bottom:3px;"></div>'
        for i in range(4)
    )
    return f"""\
<div style="background:{WARM};padding:0;margin:0;font-family:Inter,Arial,sans-serif;color:{CHARCOAL};">
  <div style="max-width:600px;margin:0 auto;padding:32px 28px;">
    <table role="presentation" cellpadding="0" cellspacing="0"><tr>
      <td style="vertical-align:middle;padding-right:12px;">{stripes}</td>
      <td style="vertical-align:middle;font-family:Georgia,serif;font-size:22px;
        font-weight:700;color:{AMBER};">Crosswalk Wisdom</td>
    </tr></table>

    <h1 style="font-family:Georgia,serif;font-size:26px;line-height:1.2;margin:28px 0 14px;">
      {fn}, your Pivot Map is ready.</h1>

    <p style="font-size:16px;line-height:1.6;margin:0 0 16px;">
      Your guide, <strong>{GUIDE_TITLE}</strong>, is attached as a PDF.</p>

    <p style="font-size:16px;line-height:1.6;margin:0 0 16px;">
      One ask before you open it: read <strong>Section 2</strong> twice. The reframe in it
      is the whole game — everything else is just the map that follows from it.</p>

    <p style="font-size:16px;line-height:1.6;margin:0 0 16px;">
      And when you're ready to see the real odds behind the lottery you've been playing,
      run the numbers for yourself:</p>

    <p style="margin:22px 0;">
      <a href="{CTA_URL}" style="background:{AMBER};color:{CHARCOAL};
        text-decoration:none;font-weight:700;font-size:16px;padding:14px 26px;
        border-radius:6px;display:inline-block;">{CTA_LABEL} &rarr;</a></p>

    <p style="font-family:Georgia,serif;font-style:italic;color:{AMBER};font-size:16px;margin:24px 0 0;">
      From the Ward to the World,<br>Crosswalk Wisdom</p>

    <hr style="border:none;border-top:1px solid #e3ddd2;margin:28px 0 16px;">
    <p style="font-size:13px;color:#8a8278;margin:0 0 8px;">{social_links}</p>
    <p style="font-size:12px;color:#9a9388;line-height:1.5;margin:0;">
      You're receiving this because you requested a guide from Crosswalk Wisdom.<br>
      {MAILING_ADDRESS}<br>
      <a href="mailto:{UNSUB_MAILTO}?subject=unsubscribe" style="color:#9a9388;">Unsubscribe</a>
    </p>
  </div>
</div>"""


def email_text(name: str) -> str:
    fn = first_name(name)
    return (
        f"{fn}, your Pivot Map is ready.\n\n"
        f"Your guide, {GUIDE_TITLE}, is attached as a PDF.\n\n"
        f"One ask: read Section 2 twice. The reframe in it is the whole game.\n\n"
        f"When you're ready to see the real odds, run the numbers — {CTA_LABEL}: {CTA_URL}\n\n"
        f"From the Ward to the World,\nCrosswalk Wisdom\n\n"
        f"---\n{MAILING_ADDRESS}\nUnsubscribe: mailto:{UNSUB_MAILTO}?subject=unsubscribe\n"
    )


def send_with_attachment(mailer: ReportMailer, to: str, subject: str,
                         html_body: str, text_body: str, pdf_path: Path) -> bool:
    """Send a multipart email with the PDF attached, using ReportMailer's SMTP config."""
    if not mailer.smtp_password:
        print("✗ SMTP_PASSWORD not available (keychain/env) — cannot send.")
        return False

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = mailer.from_address
    msg["To"] = to
    msg["List-Unsubscribe"] = f"<mailto:{UNSUB_MAILTO}?subject=unsubscribe>"

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(text_body, "plain"))
    alt.attach(MIMEText(html_body, "html"))
    msg.attach(alt)

    part = MIMEApplication(pdf_path.read_bytes(), _subtype="pdf")
    part.add_header("Content-Disposition", "attachment", filename=pdf_path.name)
    msg.attach(part)

    try:
        with smtplib.SMTP(mailer.smtp_host, mailer.smtp_port) as server:
            server.starttls()
            server.login(mailer.smtp_user, mailer.smtp_password)
            server.send_message(msg)
        print(f"✓ Email sent to {to} with {pdf_path.name} attached.")
        return True
    except Exception as e:
        print(f"✗ Email failed: {e}")
        return False


def run_check() -> int:
    """Read-only connectivity check for both integrations. No writes, no email."""
    ok = True

    # Encharge: GET /fields (read-only)
    key = os.getenv("ENCHARGE_API_KEY")
    if not key:
        print("✗ Encharge: ENCHARGE_API_KEY not set.")
        ok = False
    else:
        try:
            fields = EnchargeClient(key).get_fields()
            n = len(fields) if isinstance(fields, list) else "?"
            print(f"✓ Encharge: connected (key valid, {n} person fields).")
        except Exception as e:
            print(f"✗ Encharge: {e}")
            ok = False

    # SMTP: connect + login, then quit (no message sent)
    mailer = ReportMailer()
    if not mailer.smtp_password:
        print("✗ SMTP: password not available from keychain/env.")
        ok = False
    else:
        try:
            with smtplib.SMTP(mailer.smtp_host, mailer.smtp_port) as server:
                server.starttls()
                server.login(mailer.smtp_user, mailer.smtp_password)
            print(f"✓ SMTP: login OK ({mailer.smtp_user} @ {mailer.smtp_host}:{mailer.smtp_port}).")
        except Exception as e:
            print(f"✗ SMTP: {e}")
            ok = False

    return 0 if ok else 1


def deliver(email: str, name: str, pdf_path: Path, dry_run: bool) -> int:
    subject = f"{first_name(name)}, your Pivot Map is ready"
    if dry_run:
        print("DRY RUN — no live calls made.\n")
        print(f"  Encharge: upsert {email!r} (name={name!r}) + tag {LEAD_TAG!r}")
        print(f"  Email:    to {email!r}")
        print(f"            subject: {subject!r}")
        print(f"            attach:  {pdf_path.name} ({pdf_path.stat().st_size // 1024} KB)")
        print(f"            CTA:     {CTA_LABEL} -> {CTA_URL}")
        return 0

    # 1) Encharge upsert + tag (fires the matching flow for the new tag)
    key = os.getenv("ENCHARGE_API_KEY")
    if not key:
        print("✗ ENCHARGE_API_KEY not set — aborting.")
        return 1
    try:
        EnchargeClient(key).add_subscriber(email=email, name=name, tags=[LEAD_TAG])
        print(f"✓ Encharge: tagged {email} with {LEAD_TAG}.")
    except Exception as e:
        print(f"✗ Encharge upsert failed: {e}")
        return 1

    # 2) Email the PDF
    sent = send_with_attachment(
        ReportMailer(), email, subject, email_html(name), email_text(name), pdf_path
    )
    return 0 if sent else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Tag a lead in Encharge and email the PDF.")
    ap.add_argument("--email", help="Recipient email (required for live/dry-run).")
    ap.add_argument("--name", default="", help="Recipient name.")
    ap.add_argument("--pdf", default=DEFAULT_PDF, help="PDF to attach.")
    ap.add_argument("--check", action="store_true", help="Read-only integration check.")
    ap.add_argument("--dry-run", action="store_true", help="Show plan; make no live calls.")
    args = ap.parse_args()

    if args.check:
        return run_check()

    if not args.email:
        ap.error("--email is required (or use --check).")

    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = HERE / pdf_path
    if not pdf_path.exists():
        print(f"✗ PDF not found: {pdf_path}. Run generate_lead_magnet.py first.")
        return 1

    return deliver(args.email, args.name, pdf_path, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
