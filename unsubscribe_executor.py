"""
Unsubscribe Executor — performs RFC 8058 one-click unsubscribes.

Reads reports/unsubscribe_scan.json and, for each sender whose method is
"one-click" (or "http-link" as fallback), sends an HTTP POST to the
List-Unsubscribe URL with body `List-Unsubscribe=One-Click` per RFC 8058.
If the POST is rejected, it falls back to a GET of the same URL.

This is the ONLY module that contacts senders. It acts solely on the senders
passed in (or all one-click senders by default) and writes a per-sender result
log to reports/unsubscribe_results.json.

Usage:
    python3 unsubscribe_executor.py                 # all one-click senders
    python3 unsubscribe_executor.py --dry-run       # show what would be sent
    python3 unsubscribe_executor.py --exclude a@b.com c@d.com
"""
import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import requests

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("unsubscribe_executor")

SCAN_FILE = Path("reports/unsubscribe_scan.json")
RESULTS_FILE = Path("reports/unsubscribe_results.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MailUnsubscribe/1.0)",
}
TIMEOUT = 20


def one_click(url: str) -> Dict:
    """
    Attempt an RFC 8058 one-click unsubscribe: POST first, GET as fallback.
    Returns {ok, status, via, error}.
    """
    # RFC 8058 one-click POST
    try:
        resp = requests.post(
            url,
            data={"List-Unsubscribe": "One-Click"},
            headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
            timeout=TIMEOUT,
            allow_redirects=True,
        )
        if resp.status_code < 400:
            return {"ok": True, "status": resp.status_code, "via": "POST", "error": None}
        post_status = resp.status_code
    except requests.RequestException as e:
        post_status = f"err:{type(e).__name__}"

    # Fallback: GET the unsubscribe URL (many links unsubscribe directly on load)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return {
            "ok": resp.status_code < 400,
            "status": resp.status_code,
            "via": "GET",
            "error": None if resp.status_code < 400 else f"POST={post_status}",
        }
    except requests.RequestException as e:
        return {"ok": False, "status": None, "via": "GET",
                "error": f"POST={post_status}; GET={type(e).__name__}: {e}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute one-click unsubscribes")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--exclude", nargs="*", default=[], help="sender emails to skip")
    args = parser.parse_args()

    report = json.loads(SCAN_FILE.read_text())
    exclude = {e.lower() for e in args.exclude}

    targets = [
        s for s in report["senders"]
        if s["method"] in ("one-click", "http-link")
        and s["http"]
        and s["sender_email"].lower() not in exclude
    ]

    logger.info(f"{len(targets)} senders to unsubscribe"
                f"{' (DRY RUN)' if args.dry_run else ''}\n")

    results: List[Dict] = []
    ok_count = 0

    for i, s in enumerate(targets, 1):
        sender = s["sender_email"] or s["sender_name"]
        if args.dry_run:
            logger.info(f"  [{i:2d}/{len(targets)}] WOULD POST  {sender}")
            results.append({"sender": sender, "dry_run": True, "url": s["http"]})
            continue

        res = one_click(s["http"])
        ok_count += 1 if res["ok"] else 0
        mark = "OK " if res["ok"] else "FAIL"
        logger.info(f"  [{i:2d}/{len(targets)}] {mark} {res['via']} {res['status']}  {sender}")
        results.append({
            "sender": sender,
            "accounts": s["accounts"],
            "count": s["count"],
            "url": s["http"],
            **res,
        })

    if not args.dry_run:
        out = {
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "attempted": len(targets),
            "succeeded": ok_count,
            "failed": len(targets) - ok_count,
            "results": results,
        }
        RESULTS_FILE.write_text(json.dumps(out, indent=2))
        logger.info(f"\n{ok_count}/{len(targets)} succeeded. Log: {RESULTS_FILE}")
        failed = [r for r in results if not r["ok"]]
        if failed:
            logger.info("\nFailed (try manually):")
            for r in failed:
                logger.info(f"  {r['sender']}  -> {r['url'][:80]}")


if __name__ == "__main__":
    main()
