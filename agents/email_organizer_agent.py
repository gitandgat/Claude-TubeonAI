"""
Email Organizer Agent — daily runner CLI

Accounts are defined in email_accounts.json (repo root):
  [
    {"provider": "gmail",   "name": "personal", "token_file": "gmail_token.json"},
    {"provider": "outlook", "name": "hotmail",  "token_file": "outlook_token.json",
     "email": "toto_makus@hotmail.com"}
  ]
Falls back to the default single Gmail + Outlook pair if the file is missing.

Usage:
  python -m agents.email_organizer_agent          # run all configured accounts
  python -m agents.email_organizer_agent --gmail-only
  python -m agents.email_organizer_agent --outlook-only
  python -m agents.email_organizer_agent --dry-run  # classify only, no writes
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

ACCOUNTS_FILE = Path("email_accounts.json")
DEFAULT_ACCOUNTS = [
    {"provider": "gmail", "name": "gmail", "token_file": "gmail_token.json"},
    {"provider": "outlook", "name": "outlook", "token_file": "outlook_token.json"},
]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Email Organizer Agent")
    parser.add_argument(
        "--gmail-only", action="store_true", help="Process Gmail accounts only"
    )
    parser.add_argument(
        "--outlook-only", action="store_true", help="Process Outlook accounts only"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Classify only, do not apply labels/moves",
    )
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Generate report only, do not send email",
    )
    return parser


def load_accounts(args: argparse.Namespace) -> List[Dict]:
    """Read account list from email_accounts.json, filtered by CLI flags."""
    if ACCOUNTS_FILE.exists():
        try:
            accounts = json.loads(ACCOUNTS_FILE.read_text())
        except Exception as e:
            logger.error(f"Failed to parse {ACCOUNTS_FILE}: {str(e)}")
            accounts = DEFAULT_ACCOUNTS
    else:
        accounts = DEFAULT_ACCOUNTS

    if args.gmail_only:
        accounts = [a for a in accounts if a["provider"] == "gmail"]
    if args.outlook_only:
        accounts = [a for a in accounts if a["provider"] == "outlook"]
    return accounts


def build_client(account: Dict):
    """Instantiate the provider client for one account entry."""
    if account["provider"] == "gmail":
        from gmail_client import GmailClient

        return GmailClient(
            credentials_file=account.get(
                "credentials_file", "gmail_credentials.json"
            ),
            token_file=account.get("token_file", "gmail_token.json"),
        )

    if account["provider"] == "outlook":
        from outlook_client import OutlookClient

        return OutlookClient(
            token_file=account.get("token_file", "outlook_token.json"),
            email=account.get("email"),
        )

    if account["provider"] == "imap":
        from imap_client import ImapClient

        return ImapClient(
            host=account["host"],
            email=account["email"],
            password_env=account.get("password_env", "IMAP_PASSWORD"),
            port=account.get("port", 993),
        )

    raise ValueError(f"Unknown provider: {account['provider']}")


def run(args: argparse.Namespace) -> int:
    """
    For each configured account: build client, run EmailOrganizer,
    merge per-account reports into one combined report + digest email.
    Returns exit code (0 = success, 1 = error)
    """
    try:
        from email_organizer import EmailOrganizer, OrganizerReport
        from report_mailer import ReportMailer

        logger.info("Starting Email Organizer Agent...")
        accounts = load_accounts(args)
        if not accounts:
            logger.error("No accounts configured for the selected flags")
            return 1

        if args.dry_run:
            logger.info("DRY RUN: Classifying emails only, no API writes")

        combined = OrganizerReport()
        ran_any = False

        for account in accounts:
            label = f"{account['provider']}:{account.get('name', '?')}"
            try:
                client = build_client(account)
            except Exception as e:
                msg = f"Failed to initialize {label}: {str(e)}"
                logger.warning(msg)
                combined.errors.append(msg)
                continue

            # imap-provider clients share the OutlookClient interface
            organizer = EmailOrganizer(
                gmail_client=client if account["provider"] == "gmail" else None,
                outlook_client=client
                if account["provider"] in ("outlook", "imap")
                else None,
                dry_run=args.dry_run,
            )

            logger.info(f"--- Processing {label} ---")
            report = organizer.run()
            ran_any = True

            # Tag each email with its account name for the merged report
            for email in report.emails:
                email["account"] = account.get("name", account["provider"])

            combined.total_processed += report.total_processed
            combined.archived += report.archived
            combined.emails.extend(report.emails)
            combined.errors.extend(report.errors)
            for category, count in report.labeled.items():
                combined.labeled[category] = (
                    combined.labeled.get(category, 0) + count
                )

        if not ran_any:
            logger.error("No account could be processed")
            return 1

        # Save the merged report once
        saver = EmailOrganizer(dry_run=True)
        saved_path = saver._save_report(combined)
        logger.info(f"Report saved to {saved_path}")

        if not args.no_email:
            logger.info("Sending digest email...")
            mailer = ReportMailer()
            success = mailer.send_email_organizer_digest(combined.__dict__)
            if not success:
                logger.warning("Failed to send email, but report was saved")

        logger.info("Email Organizer Agent completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Email Organizer Agent failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()
    sys.exit(run(args))
