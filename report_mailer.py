"""
Report Mailer — sends digest emails via SMTP
"""
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from dotenv import load_dotenv

from keychain_secrets import get_secret

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_TO = os.getenv("NOTIFY_EMAIL", "totomakus@gmail.com")
DEFAULT_SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
DEFAULT_SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
DEFAULT_SMTP_USER = os.getenv("SMTP_USER", "totomakus@gmail.com")
DEFAULT_SMTP_PASSWORD = get_secret("SMTP_PASSWORD") or ""
DEFAULT_SMTP_FROM = os.getenv("SMTP_FROM", "totomakus@gmail.com")


class ReportMailer:
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_address: Optional[str] = None,
    ) -> None:
        """
        Initialize SMTP client. All params read from env vars if not provided.
        Falls back to Gmail SMTP (smtp.gmail.com:587) when SMTP_HOST not set.
        """
        self.smtp_host = smtp_host or DEFAULT_SMTP_HOST
        self.smtp_port = smtp_port or DEFAULT_SMTP_PORT
        self.smtp_user = smtp_user or DEFAULT_SMTP_USER
        self.smtp_password = smtp_password or DEFAULT_SMTP_PASSWORD
        self.from_address = from_address or DEFAULT_SMTP_FROM

    def send(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """
        Send email via SMTP with TLS.
        Returns True on success, False on failure (logs error, does not raise).
        """
        if not self.smtp_password:
            logger.error(
                "SMTP_PASSWORD not set in environment — cannot send email"
            )
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_address
            msg["To"] = to

            if text_body:
                msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent: {to} — {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {str(e)}")
            return False

    def send_email_organizer_digest(
        self, report: dict, to: str = DEFAULT_TO
    ) -> bool:
        """
        Build and send the Email Organizer daily digest.
        Subject: 'Email Organizer Report — {date} ({N} processed)'
        Returns: True on success
        """
        run_at = report.get("run_at", "unknown")
        total_processed = report.get("total_processed", 0)
        archived = report.get("archived", 0)
        labeled = report.get("labeled", {})
        errors = report.get("errors", [])

        date_str = run_at.split("T")[0] if "T" in run_at else run_at

        subject = f"Email Organizer Report — {date_str} ({total_processed} processed)"

        html_body = f"""
        <html>
        <head><style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        .stats {{ background: #ecf0f1; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        .category {{ margin-bottom: 10px; }}
        .error {{ color: #e74c3c; margin-top: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #34495e; color: white; }}
        </style></head>
        <body>
        <div class="container">
        <div class="header">
            <h2 style="margin: 0;">Email Organizer Report</h2>
            <p style="margin: 5px 0 0 0;">{date_str}</p>
        </div>

        <div class="stats">
            <p><strong>Total processed:</strong> {total_processed}</p>
            <p><strong>Archived:</strong> {archived}</p>
            <div><strong>Labeled:</strong>
            <ul>
        """

        for label, count in labeled.items():
            html_body += f"<li>{label}: {count}</li>"

        html_body += """
            </ul>
            </div>
        </div>
        """

        if errors:
            html_body += '<div class="error"><strong>Errors:</strong><ul>'
            for error in errors:
                html_body += f"<li>{error}</li>"
            html_body += "</ul></div>"

        html_body += """
        <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #888;">
            This is an automated report from the Email Organizer Agent.
        </p>
        </div>
        </body>
        </html>
        """

        return self.send(to, subject, html_body)

    def send_file_organizer_digest(self, report: dict, to: str = DEFAULT_TO) -> bool:
        """
        Build and send the File Organizer daily digest.
        Subject: 'File Organizer Report — {date} ({N} files, {N} duplicate groups)'
        Includes approval call-to-action.
        Returns: True on success
        """
        run_at = report.get("run_at", "unknown")
        total_files = report.get("total_files", 0)
        total_size_bytes = report.get("total_size_bytes", 0)
        by_category = report.get("by_category", {})
        duplicate_groups = report.get("duplicate_groups", [])
        total_duplicate_wasted_bytes = report.get(
            "total_duplicate_wasted_bytes", 0
        )

        date_str = run_at.split("T")[0] if "T" in run_at else run_at

        def format_bytes(n: int) -> str:
            for unit in ["B", "KB", "MB", "GB"]:
                if n < 1024:
                    return f"{n:.1f} {unit}"
                n /= 1024
            return f"{n:.1f} TB"

        subject = f"File Organizer Report — {date_str} ({total_files} files, {len(duplicate_groups)} duplicates)"

        html_body = f"""
        <html>
        <head><style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        .alert {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #856404; }}
        .stats {{ background: #ecf0f1; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #34495e; color: white; }}
        .duplicate-group {{ background: #f8f9fa; padding: 10px; margin-bottom: 10px; border-radius: 4px; border-left: 3px solid #e74c3c; }}
        .cta {{ background: #3498db; color: white; padding: 15px; border-radius: 4px; text-align: center; margin: 20px 0; }}
        </style></head>
        <body>
        <div class="container">
        <div class="header">
            <h2 style="margin: 0;">File Organizer Report</h2>
            <p style="margin: 5px 0 0 0;">{date_str}</p>
        </div>

        <div class="alert">
            <strong>⚠️ No files were moved.</strong>
            Review this report and reply to approve organization.
        </div>

        <div class="stats">
            <p><strong>Total files:</strong> {total_files}</p>
            <p><strong>Total size:</strong> {format_bytes(total_size_bytes)}</p>
            <p><strong>Duplicates found:</strong> {len(duplicate_groups)} groups ({format_bytes(total_duplicate_wasted_bytes)} wasted)</p>
        </div>

        <h3>Files by Category</h3>
        <table>
            <tr><th>Category</th><th>Count</th></tr>
        """

        for category, count in sorted(by_category.items(), key=lambda x: -x[1]):
            html_body += f"<tr><td>{category}</td><td>{count}</td></tr>"

        html_body += "</table>"

        if duplicate_groups:
            html_body += "<h3>Top Duplicate Groups (by wasted space)</h3>"
            top_dups = sorted(
                duplicate_groups,
                key=lambda x: x.get("wasted_bytes", 0),
                reverse=True,
            )[:5]
            for dup in top_dups:
                wasted = format_bytes(dup.get("wasted_bytes", 0))
                file_count = len(dup.get("files", []))
                html_body += f"""
                <div class="duplicate-group">
                    <strong>{file_count} copies</strong> ({wasted} wasted)
                    <ul style="margin: 5px 0; padding-left: 20px; font-size: 12px;">
                """
                for file_path in dup.get("files", [])[:3]:
                    html_body += f"<li>{file_path}</li>"
                if len(dup.get("files", [])) > 3:
                    html_body += f"<li>... and {len(dup['files']) - 3} more</li>"
                html_body += "</ul></div>"

        html_body += """
        <div class="cta">
            <p>Reply to this email with your approval to organize files.</p>
            <p style="font-size: 12px; margin: 10px 0 0 0;">Options: approve all, approve duplicates only, custom approval</p>
        </div>

        <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #888;">
            This is an automated report from the File Organizer Agent. No files were modified.
        </p>
        </div>
        </body>
        </html>
        """

        return self.send(to, subject, html_body)
