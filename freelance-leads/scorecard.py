"""
Conversation scorecard — the numbers that decide the 30-day kill/keep call.

Tracks the ghostwriting-service outreach funnel. Machine-derived stages come
straight from lead/campaign state; human-only events (calls, clients, manual
comment touches) are logged via the CLI and stored in scorecard-log.json.

    python3 freelance-leads/scorecard.py                 # print scorecard
    python3 freelance-leads/scorecard.py log touch 8     # comments made today
    python3 freelance-leads/scorecard.py log call "Deb Matthew"
    python3 freelance-leads/scorecard.py log client "Deb Matthew" 500
"""

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LEADS_FILE = os.path.join(HERE, "health-coaches-2026-06-21.json")
REPLIES_FILE = os.path.join(HERE, "replies-inbox.json")
LOG_FILE = os.path.join(HERE, "scorecard-log.json")

CAMPAIGN_START = "2026-07-15"  # day the drip resumed; day-30 verdict due 2026-08-14


def _load(path: str, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def _manual_log() -> dict:
    return _load(LOG_FILE, {"touches": {}, "calls": [], "clients": []})


def compute(campaign_statuses: dict | None = None) -> dict:
    """Funnel counts. campaign_statuses = {sp_lead_id: status} if the caller
    already fetched them (briefing does); otherwise machine stages that need
    SendPilot are reported from local state only."""
    leads = _load(LEADS_FILE, [])
    log = _manual_log()

    connects = sum(1 for l in leads if l.get("connect_sent"))
    dms = sum(1 for l in leads if l.get("dm_sent"))
    accepted = 0
    if campaign_statuses is not None:
        accepted = sum(1 for l in leads
                       if campaign_statuses.get(l.get("sp_lead_id"))
                       in ("CONNECTION_ACCEPTED", "MESSAGE_SENT", "REPLY_RECEIVED"))
    replies = len(_load(REPLIES_FILE, []))
    touches = sum(log["touches"].values())

    return {
        "campaign_day": (int(time.time() - time.mktime(
            time.strptime(CAMPAIGN_START, "%Y-%m-%d"))) // 86400) + 1,
        "connects_sent": connects,
        "accepted": accepted if campaign_statuses is not None else None,
        "first_touch_dms": dms,
        "replies": replies,
        "comment_touches": touches,
        "calls_booked": len(log["calls"]),
        "clients": len(log["clients"]),
        "mrr": sum(c.get("amount", 0) for c in log["clients"]),
    }


def render(card: dict) -> str:
    acc = "—" if card["accepted"] is None else str(card["accepted"])
    return (
        f"Day {card['campaign_day']}/30 | "
        f"connects {card['connects_sent']} → accepts {acc} → "
        f"DMs {card['first_touch_dms']} → replies {card['replies']} | "
        f"comments {card['comment_touches']} | "
        f"calls {card['calls_booked']} | "
        f"clients {card['clients']} (${card['mrr']}/mo)"
    )


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "log":
        log = _manual_log()
        kind = sys.argv[2]
        today = time.strftime("%Y-%m-%d")
        if kind == "touch":
            log["touches"][today] = log["touches"].get(today, 0) + int(sys.argv[3])
        elif kind == "call":
            log["calls"].append({"who": sys.argv[3], "date": today})
        elif kind == "client":
            amount = int(sys.argv[4]) if len(sys.argv) > 4 else 0
            log["clients"].append({"who": sys.argv[3], "amount": amount, "date": today})
        else:
            sys.exit(f"unknown log kind: {kind} (touch|call|client)")
        with open(LOG_FILE, "w") as f:
            json.dump(log, f, indent=2)
        print("logged.")
    print(render(compute()))


if __name__ == "__main__":
    main()
