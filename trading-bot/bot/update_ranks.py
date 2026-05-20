"""
update_ranks.py — Daily Kavout data entry
──────────────────────────────────────────
Run this every evening before 8:00 PM Bangkok (9:00 AM ET).
Open Kavout → Watchlist → Overview tab, then type two letters per ticker.

Usage:
    python bot/update_ranks.py

Stock Rank:  H = High   M = Medium   L = Low
Outlook:     O = Outperform   N = Neutral   U = Underperform

Press Enter with no input to keep yesterday's value.
"""

import json
import sys
from pathlib import Path

RANKS_FILE = Path(__file__).parent.parent / "ranks.json"

RANK_MAP     = {"h": "High",         "m": "Medium",       "l": "Low"}
OUTLOOK_MAP  = {"o": "Outperform",   "n": "Neutral",      "u": "Underperform"}

RANK_SIGNAL = {
    "High":   ("▲", "32"),   # green
    "Medium": ("─", "33"),   # yellow
    "Low":    ("▼", "31"),   # red
}
OUTLOOK_SIGNAL = {
    "Outperform":   ("↑", "32"),
    "Neutral":      ("→", "33"),
    "Underperform": ("↓", "31"),
}


def color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if sys.stdout.isatty() else text


def fmt_entry(rank: str, outlook: str) -> str:
    rs, rc = RANK_SIGNAL.get(rank, ("?", "90"))
    os_, oc = OUTLOOK_SIGNAL.get(outlook, ("?", "90"))
    return f"{color(rs + ' ' + rank, rc)}  {color(os_ + ' ' + outlook, oc)}"


def parse_input(raw: str, current_map: dict, current_val: str) -> str:
    key = raw.strip().lower()
    if not key:
        return current_val
    if key in current_map:
        return current_map[key]
    print(color(f"    ⚠ Invalid — keeping '{current_val}'", "33"))
    return current_val


def main() -> None:
    if not RANKS_FILE.exists():
        sys.exit(f"[ERROR] ranks.json not found at {RANKS_FILE}")

    with open(RANKS_FILE) as f:
        data: dict = json.load(f)

    print()
    print(color("  ── Daily Kavout Entry ─────────────────────────────────", "90"))
    print(color("  Source: Kavout → Watchlist → Overview tab", "90"))
    print(color("  Rank:    H = High   M = Medium   L = Low", "90"))
    print(color("  Outlook: O = Outperform   N = Neutral   U = Underperform", "90"))
    print(color("  Tip:     Press Enter to keep yesterday's value.", "90"))
    print(color("  ──────────────────────────────────────────────────────", "90"))
    print()

    updated = {}
    changed = 0

    for ticker, vals in data.items():
        current_rank    = vals.get("rank",    "Medium")
        current_outlook = vals.get("outlook", "Neutral")
        current_display = fmt_entry(current_rank, current_outlook)

        print(f"  {ticker:<6}  {current_display}")

        raw_rank = input(color(f"          Rank    [H/M/L]:    ", "90")).strip()
        new_rank = parse_input(raw_rank, RANK_MAP, current_rank)

        raw_out  = input(color(f"          Outlook [O/N/U]:    ", "90")).strip()
        new_out  = parse_input(raw_out, OUTLOOK_MAP, current_outlook)

        if new_rank != current_rank or new_out != current_outlook:
            changed += 1

        updated[ticker] = {"rank": new_rank, "outlook": new_out}
        print()

    with open(RANKS_FILE, "w") as f:
        json.dump(updated, f, indent=2)

    print(color("  ── Saved ────────────────────────────────────────────", "90"))
    for ticker, vals in updated.items():
        print(f"  {ticker:<6}  {fmt_entry(vals['rank'], vals['outlook'])}")

    print()
    print(color(f"  {changed} ticker(s) changed → ranks.json", "32"))
    print(color("  Bot is ready for the 9:00 AM ET run.", "32"))
    print()


if __name__ == "__main__":
    main()
