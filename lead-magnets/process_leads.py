#!/usr/bin/env python3
"""
Lead queue processor — auto-delivers the lead magnet to new leads.

This is the "fires automatically when a new lead lands" piece. A LaunchAgent
runs it on an interval; it reads new leads from a queue file and delivers to
each exactly once (with bounded retries), so the queue is the single place any
source — a form, Zapier, a webhook, or a manual append — drops a lead.

Queue format (leads_queue.jsonl), one JSON object per line:
    {"email": "lead@x.com", "name": "Dr. Asha Rao"}

State is tracked in leads_state.json so a lead is never emailed twice and a
permanently failing address is dead-lettered after MAX_ATTEMPTS.

    python process_leads.py            # process pending leads (live)
    python process_leads.py --dry-run  # show what would be delivered
"""

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from deliver_lead_magnet import deliver  # same dir

HERE = Path(__file__).resolve().parent
QUEUE_FILE = HERE / "leads_queue.jsonl"
STATE_FILE = HERE / "leads_state.json"
PDF_FILE = HERE / "crosswalk-img-pivot-map.pdf"
MAX_ATTEMPTS = 3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("process_leads")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.warning("State file corrupt — starting fresh.")
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def read_queue() -> list[dict]:
    if not QUEUE_FILE.exists():
        return []
    leads = []
    for n, line in enumerate(QUEUE_FILE.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            obj = json.loads(line)
            if obj.get("email"):
                leads.append({"email": obj["email"].strip(), "name": obj.get("name", "").strip()})
            else:
                log.warning("Queue line %d has no email — skipped.", n)
        except json.JSONDecodeError:
            log.warning("Queue line %d is not valid JSON — skipped: %s", n, line[:80])
    return leads


def is_done(entry: dict | None) -> bool:
    if not entry:
        return False
    return entry.get("status") == "sent" or entry.get("attempts", 0) >= MAX_ATTEMPTS


def main() -> int:
    ap = argparse.ArgumentParser(description="Process the lead-magnet delivery queue.")
    ap.add_argument("--dry-run", action="store_true", help="Show pending leads; deliver nothing.")
    args = ap.parse_args()

    leads = read_queue()
    if not leads:
        log.info("No leads in queue.")
        return 0

    if not PDF_FILE.exists():
        log.error("PDF missing: %s — run generate_lead_magnet.py first.", PDF_FILE.name)
        return 1

    state = load_state()
    pending = [l for l in leads if not is_done(state.get(l["email"].lower()))]
    log.info("%d lead(s) in queue, %d pending.", len(leads), len(pending))

    if args.dry_run:
        for lead in pending:
            log.info("WOULD deliver to %s (%s)", lead["email"], lead["name"] or "no name")
        return 0

    sent = 0
    for lead in pending:
        key = lead["email"].lower()
        entry = state.get(key, {"attempts": 0})
        entry["attempts"] = entry.get("attempts", 0) + 1
        entry["last_attempt"] = datetime.now(timezone.utc).isoformat()
        rc = deliver(lead["email"], lead["name"], PDF_FILE, dry_run=False)
        if rc == 0:
            entry["status"] = "sent"
            sent += 1
            log.info("Delivered to %s", lead["email"])
        else:
            entry["status"] = "failed"
            log.error("Delivery failed for %s (attempt %d/%d)",
                      lead["email"], entry["attempts"], MAX_ATTEMPTS)
        state[key] = entry
        save_state(state)

    log.info("Done. %d delivered this run.", sent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
