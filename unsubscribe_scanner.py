"""
Unsubscribe Scanner — READ-ONLY discovery of marketing subscriptions.

Scans every inbox in email_accounts.json and finds messages that carry a
`List-Unsubscribe` header (the RFC 2369 / RFC 8058 signal that a sender is a
real bulk/marketing list you can unenroll from). Groups by sender so you can
review before anything is unsubscribed.

This module NEVER modifies a mailbox or contacts a sender. It only reads
message headers. Actual unsubscribing lives in unsubscribe_executor.py and
runs only on the senders you approve.

Usage:
    python3 unsubscribe_scanner.py            # scan all accounts, 60-day window
    python3 unsubscribe_scanner.py --days 90  # widen the window
"""
import argparse
import json
import logging
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from email import message_from_bytes
from email.utils import parseaddr
from pathlib import Path
from typing import Dict, List, Optional

from gmail_client import GmailClient
from outlook_client import OutlookClient
from imap_client import ImapClient

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
logger = logging.getLogger("unsubscribe_scanner")
logger.setLevel(logging.INFO)

ACCOUNTS_FILE = Path("email_accounts.json")
REPORT_FILE = Path("reports/unsubscribe_scan.json")

LU_HEADERS = ["List-Unsubscribe", "List-Unsubscribe-Post", "From", "Subject", "Date"]


def parse_list_unsubscribe(lu_value: str, post_value: str) -> Dict:
    """
    Parse a List-Unsubscribe header into actionable targets.

    Returns: {http, mailto, one_click}
      http      — https unsubscribe URL, if present
      mailto    — mailto: target (address), if present
      one_click — True when RFC 8058 one-click POST is advertised
    """
    http_url: Optional[str] = None
    mailto_addr: Optional[str] = None

    for match in re.findall(r"<([^>]+)>", lu_value or ""):
        target = match.strip()
        if target.lower().startswith("http") and http_url is None:
            http_url = target
        elif target.lower().startswith("mailto:") and mailto_addr is None:
            mailto_addr = target[len("mailto:"):].split("?")[0].strip()

    one_click = "one-click" in (post_value or "").lower()
    return {"http": http_url, "mailto": mailto_addr, "one_click": one_click}


def _record(account: str, msg) -> Optional[Dict]:
    """Build a scan record from a parsed email.message, or None if no List-Unsubscribe."""
    lu_value = msg.get("List-Unsubscribe", "")
    if not lu_value:
        return None

    targets = parse_list_unsubscribe(lu_value, msg.get("List-Unsubscribe-Post", ""))
    name, addr = parseaddr(msg.get("From", ""))
    return {
        "account": account,
        "sender_email": (addr or "").lower(),
        "sender_name": name,
        "subject": msg.get("Subject", "")[:140],
        "date": msg.get("Date", ""),
        "http": targets["http"],
        "mailto": targets["mailto"],
        "one_click": targets["one_click"],
    }


# ---------------------------------------------------------------------------
# Gmail (Google API)
# ---------------------------------------------------------------------------

def scan_gmail(account: str, client: GmailClient, days: int, cap: int) -> List[Dict]:
    """Read-only scan of a Gmail inbox via batch metadata fetch."""
    service = client._get_service()
    query = f"in:inbox newer_than:{days}d"

    ids: List[str] = []
    page_token = None
    while len(ids) < cap:
        resp = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=500, pageToken=page_token)
            .execute()
        )
        ids.extend(m["id"] for m in resp.get("messages", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    ids = ids[:cap]
    logger.info(f"[{account}] {len(ids)} inbox messages in last {days}d")

    records: List[Dict] = []

    def _callback(_request_id, response, exception):
        if exception is not None:
            return
        headers = response.get("payload", {}).get("headers", [])
        msg = message_from_bytes(b"")
        for h in headers:
            msg[h["name"]] = h["value"]
        rec = _record(account, msg)
        if rec:
            records.append(rec)

    for start in range(0, len(ids), 50):
        batch = service.new_batch_http_request(callback=_callback)
        for mid in ids[start:start + 50]:
            batch.add(
                service.users().messages().get(
                    userId="me", id=mid, format="metadata",
                    metadataHeaders=LU_HEADERS,
                )
            )
        batch.execute()

    return records


# ---------------------------------------------------------------------------
# IMAP (Outlook XOAUTH2 + generic IMAP) — both expose _get_imap()
# ---------------------------------------------------------------------------

def scan_imap(account: str, client, days: int, cap: int) -> List[Dict]:
    """Read-only scan of an IMAP inbox (header-only chunked FETCH)."""
    imap = client._get_imap()
    imap.select("INBOX", readonly=True)

    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%d-%b-%Y")
    typ, data = imap.uid("SEARCH", None, f"(SINCE {since})")
    if typ != "OK":
        logger.warning(f"[{account}] SEARCH failed: {typ}")
        return []

    uids = (data[0] or b"").split()
    uids = uids[-cap:]
    logger.info(f"[{account}] {len(uids)} inbox messages since {since}")

    fields = " ".join(LU_HEADERS).upper()
    records: List[Dict] = []

    for start in range(0, len(uids), 50):
        chunk = b",".join(uids[start:start + 50]).decode()
        typ, msg_data = imap.uid(
            "FETCH", chunk, f"(BODY.PEEK[HEADER.FIELDS ({fields})])"
        )
        if typ != "OK":
            continue
        for part in msg_data or []:
            if isinstance(part, tuple) and len(part) == 2 and part[1]:
                rec = _record(account, message_from_bytes(part[1]))
                if rec:
                    records.append(rec)

    return records


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def build_client(acct: Dict):
    """Instantiate the right client for an account entry."""
    provider = acct["provider"]
    if provider == "gmail":
        return GmailClient(
            credentials_file=acct.get("credentials_file", "gmail_credentials.json"),
            token_file=acct["token_file"],
        )
    if provider == "outlook":
        return OutlookClient(token_file=acct["token_file"], email=acct["email"])
    if provider == "imap":
        return ImapClient(
            host=acct["host"], email=acct["email"],
            password_env=acct["password_env"], port=acct.get("port", 993),
        )
    raise ValueError(f"Unknown provider: {provider}")


def scan_account(acct: Dict, days: int, cap: int) -> List[Dict]:
    """Scan one account, dispatching by provider. Failures are isolated."""
    name = acct["name"]
    try:
        client = build_client(acct)
        if acct["provider"] == "gmail":
            return scan_gmail(name, client, days, cap)
        return scan_imap(name, client, days, cap)
    except Exception as e:
        logger.error(f"[{name}] scan failed: {e}")
        return []


def group_by_sender(records: List[Dict]) -> List[Dict]:
    """Collapse raw records into one row per sender with counts + method."""
    groups: Dict[str, Dict] = {}
    accounts_seen: Dict[str, set] = defaultdict(set)

    for r in records:
        key = r["sender_email"] or r["sender_name"]
        if not key:
            continue
        accounts_seen[key].add(r["account"])
        g = groups.setdefault(key, {
            "sender_email": r["sender_email"],
            "sender_name": r["sender_name"],
            "count": 0,
            "example_subject": r["subject"],
            "http": r["http"],
            "mailto": r["mailto"],
            "one_click": r["one_click"],
        })
        g["count"] += 1
        # Prefer a one-click http target if any message from this sender has it
        if r["one_click"] and r["http"]:
            g["http"], g["one_click"] = r["http"], True
        elif r["http"] and not g["http"]:
            g["http"] = r["http"]
        if r["mailto"] and not g["mailto"]:
            g["mailto"] = r["mailto"]

    rows = []
    for key, g in groups.items():
        g["accounts"] = sorted(accounts_seen[key])
        if g["one_click"] and g["http"]:
            g["method"] = "one-click"
        elif g["http"]:
            g["method"] = "http-link"
        elif g["mailto"]:
            g["method"] = "mailto"
        else:
            g["method"] = "none"
        rows.append(g)

    rows.sort(key=lambda x: x["count"], reverse=True)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only marketing-subscription scan")
    parser.add_argument("--days", type=int, default=60, help="look-back window (days)")
    parser.add_argument("--cap", type=int, default=1200, help="max messages per account")
    args = parser.parse_args()

    accounts = json.loads(ACCOUNTS_FILE.read_text())
    all_records: List[Dict] = []
    per_account: Dict[str, int] = {}

    for acct in accounts:
        recs = scan_account(acct, args.days, args.cap)
        per_account[acct["name"]] = len(recs)
        all_records.extend(recs)

    rows = group_by_sender(all_records)
    report = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "window_days": args.days,
        "per_account_hits": per_account,
        "total_messages_with_unsubscribe": len(all_records),
        "distinct_senders": len(rows),
        "senders": rows,
    }
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2))

    print("\n=== Marketing subscriptions found (List-Unsubscribe present) ===")
    print(f"Window: last {args.days} days | distinct senders: {len(rows)}\n")
    method_counts: Dict[str, int] = defaultdict(int)
    for r in rows:
        method_counts[r["method"]] += 1
    for m, c in method_counts.items():
        print(f"  {m:10s}: {c} senders")
    print(f"\nPer-account messages w/ unsubscribe: {per_account}")
    print(f"\nTop senders:")
    for r in rows[:60]:
        accts = ",".join(r["accounts"])
        print(f"  {r['count']:4d}  [{r['method']:9s}]  {r['sender_email'] or r['sender_name']:45s}  ({accts})")
    print(f"\nFull report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
