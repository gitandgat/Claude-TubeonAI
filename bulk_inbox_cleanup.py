"""
One-off bulk inbox cleanup — Jun 2026 (v2: incremental + reconnect-safe)

Outlook (~51K messages): classify the last 12 months into folders
(marketing → Archive), then bulk-archive everything older.
Gmail (~458 messages): classify everything via batched label operations.

v2 changes after v1 hung on a dropped connection:
- socket timeouts in the IMAP clients
- classify+move per batch (progress survives interruption; re-running
  is safe — moved messages are no longer in INBOX)
- every IMAP call wrapped in reconnect-and-retry

Usage: python3 bulk_inbox_cleanup.py
"""
import json
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from email import message_from_bytes
from email.utils import parseaddr
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

RECENT_MONTHS = 12
FETCH_CHUNK = 200
MOVE_CHUNK = 250  # smaller batches + pacing to stay under Microsoft throttling
BATCH_PAUSE = 1.0
REPORT_PATH = Path("reports/bulk_cleanup_2026-06-12.json")


def compress_uid_set(uids: List[int]) -> str:
    """Compress sorted UIDs into IMAP set syntax (1:5,8,10:12)."""
    if not uids:
        return ""
    uids = sorted(uids)
    parts = []
    start = prev = uids[0]
    for uid in uids[1:]:
        if uid == prev + 1:
            prev = uid
            continue
        parts.append(str(start) if start == prev else f"{start}:{prev}")
        start = prev = uid
    parts.append(str(start) if start == prev else f"{start}:{prev}")
    return ",".join(parts)


def chunked(items: List, size: int) -> List[List]:
    return [items[i : i + size] for i in range(0, len(items), size)]


class ImapSession:
    """Wraps an OutlookClient connection with reconnect-and-retry.

    Microsoft throttles sustained bulk IMAP activity, so retries back off
    (10s → 30s → 60s → 120s) to let the throttle window pass.
    """

    RETRY_WAITS = [10, 30, 60, 120]

    def __init__(self, client) -> None:
        self.client = client

    def _reconnect(self):
        self.client._imap = None
        imap = self.client._get_imap()
        imap.select("INBOX")
        return imap

    def uid(self, *args):
        """Run an IMAP UID command; reconnect with backoff on failure."""
        try:
            imap = self.client._get_imap()
            return imap.uid(*args)
        except Exception as e:
            last_error = e

        for wait in self.RETRY_WAITS:
            logger.warning(
                f"IMAP {args[0]} failed ({str(last_error)}) — retrying in {wait}s"
            )
            time.sleep(wait)
            try:
                imap = self._reconnect()
                return imap.uid(*args)
            except Exception as e:
                last_error = e

        raise last_error


def classify_batch(session, organizer, uids: List[int]) -> Dict[str, List[int]]:
    """
    Fetch headers for a UID batch and group UIDs by destination folder.

    Outlook returns the UID *after* the header literal, as a separate
    bytes element following each tuple — e.g.
      (b'36418 (BODY[HEADER.FIELDS ...] {140}', b'<headers>'), b' UID 273358)'
    Other servers put it in the tuple descriptor. Handle both.
    """
    from outlook_client import OutlookClient

    by_folder: Dict[str, List[int]] = {}
    typ, msg_data = session.uid(
        "FETCH",
        compress_uid_set(uids),
        "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM)])",
    )

    def classify(uid: int, header_bytes: bytes) -> None:
        msg = message_from_bytes(header_bytes)
        subject = OutlookClient._decode_mime_header(msg.get("Subject", ""))
        sender = parseaddr(msg.get("From", ""))[1]
        c = organizer.classify_email(subject, sender, "")
        dest = "Archive" if c["action"] == "archive" else c["category"]
        by_folder.setdefault(dest, []).append(uid)

    pending_headers = None
    for part in msg_data:
        if isinstance(part, tuple) and len(part) == 2:
            descriptor = part[0].decode("utf-8", errors="replace")
            uid_match = re.search(r"UID (\d+)", descriptor)
            if uid_match:
                classify(int(uid_match.group(1)), part[1])
                pending_headers = None
            else:
                pending_headers = part[1]
        elif isinstance(part, bytes) and pending_headers is not None:
            uid_match = re.search(rb"UID (\d+)", part)
            if uid_match:
                classify(int(uid_match.group(1)), pending_headers)
            pending_headers = None

    return by_folder


def outlook_cleanup(organizer) -> Dict:
    from outlook_client import OutlookClient

    client = OutlookClient()
    imap = client._get_imap()
    imap.select("INBOX")
    session = ImapSession(client)

    cutoff = datetime.now(timezone.utc) - timedelta(days=RECENT_MONTHS * 30)
    cutoff_str = cutoff.strftime("%d-%b-%Y")

    typ, data = session.uid("SEARCH", None, f"SINCE {cutoff_str}")
    recent_uids = [int(u) for u in (data[0] or b"").split()]
    typ, data = session.uid("SEARCH", None, f"BEFORE {cutoff_str}")
    old_uids = [int(u) for u in (data[0] or b"").split()]
    logger.info(
        f"Outlook: {len(recent_uids)} recent (since {cutoff_str}), "
        f"{len(old_uids)} older"
    )

    known_folders = set()
    folder_counts: Dict[str, int] = {}
    moved_recent = 0

    # --- Phase A: classify + move per batch (incremental) ---
    for batch_num, batch in enumerate(chunked(recent_uids, FETCH_CHUNK), 1):
        by_folder = classify_batch(session, organizer, batch)

        parsed = sum(len(v) for v in by_folder.values())
        if parsed == 0 and batch:
            logger.warning(
                f"Batch {batch_num}: 0/{len(batch)} messages parsed — aborting "
                "to avoid a silent no-op run"
            )
            break

        for folder, uids in by_folder.items():
            if folder != "Archive" and folder not in known_folders:
                client._ensure_folder(folder)
                known_folders.add(folder)

            typ, _ = session.uid("MOVE", compress_uid_set(uids), f'"{folder}"')
            if typ == "OK":
                moved_recent += len(uids)
                folder_counts[folder] = folder_counts.get(folder, 0) + len(uids)
            else:
                logger.warning(f"MOVE of {len(uids)} → {folder} returned {typ}")

        done = min(batch_num * FETCH_CHUNK, len(recent_uids))
        if batch_num % 10 == 0 or done >= len(recent_uids):
            logger.info(f"  recent: {done}/{len(recent_uids)} processed, {moved_recent} moved")

    # --- Phase B: bulk-archive everything older ---
    moved_old = 0
    for batch_num, batch in enumerate(chunked(old_uids, MOVE_CHUNK), 1):
        typ, _ = session.uid("MOVE", compress_uid_set(batch), '"Archive"')
        if typ == "OK":
            moved_old += len(batch)
        else:
            logger.warning(f"Archive batch {batch_num} returned {typ}")
        if batch_num % 20 == 0 or moved_old >= len(old_uids):
            logger.info(f"  archived {moved_old}/{len(old_uids)} old")
        time.sleep(BATCH_PAUSE)

    client.close()
    return {
        "recent_total": len(recent_uids),
        "recent_moved": moved_recent,
        "old_archived": moved_old,
        "by_folder": folder_counts,
    }


def gmail_cleanup(organizer) -> Dict:
    from gmail_client import GmailClient

    client = GmailClient()
    service = client._get_service()

    msg_ids = []
    page_token = None
    while True:
        resp = (
            service.users()
            .messages()
            .list(userId="me", q="in:inbox", maxResults=500, pageToken=page_token)
            .execute()
        )
        msg_ids.extend(m["id"] for m in resp.get("messages", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    logger.info(f"Gmail: {len(msg_ids)} messages in INBOX")

    by_label: Dict[str, List[str]] = {}

    for i, msg_id in enumerate(msg_ids, 1):
        try:
            msg = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg_id,
                    format="metadata",
                    metadataHeaders=["Subject", "From"],
                )
                .execute()
            )
            headers = msg.get("payload", {}).get("headers", [])
            subject = next(
                (h["value"] for h in headers if h["name"] == "Subject"), ""
            )
            sender = next(
                (h["value"] for h in headers if h["name"] == "From"), ""
            )
            snippet = msg.get("snippet", "")

            c = organizer.classify_email(subject, sender, snippet)
            label = "Marketing" if c["action"] == "archive" else c["category"]
            by_label.setdefault(label, []).append(msg_id)
        except Exception as e:
            logger.warning(f"Gmail message {msg_id} failed: {str(e)}")

        if i % 100 == 0 or i == len(msg_ids):
            logger.info(f"  classified {i}/{len(msg_ids)}")

    moved = 0
    for label, ids in by_label.items():
        for batch in chunked(ids, 900):
            if client.batch_modify(
                batch, add_labels=[label], remove_labels=["INBOX"]
            ):
                moved += len(batch)
        logger.info(f"  labeled {len(ids)} → {label} (archived from inbox)")

    return {
        "classified": len(msg_ids),
        "moved": moved,
        "by_label": {k: len(v) for k, v in by_label.items()},
    }


def main() -> int:
    from email_organizer import EmailOrganizer
    from report_mailer import ReportMailer
    import os

    organizer = EmailOrganizer(dry_run=True)  # classify_email only, no client I/O

    logger.info("=== Outlook bulk cleanup ===")
    try:
        outlook_stats = outlook_cleanup(organizer)
    except Exception as e:
        logger.error(f"Outlook cleanup aborted: {str(e)}")
        outlook_stats = {"error": str(e)}

    logger.info("=== Gmail bulk cleanup ===")
    try:
        gmail_stats = gmail_cleanup(organizer)
    except Exception as e:
        logger.error(f"Gmail cleanup aborted: {str(e)}")
        gmail_stats = {"error": str(e)}

    report = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "outlook": outlook_stats,
        "gmail": gmail_stats,
    }
    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    logger.info(f"Report saved to {REPORT_PATH}")

    try:
        mailer = ReportMailer()
        notify = os.getenv("NOTIFY_EMAIL", "totomakus@gmail.com")
        html = (
            "<h2>Bulk Inbox Cleanup Complete</h2>"
            f"<h3>Outlook</h3><pre>{json.dumps(outlook_stats, indent=2)}</pre>"
            f"<h3>Gmail</h3><pre>{json.dumps(gmail_stats, indent=2)}</pre>"
        )
        mailer.send(notify, "Bulk Inbox Cleanup — Complete", html)
    except Exception as e:
        logger.warning(f"Summary email failed (report still saved): {str(e)}")

    logger.info("Bulk cleanup complete!")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
