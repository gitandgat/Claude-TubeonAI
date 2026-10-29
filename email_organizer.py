"""
Email Organizer — classification engine and orchestrator for Gmail + Outlook
"""
import os
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

IMPORTANT_KEYWORDS = [
    "invoice",
    "receipt",
    "contract",
    "urgent",
    "action required",
    "confirm",
    "verify",
    "confirmation",
    "payment",
    "overdue",
    "deadline",
    "renewal",
    "expir",
]

MARKETING_KEYWORDS = [
    "unsubscribe",
    "view in browser",
    "email preferences",
    "you're receiving this",
    "opt out",
    "manage subscription",
    "weekly digest",
    "newsletter",
    "% off",
    "limited time",
    "sale ends",
    "free trial",
    "deal of the day",
    "promo",
]

MARKETING_SENDER_PATTERNS = [
    "noreply",
    "no-reply",
    "newsletter",
    "notifications@",
    "updates@",
    "hello@",
    "team@mailchimp",
    "campaign-archive",
    "marketing@",
    "offers@",
    "deals@",
    "promo@",
    "news@",
    "digest@",
    "alerts@",
]

CATEGORY_KEYWORDS = {
    "Finance": [
        "invoice",
        "receipt",
        "payment",
        "bank",
        "tax",
        "billing",
        "statement",
        "transaction",
        "refund",
        "wire",
    ],
    "Work": [
        "meeting",
        "project",
        "deadline",
        "contract",
        "proposal",
        "client",
        "colleague",
        "onboarding",
        "schedule",
    ],
    "Personal": ["family", "friend", "personal", "vacation", "holiday"],
}

FOLDERS = ["Work", "Finance", "Invoices", "Personal", "Receipts", "Marketing"]


@dataclass
class ClassifiedEmail:
    msg_id: str
    provider: str
    subject: str
    sender: str
    category: str
    action: str
    is_important: bool
    reason: str


@dataclass
class OrganizerReport:
    run_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    total_processed: int = 0
    archived: int = 0
    labeled: Dict[str, int] = field(default_factory=dict)
    emails: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class EmailOrganizer:
    def __init__(
        self,
        gmail_client=None,
        outlook_client=None,
        report_dir: Path = Path("reports"),
        dry_run: bool = False,
    ) -> None:
        self.gmail_client = gmail_client
        self.outlook_client = outlook_client
        self.report_dir = Path(report_dir)
        self.dry_run = dry_run
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def _is_marketing(
        self, subject: str, sender: str, snippet: str
    ) -> bool:
        """Check marketing keywords in subject/snippet and sender patterns."""
        text_to_check = (
            f"{subject} {sender} {snippet}".lower()
        )

        for keyword in MARKETING_KEYWORDS:
            if keyword in text_to_check:
                return True

        for pattern in MARKETING_SENDER_PATTERNS:
            if pattern in sender.lower():
                return True

        return False

    def _detect_category(self, subject: str, snippet: str) -> str:
        """
        Keyword-match subject+snippet against CATEGORY_KEYWORDS.
        Returns best-match category name or "Personal" as fallback.
        """
        text_to_check = f"{subject} {snippet}".lower()

        best_match = "Personal"
        best_count = 0

        for category, keywords in CATEGORY_KEYWORDS.items():
            match_count = sum(
                1 for kw in keywords if kw in text_to_check
            )
            if match_count > best_count:
                best_count = match_count
                best_match = category

        return best_match

    def classify_email(
        self, subject: str, sender: str, snippet: str
    ) -> Dict:
        """
        Pure classification logic — no I/O.
        Priority order:
          1. marketing detection → category=Marketing, action=archive
          2. important keyword match → determine sub-category
          3. sender domain heuristics
          4. fallback → category=Personal, action=label_and_move
        Returns: dict with category, action, is_important, reason
        """
        subject_lower = subject.lower()
        snippet_lower = snippet.lower()

        # Check if marketing
        if self._is_marketing(subject, sender, snippet):
            return {
                "category": "Marketing",
                "action": "archive",
                "is_important": False,
                "reason": "Marketing email detected",
            }

        # Check if important
        is_important = any(
            kw in subject_lower or kw in snippet_lower
            for kw in IMPORTANT_KEYWORDS
        )

        # Special case: invoice keyword → Invoices folder
        if "invoice" in subject_lower:
            category = "Invoices"
        # Special case: receipt keyword → Receipts folder
        elif "receipt" in subject_lower:
            category = "Receipts"
        else:
            category = self._detect_category(subject, snippet)

        return {
            "category": category,
            "action": "label_and_move",
            "is_important": is_important,
            "reason": f"Classified as {category} (important: {is_important})",
        }

    def run_gmail(self) -> List[Dict]:
        """Fetch unread Gmail messages, classify, apply labels/archive. Returns classifications."""
        if not self.gmail_client:
            logger.info("Gmail client not configured, skipping Gmail")
            return []

        try:
            logger.info("Running Gmail organizer...")
            messages = self.gmail_client.list_unread(max_results=100)
            logger.info(f"Processing {len(messages)} Gmail messages...")

            classifications = []
            for msg in messages:
                try:
                    classification = self.classify_email(
                        msg["subject"],
                        msg["sender"],
                        msg["snippet"],
                    )

                    classified_email = ClassifiedEmail(
                        msg_id=msg["id"],
                        provider="gmail",
                        subject=msg["subject"],
                        sender=msg["sender"],
                        category=classification["category"],
                        action=classification["action"],
                        is_important=classification["is_important"],
                        reason=classification["reason"],
                    )

                    # Apply the action (skipped in dry-run)
                    if self.dry_run:
                        pass
                    elif classification["action"] == "archive":
                        self.gmail_client.archive(
                            msg["id"],
                            also_label="Marketing",
                        )
                    else:
                        self.gmail_client.move_to_folder(
                            msg["id"],
                            classification["category"],
                        )

                    classifications.append(asdict(classified_email))
                    logger.debug(
                        f"  {msg['subject'][:50]} → {classification['category']}"
                    )

                except Exception as e:
                    logger.warning(
                        f"Failed to process Gmail message {msg['id']}: {str(e)}"
                    )

            logger.info(f"Processed {len(classifications)} Gmail messages")
            return classifications

        except Exception as e:
            logger.error(f"Gmail organizer failed: {str(e)}")
            return []

    def run_outlook(self) -> List[Dict]:
        """Fetch unread Outlook messages, classify, apply categories/move/archive. Returns classifications."""
        if not self.outlook_client:
            logger.info("Outlook client not configured, skipping Outlook")
            return []

        try:
            logger.info("Running Outlook organizer...")
            messages = self.outlook_client.list_unread(max_results=100)
            logger.info(f"Processing {len(messages)} Outlook messages...")

            classifications = []
            for msg in messages:
                try:
                    classification = self.classify_email(
                        msg["subject"],
                        msg["sender_email"],
                        msg["body_preview"],
                    )

                    classified_email = ClassifiedEmail(
                        msg_id=msg["id"],
                        provider="outlook",
                        subject=msg["subject"],
                        sender=msg["sender_email"],
                        category=classification["category"],
                        action=classification["action"],
                        is_important=classification["is_important"],
                        reason=classification["reason"],
                    )

                    # Apply the action (skipped in dry-run)
                    if self.dry_run:
                        pass
                    elif classification["action"] == "archive":
                        self.outlook_client.archive(
                            msg["id"],
                            also_category="Marketing",
                        )
                    else:
                        self.outlook_client.move_to_folder(
                            msg["id"],
                            classification["category"],
                        )

                    classifications.append(asdict(classified_email))
                    logger.debug(
                        f"  {msg['subject'][:50]} → {classification['category']}"
                    )

                except Exception as e:
                    logger.warning(
                        f"Failed to process Outlook message {msg['id']}: {str(e)}"
                    )

            logger.info(f"Processed {len(classifications)} Outlook messages")
            return classifications

        except Exception as e:
            logger.error(f"Outlook organizer failed: {str(e)}")
            return []

    def run(self) -> OrganizerReport:
        """
        Entry point: run Gmail + Outlook, build OrganizerReport, save JSON.
        Returns: OrganizerReport
        """
        logger.info("Starting Email Organizer...")

        report = OrganizerReport()

        gmail_results = self.run_gmail()
        outlook_results = self.run_outlook()

        all_results = gmail_results + outlook_results
        report.total_processed = len(all_results)
        report.emails = all_results

        # Count by category and action
        by_category = {}
        archived_count = 0

        for classified in all_results:
            category = classified.get("category", "Unknown")
            action = classified.get("action", "")

            by_category[category] = by_category.get(category, 0) + 1

            if action == "archive":
                archived_count += 1

        report.labeled = by_category
        report.archived = archived_count

        logger.info(
            f"Email Organizer complete: {report.total_processed} processed, {report.archived} archived"
        )

        return report

    def _save_report(self, report: OrganizerReport) -> Path:
        """
        Write report as JSON to reports/email_organizer_YYYY-MM-DD.json.
        Returns: path to written file
        """
        now = datetime.now(timezone.utc).isoformat().split("T")[0]
        filename = f"email_organizer_{now}.json"
        output_path = self.report_dir / filename

        try:
            with open(output_path, "w") as f:
                json.dump(asdict(report), f, indent=2)
            logger.info(f"Report saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
            raise
