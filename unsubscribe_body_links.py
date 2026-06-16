"""
Body-link Unsubscribe — fallback for senders without a usable
List-Unsubscribe header (method "none" or "mailto" in the scan report).

For each such sender it finds their most recent message on the relevant
IMAP account, pulls the HTML body, extracts the best "unsubscribe" link from
the footer, and hits it (POST one-click, then GET) via unsubscribe_executor.

Why this exists: ConvertKit-style newsletters often advertise only a mailto:
in the header, and some senders ship a malformed header — but nearly all of
them still carry a clickable unsubscribe link in the body. This handles those
without needing SMTP send capability.

Usage:
    python3 unsubscribe_body_links.py --dry-run
    python3 unsubscribe_body_links.py
"""
import argparse
import json
import logging
import re
from datetime import datetime, timezone
from email import message_from_bytes
from html import unescape
from pathlib import Path
from typing import Dict, List, Optional

from outlook_client import OutlookClient
from imap_client import ImapClient
from unsubscribe_executor import one_click

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("unsubscribe_body_links")

ACCOUNTS_FILE = Path("email_accounts.json")
SCAN_FILE = Path("reports/unsubscribe_scan.json")
RESULTS_FILE = Path("reports/unsubscribe_body_results.json")

# Never act on the user's own broadcast domain.
PROTECTED_SENDERS = {"sahawat@crosswalkwisdom.com"}

ANCHOR_RE = re.compile(
    r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")


def _score_link(url: str, text: str) -> int:
    """Higher score = more likely the real unsubscribe link."""
    t = TAG_RE.sub("", text).lower().strip()
    u = url.lower()
    score = 0
    if "unsubscribe" in t:
        score += 10
    if "opt out" in t or "opt-out" in t:
        score += 6
    if any(k in t for k in ("email preference", "manage your", "manage subscription",
                            "no longer", "manage preferences", "update your preferences")):
        score += 4
    if any(k in u for k in ("unsubscribe", "optout", "opt-out", "unsub", "/u/", "remove")):
        score += 3
    return score


def extract_unsub_link(html: str) -> Optional[str]:
    """Pick the best unsubscribe URL from an HTML body, or None."""
    best_url, best_score = None, 0
    for url, text in ANCHOR_RE.findall(html or ""):
        url = unescape(url.strip())
        if not url.lower().startswith("http"):
            continue
        s = _score_link(url, text)
        if s > best_score:
            best_url, best_score = url, s
    return best_url if best_score >= 3 else None


def _html_from_message(raw: bytes) -> str:
    """Return decoded text/html (preferred) or text/plain from a raw message."""
    msg = message_from_bytes(raw)
    html, text = "", ""
    for part in msg.walk():
        ctype = part.get_content_type()
        if ctype not in ("text/html", "text/plain"):
            continue
        try:
            payload = part.get_payload(decode=True) or b""
            decoded = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        except Exception:
            continue
        if ctype == "text/html":
            html += decoded
        else:
            text += decoded
    return html or text


def fetch_latest_body(client, sender_email: str) -> Optional[str]:
    """Find the newest INBOX message from sender_email and return its body."""
    imap = client._get_imap()
    imap.select("INBOX", readonly=True)
    typ, data = imap.uid("SEARCH", None, f'(FROM "{sender_email}")')
    if typ != "OK" or not (data and data[0]):
        return None
    uid = data[0].split()[-1].decode()
    typ, msg_data = imap.uid("FETCH", uid, "(BODY.PEEK[])")
    if typ != "OK":
        return None
    for part in msg_data or []:
        if isinstance(part, tuple) and len(part) == 2 and part[1]:
            return _html_from_message(part[1])
    return None


def build_imap_clients(accounts: List[Dict]) -> Dict[str, object]:
    """Instantiate only the IMAP-capable accounts (outlook + imap), keyed by name."""
    clients: Dict[str, object] = {}
    for a in accounts:
        if a["provider"] == "outlook":
            clients[a["name"]] = OutlookClient(token_file=a["token_file"], email=a["email"])
        elif a["provider"] == "imap":
            clients[a["name"]] = ImapClient(
                host=a["host"], email=a["email"],
                password_env=a["password_env"], port=a.get("port", 993),
            )
    return clients


def main() -> None:
    parser = argparse.ArgumentParser(description="Unsubscribe via body links")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    accounts = json.loads(ACCOUNTS_FILE.read_text())
    report = json.loads(SCAN_FILE.read_text())
    clients = build_imap_clients(accounts)

    targets = [
        s for s in report["senders"]
        if s["method"] in ("none", "mailto")
        and s["sender_email"] not in PROTECTED_SENDERS
    ]
    logger.info(f"{len(targets)} senders to resolve via body link"
                f"{' (DRY RUN)' if args.dry_run else ''}\n")

    results: List[Dict] = []
    ok = 0
    for i, s in enumerate(targets, 1):
        sender = s["sender_email"]
        # Search the IMAP account(s) this sender appeared in.
        link = None
        for acct in s["accounts"]:
            client = clients.get(acct)
            if not client:
                continue
            try:
                body = fetch_latest_body(client, sender)
                link = extract_unsub_link(body) if body else None
                if link:
                    break
            except Exception as e:
                logger.info(f"      ({acct} fetch error: {type(e).__name__})")

        if not link:
            logger.info(f"  [{i:2d}/{len(targets)}] NO-LINK   {sender}")
            results.append({"sender": sender, "ok": False, "reason": "no link found"})
            continue

        if args.dry_run:
            logger.info(f"  [{i:2d}/{len(targets)}] FOUND     {sender}  -> {link[:70]}")
            results.append({"sender": sender, "dry_run": True, "url": link})
            continue

        res = one_click(link)
        ok += 1 if res["ok"] else 0
        mark = "OK  " if res["ok"] else "FAIL"
        logger.info(f"  [{i:2d}/{len(targets)}] {mark} {res['via']} {res['status']}  {sender}")
        results.append({"sender": sender, "url": link, **res})

    if not args.dry_run:
        RESULTS_FILE.write_text(json.dumps({
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "attempted": len(targets),
            "succeeded": ok,
            "results": results,
        }, indent=2))
        logger.info(f"\n{ok}/{len(targets)} succeeded. Log: {RESULTS_FILE}")
        leftover = [r for r in results if not r.get("ok")]
        if leftover:
            logger.info("\nStill need a manual click (no link / confirmation page):")
            for r in leftover:
                logger.info(f"  {r['sender']}"
                            + (f"  -> {r['url'][:70]}" if r.get("url") else f"  ({r.get('reason','')})"))


if __name__ == "__main__":
    main()
