"""
discover_ai_picks.py — Smart auto-discovery with manual approval
──────────────────────────────────────────────────────────────────
Scrapes Kavout's AI Stock Picker, extracts top picks by sector,
filters for diversity, and presents candidates for manual approval.
Approved stocks get added to ranks.json automatically.

Usage:
    python bot/discover_ai_picks.py              # interactive approval
    python bot/discover_ai_picks.py --auto       # auto-approve all (use with caution)
    python bot/discover_ai_picks.py --dry-run    # show candidates, no changes
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

RANKS_FILE = Path(__file__).parent.parent / "ranks.json"
BROWSER_DATA = Path(__file__).parent.parent / ".browser_data"
CANDIDATES_LOG = Path(__file__).parent.parent / "candidates.log"

AI_PICKER_URL = "https://www.kavout.com/ai-stock-picker/top-ai-stock-picks?universe=SPX&region=US"

AUTO_APPROVE = "--auto" in sys.argv
DRY_RUN = "--dry-run" in sys.argv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(CANDIDATES_LOG),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ── Stock data extraction ─────────────────────────────────────────────────────

async def scrape_ai_picks(page) -> list[dict]:
    """
    Scrape AI Stock Picker page and extract stock data.
    Returns list of {ticker, price, sector, market_cap, entry_date}
    """
    stocks = await page.evaluate("""
        () => {
            const results = [];

            // Look for all rows (tr or div-based)
            const rows = Array.from(document.querySelectorAll('tr, [role="row"]'));

            for (const row of rows) {
                const cells = Array.from(row.querySelectorAll('td, [role="cell"], [role="gridcell"]'))
                    .map(c => c.innerText.trim())
                    .filter(c => c);

                if (cells.length < 3) continue;

                // Try to extract ticker, price, sector from cells
                let ticker = null;
                let price = null;
                let sector = null;
                let market_cap = null;
                let entry_date = null;

                for (let i = 0; i < cells.length; i++) {
                    const cell = cells[i];

                    // Ticker: 1-5 uppercase letters
                    if (!ticker && /^[A-Z]{1,5}$/.test(cell) && cell.length <= 5) {
                        ticker = cell;
                    }

                    // Price: $ followed by number
                    if (!price && cell.match(/^\\$?[0-9,]+\\.?[0-9]*$/)) {
                        price = parseFloat(cell.replace(/[$,]/g, ''));
                    }

                    // Sector: common sector names
                    if (!sector && /Technology|Healthcare|Financials|Industrials|Energy|Consumer|Materials|Utilities|Real Estate|Communication/i.test(cell)) {
                        sector = cell;
                    }

                    // Market cap: $ followed by letter
                    if (!market_cap && cell.match(/^\\$[0-9,.]+[KMBT]$/)) {
                        market_cap = cell;
                    }

                    // Entry date: looks like date
                    if (!entry_date && cell.match(/^20\\d{2}-\\d{2}-\\d{2}$/)) {
                        entry_date = cell;
                    }
                }

                if (ticker && price) {
                    results.push({
                        ticker,
                        price,
                        sector: sector || 'Unknown',
                        market_cap: market_cap || 'N/A',
                        entry_date: entry_date || 'N/A'
                    });
                }
            }

            return results;
        }
    """)

    return stocks


# ── Sector diversity analysis ─────────────────────────────────────────────────

def analyze_sector_diversity(current: dict, candidates: list[dict]) -> dict:
    """
    Analyze sector distribution to suggest diversity-balanced additions.
    Returns {sector: [stocks]} for candidates.
    """
    # Count current watchlist by sector
    current_sectors = defaultdict(list)
    for ticker in current.keys():
        # Mock sector assignment (would be better with real data)
        sector_map = {
            "AAPL": "Technology",
            "MSFT": "Technology",
            "GOOGL": "Technology",
            "NVDA": "Technology",
            "TSM": "Technology",
            "AMZN": "Consumer",
            "NFLX": "Consumer",
            "ULTA": "Consumer",
            "ORCL": "Technology",
            "PLTR": "Technology",
            "HUBS": "Technology",
            "TSLA": "Consumer",
            "BRK-B": "Financials",
            "ELV": "Consumer",
        }
        sector = sector_map.get(ticker, "Other")
        current_sectors[sector].append(ticker)

    # Group candidates by sector
    candidate_sectors = defaultdict(list)
    for stock in candidates:
        sector = stock.get("sector", "Unknown")
        candidate_sectors[sector].append(stock)

    return {
        "current": dict(current_sectors),
        "candidates": dict(candidate_sectors),
    }


# ── Interactive approval ──────────────────────────────────────────────────────

def interactive_approve(candidates: list[dict], current: set[str]) -> list[dict]:
    """
    Present candidates to user for approval, one by one.
    Returns list of approved stocks.
    """
    approved = []

    log.info("")
    log.info("=" * 70)
    log.info(f"CANDIDATE REVIEW: {len(candidates)} new stocks from AI Stock Picker")
    log.info("=" * 70)
    log.info("")

    # Group by sector
    by_sector = defaultdict(list)
    for stock in candidates:
        by_sector[stock["sector"]].append(stock)

    for sector in sorted(by_sector.keys()):
        log.info(f"\n📊 {sector}")
        log.info("-" * 70)

        for stock in by_sector[sector]:
            ticker = stock["ticker"]
            price = stock["price"]
            mcap = stock["market_cap"]
            log.info(f"  {ticker:<7} @ ${price:>8.2f}  |  {mcap:<10}  |  {stock['entry_date']}")

            if AUTO_APPROVE:
                log.info(f"    ✓ Auto-approved")
                approved.append(stock)
            else:
                while True:
                    resp = input(f"    Add {ticker} to watchlist? (y/n/skip): ").strip().lower()
                    if resp == "y":
                        log.info(f"    ✓ Approved")
                        approved.append(stock)
                        break
                    elif resp == "n":
                        log.info(f"    ✗ Rejected")
                        break
                    elif resp == "skip":
                        log.info(f"    ⊘ Skipped (ask later)")
                        break

    return approved


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    from playwright.async_api import async_playwright

    if not RANKS_FILE.exists():
        log.error("ranks.json not found")
        sys.exit(1)

    with open(RANKS_FILE) as f:
        current: dict = json.load(f)
    current_tickers = set(current.keys())

    BROWSER_DATA.mkdir(exist_ok=True)

    log.info("AI Stock Picker — Auto-Discovery with Approval")
    log.info(f"Current watchlist: {len(current_tickers)} tickers")
    log.info("")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA),
            headless=False,
            viewport={"width": 1400, "height": 900},
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()

        log.info("Opening AI Stock Picker …")
        await page.goto(AI_PICKER_URL, wait_until="networkidle", timeout=30_000)
        await page.wait_for_timeout(5_000)

        log.info("Scraping top picks …")
        all_picks = await scrape_ai_picks(page)
        log.info(f"Found {len(all_picks)} stocks on page")

        await browser.close()

    # ── Filter for new stocks ─────────────────────────────────────────────
    new_candidates = [s for s in all_picks if s["ticker"] not in current_tickers]
    log.info(f"New candidates: {len(new_candidates)} (not in current watchlist)")

    if not new_candidates:
        log.info("✓ No new stocks found — watchlist is complete.")
        return

    # ── Analyze diversity ─────────────────────────────────────────────────
    diversity = analyze_sector_diversity(current, new_candidates)
    log.info("")
    log.info("Current watchlist by sector:")
    for sector, tickers in sorted(diversity["current"].items()):
        log.info(f"  {sector:<15} {len(tickers):>2} stocks: {', '.join(tickers)}")

    log.info("")
    log.info("New candidates by sector:")
    for sector, stocks in sorted(diversity["candidates"].items()):
        log.info(f"  {sector:<15} {len(stocks):>2} stocks")

    # ── Interactive approval ──────────────────────────────────────────────
    if DRY_RUN:
        log.info("")
        log.info("(--dry-run: no changes will be made)")
        return

    approved = interactive_approve(new_candidates, current_tickers)

    if not approved:
        log.info("")
        log.info("No stocks approved — watchlist unchanged.")
        return

    # ── Add to ranks.json ─────────────────────────────────────────────────
    log.info("")
    log.info(f"Adding {len(approved)} stocks to ranks.json …")
    updated = current.copy()
    for stock in approved:
        ticker = stock["ticker"]
        updated[ticker] = {
            "rank": "Medium",  # default until scraper updates
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
    log.info("  3. Bot will trade new stocks starting next scheduled run (9 AM ET)")
    log.info("")


if __name__ == "__main__":
    asyncio.run(main())
