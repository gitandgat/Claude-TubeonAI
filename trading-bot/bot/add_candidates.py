"""
add_candidates.py — Simple manual watchlist expansion
────────────────────────────────────────────────────
Add new tickers from a list (copy-pasted from Kavout AI Stock Picker
or any other source) with sector diversity review.

Usage:
    python bot/add_candidates.py
    # Paste tickers when prompted, one per line, then Ctrl+D (Mac) or Ctrl+Z (Windows)

Example input:
    MSCI
    SCHW
    MA
    V
    GLD
"""

from __future__ import annotations

import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

RANKS_FILE = Path(__file__).parent.parent / "ranks.json"
CANDIDATES_LOG = Path(__file__).parent.parent / "candidates.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(CANDIDATES_LOG),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def main() -> None:
    if not RANKS_FILE.exists():
        log.error("ranks.json not found")
        sys.exit(1)

    with open(RANKS_FILE) as f:
        current: dict = json.load(f)
    current_tickers = set(current.keys())

    log.info("Add Candidates to Watchlist")
    log.info(f"Current watchlist: {len(current_tickers)} tickers")
    log.info("")
    log.info("Paste candidate tickers (one per line, then Ctrl+D on Mac / Ctrl+Z on Windows):")
    log.info("")

    # Read tickers from stdin
    new_tickers = []
    try:
        while True:
            line = input().strip().upper()
            if line:
                new_tickers.append(line)
    except EOFError:
        pass

    if not new_tickers:
        log.info("No tickers entered.")
        return

    log.info("")
    log.info(f"Processing {len(new_tickers)} candidate(s) …")
    log.info("")

    # Filter for new ones
    candidates = [t for t in new_tickers if t not in current_tickers]

    if not candidates:
        log.info("✓ All tickers already in watchlist.")
        return

    log.info(f"New candidates: {len(candidates)}")
    for ticker in sorted(candidates):
        log.info(f"  • {ticker}")

    # Sector diversity check (simple heuristic)
    sector_map = {
        # Tech
        "AAPL": "Technology",
        "MSFT": "Technology",
        "GOOGL": "Technology",
        "NVDA": "Technology",
        "TSM": "Technology",
        "ORCL": "Technology",
        "PLTR": "Technology",
        "HUBS": "Technology",
        # Financial Services / FinTech
        "MA": "Financials",
        "V": "Financials",
        "SCHW": "Financials",
        "BLK": "Financials",
        "JPM": "Financials",
        # Healthcare
        "UNH": "Healthcare",
        "JNJ": "Healthcare",
        "ABBV": "Healthcare",
        # Industrials
        "BA": "Industrials",
        "CAT": "Industrials",
        "LMT": "Industrials",
        # Consumer / Retail
        "AMZN": "Consumer",
        "TSLA": "Consumer",
        "ULTA": "Consumer",
        "ELV": "Consumer",
        "NFLX": "Consumer",
        # Commodities / ETFs
        "GLD": "Commodities",
        "USO": "Commodities",
        "DBC": "Commodities",
        # Real Estate
        "SPG": "Real Estate",
        "PLD": "Real Estate",
        # Utilities
        "NEE": "Utilities",
        "DUK": "Utilities",
    }

    log.info("")
    log.info("Sector distribution check:")
    log.info("")

    # Current sectors
    current_by_sector = defaultdict(list)
    for ticker in current_tickers:
        sector = sector_map.get(ticker, "Other")
        current_by_sector[sector].append(ticker)

    log.info("Current watchlist:")
    for sector in sorted(current_by_sector.keys()):
        count = len(current_by_sector[sector])
        pct = (count / len(current_tickers)) * 100
        log.info(f"  {sector:<15} {count:>2} ({pct:>5.1f}%)")

    log.info("")
    log.info("New candidates:")
    candidates_by_sector = defaultdict(list)
    for ticker in candidates:
        sector = sector_map.get(ticker, "Other")
        candidates_by_sector[sector].append(ticker)

    for sector in sorted(candidates_by_sector.keys()):
        tickers = ", ".join(candidates_by_sector[sector])
        log.info(f"  {sector:<15} {tickers}")

    # Confirm addition
    log.info("")
    log.info("This will:")
    log.info(f"  • Add {len(candidates)} new tickers")
    log.info(f"  • Expand watchlist to {len(current_tickers) + len(candidates)} tickers")
    log.info("  • Set default rank/outlook/tech values")
    log.info("  • Be picked up by next scraper run")

    log.info("")
    while True:
        confirm = input("Proceed? (y/n): ").strip().lower()
        if confirm == "y":
            break
        elif confirm == "n":
            log.info("Cancelled.")
            return

    # Add to ranks.json
    log.info("")
    log.info("Adding candidates …")
    updated = current.copy()
    for ticker in candidates:
        updated[ticker] = {
            "rank": "Medium",
            "outlook": "Neutral",
            "tech": "HOLD",
        }

    with open(RANKS_FILE, "w") as f:
        json.dump(updated, f, indent=2)

    log.info(f"✓ ranks.json updated: {len(current)} → {len(updated)} tickers")
    log.info("")
    log.info("NEXT STEPS:")
    log.info("  1. Run 'python bot/scrape_kavout.py --signal' to fetch rank/outlook/tech")
    log.info("  2. Review candidates.log to confirm additions")
    log.info("  3. Monitor new stocks in bot.log over next few days")
    log.info("")


if __name__ == "__main__":
    main()
