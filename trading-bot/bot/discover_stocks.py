"""
discover_stocks.py — Auto-discovery of high-ranked stocks from Kavout
──────────────────────────────────────────────────────────────────────
Scans Kavout's full stock rankings, finds stocks ranked High + Outperform,
and auto-adds new candidates to ranks.json. Manual review recommended before
first run to avoid unwanted tickers.

Usage:
    python bot/discover_stocks.py              # discover and add new stocks
    python bot/discover_stocks.py --dry-run    # show what would be added (no changes)
    python bot/discover_stocks.py --debug      # dump raw DOM rows
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

RANKS_FILE = Path(__file__).parent.parent / "ranks.json"
BROWSER_DATA = Path(__file__).parent.parent / ".browser_data"
DISCOVERY_LOG = Path(__file__).parent.parent / "discovery.log"

# Kavout rankings/screener URLs to try (in order of preference)
RANKINGS_URLS = [
    "https://www.kavout.com/screener",                    # Main screener interface
    "https://www.kavout.com/stocks",                      # All stocks page
    "https://www.kavout.com/ai-stock-picker",            # AI stock picker
    "https://www.kavout.com/stock-rankings",             # Stock rankings
    "https://www.kavout.com/rankings",                   # Rankings
    "https://www.kavout.com/watchlist",                  # Fallback to watchlist
]

DRY_RUN = "--dry-run" in sys.argv
DEBUG = "--debug" in sys.argv

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(DISCOVERY_LOG),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ── DOM extraction ────────────────────────────────────────────────────────────

_JS_EXTRACT_ROWS = """
() => {
    function cellsOf(el) {
        return Array.from(el.querySelectorAll('td, th, [role="cell"], [role="gridcell"]'))
            .map(c => c.innerText.replace(/\\n/g, ' ').trim())
            .filter(t => t.length > 0);
    }

    // Strategy 1 — <tr> rows (standard table)
    let rows = Array.from(document.querySelectorAll('tr'));
    if (rows.length > 1) {
        return rows.map(r => cellsOf(r)).filter(r => r.length > 0);
    }

    // Strategy 2 — ARIA role="row"
    rows = Array.from(document.querySelectorAll('[role="row"]'));
    if (rows.length > 1) {
        return rows.map(r => cellsOf(r)).filter(r => r.length > 0);
    }

    // Strategy 3 — div rows
    rows = Array.from(document.querySelectorAll('div[class]')).filter(el =>
        /row/i.test(el.className) && !el.querySelector('div[class]')
    );
    if (rows.length > 0) {
        return rows.map(r => [r.innerText.replace(/\\n/g, ' ').trim()]);
    }

    return [];
}
"""


async def extract_all_rows(page) -> list[list[str]]:
    """Extract all rows from the rankings page via JavaScript."""
    rows = await page.evaluate(_JS_EXTRACT_ROWS)
    return rows


# ── Parsing ──────────────────────────────────────────────────────────────────

async def scrape_rankings(page) -> dict[str, dict]:
    """
    Scrape Kavout's rankings/watchlist page and extract all stocks with Rank + Outlook.
    Uses JavaScript to extract from various table formats.
    """
    # Extract all rows and parse them intelligently
    structured = await page.evaluate("""
        () => {
            const results = {};
            const seenTickers = new Set();

            // Method 1: Standard <tr> rows
            let rows = Array.from(document.querySelectorAll('tr'));

            if (rows.length > 1) {
                for (const row of rows) {
                    // Get all text cells in the row
                    const cells = Array.from(row.querySelectorAll('td, th'))
                        .map(c => c.innerText.trim())
                        .filter(t => t.length > 0);

                    if (cells.length < 3) continue;

                    let ticker = null;
                    let rank = null;
                    let outlook = null;

                    // Parse cells: ticker is usually first, rank/outlook later
                    for (let i = 0; i < cells.length; i++) {
                        const cell = cells[i];
                        const upper = cell.toUpperCase();

                        // First column is often the ticker
                        if (i === 0 && cell.match(/^[A-Z]{1,5}$/) && cell.length <= 5) {
                            ticker = cell;
                        }

                        // Look for rank labels
                        if (['HIGH', 'MEDIUM', 'LOW'].includes(upper)) {
                            rank = upper;
                        }

                        // Look for outlook labels
                        if (['OUTPERFORM', 'NEUTRAL', 'UNDERPERFORM'].includes(upper)) {
                            outlook = upper;
                        }
                    }

                    // Only add if we found all three
                    if (ticker && rank && outlook && !seenTickers.has(ticker)) {
                        results[ticker] = {
                            rank: rank.charAt(0) + rank.slice(1).toLowerCase(),
                            outlook: outlook.charAt(0) + outlook.slice(1).toLowerCase()
                        };
                        seenTickers.add(ticker);
                    }
                }
            }

            // Method 2: ARIA role="row" (for modern React-based layouts)
            if (Object.keys(results).length === 0) {
                rows = Array.from(document.querySelectorAll('[role="row"]'));
                if (rows.length > 1) {
                    for (const row of rows) {
                        const cells = Array.from(row.querySelectorAll('[role="cell"], [role="gridcell"]'))
                            .map(c => c.innerText.trim())
                            .filter(t => t.length > 0);

                        if (cells.length < 3) continue;

                        let ticker = null;
                        let rank = null;
                        let outlook = null;

                        for (let i = 0; i < cells.length; i++) {
                            const cell = cells[i];
                            const upper = cell.toUpperCase();

                            if (i === 0 && cell.match(/^[A-Z]{1,5}$/) && cell.length <= 5) {
                                ticker = cell;
                            }
                            if (['HIGH', 'MEDIUM', 'LOW'].includes(upper)) {
                                rank = upper;
                            }
                            if (['OUTPERFORM', 'NEUTRAL', 'UNDERPERFORM'].includes(upper)) {
                                outlook = upper;
                            }
                        }

                        if (ticker && rank && outlook && !seenTickers.has(ticker)) {
                            results[ticker] = {
                                rank: rank.charAt(0) + rank.slice(1).toLowerCase(),
                                outlook: outlook.charAt(0) + outlook.slice(1).toLowerCase()
                            };
                            seenTickers.add(ticker);
                        }
                    }
                }
            }

            return results;
        }
    """)

    if DEBUG:
        log.info(f"\n[DEBUG] Extracted {len(structured)} stocks via JavaScript:")
        for ticker, data in sorted(list(structured.items())[:20]):
            log.info(f"  {ticker}: {data}")

    return structured


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    from playwright.async_api import async_playwright

    if not RANKS_FILE.exists():
        log.error("ranks.json not found — run bot setup first.")
        sys.exit(1)

    with open(RANKS_FILE) as f:
        current: dict = json.load(f)
    current_tickers = set(current.keys())

    BROWSER_DATA.mkdir(exist_ok=True)

    log.info("Stock Auto-Discovery")
    log.info(f"Current watchlist: {len(current_tickers)} tickers")
    log.info("")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA),
            headless=False,
            viewport={"width": 1400, "height": 900},
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()

        # Try multiple URLs to find rankings page
        found_rankings = False
        for url in RANKINGS_URLS:
            short_name = url.split('/')[-1] or url.split('/')[-2]
            log.info(f"Trying {short_name} …")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=15_000)
                await page.wait_for_timeout(3_000)

                # Check if we got a 404 or error page
                body_text = await page.inner_text("body")
                if "404" not in body_text and "could not be found" not in body_text.lower():
                    # Check if the page has any table or grid data
                    has_table = await page.query_selector("table, [role='grid'], [role='table'], [role='row']")
                    if has_table:
                        found_rankings = True
                        log.info(f"✓ Loaded: {url}")
                        break
                    else:
                        log.debug(f"  Page loaded but no table found")
                else:
                    log.debug(f"  Got error page (404 or similar)")
            except Exception as e:
                log.debug(f"  URL failed: {str(e)[:100]}")
                continue

        if not found_rankings:
            log.error("")
            log.error("⚠  Could not find Kavout rankings page.")
            log.error("  Tried: " + ", ".join(RANKINGS_URLS))
            log.error("")
            log.error("TROUBLESHOOTING:")
            log.error("  1. Check if you're logged into Kavout")
            log.error("  2. Some Kavout features require a subscription")
            log.error("  3. The rankings URL structure may have changed")
            log.error("")
            log.error("ALTERNATIVE APPROACH:")
            log.error("  Use the watchlist at https://www.kavout.com/watchlist")
            log.error("  And manually add high-ranked stocks from Kavout's website")
            log.error("")
            await browser.close()
            sys.exit(1)

        # Handle login if needed
        if any(k in page.url.lower() for k in ("login", "signin", "auth")):
            log.info("⚠  Not logged in — please log in using the browser window.")
            log.info("   Session will be saved automatically.")
            await page.wait_for_url("**", timeout=120_000)
            await page.wait_for_timeout(4_000)

        log.info("Waiting for data to load (dynamic page) …")

        # Wait for table/grid to appear
        try:
            await page.wait_for_selector("table, [role='grid'], [role='table'], [role='row']", timeout=10_000)
            log.info("  ✓ Table found")
        except:
            log.warning("  ⚠ Table selector not found, proceeding with content extraction anyway")

        await page.wait_for_timeout(2_000)

        # For dynamic pages, try scrolling to load more content
        log.info("Loading dynamic content via scrolling …")
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1_000)

        log.info("Scraping all rankings …")
        all_stocks = await scrape_rankings(page)
        log.info(f"Found {len(all_stocks)} stocks in rankings.")

        if len(all_stocks) == 0 and DEBUG:
            log.info("")
            log.info("[DEBUG] Found 0 stocks — dumping first 40 page lines:")
            body_text = await page.inner_text("body")
            for i, line in enumerate(body_text.splitlines()[:40]):
                if line.strip():
                    log.info(f"  {i:02d}: {line.strip()!r}")

        await browser.close()

    # ── Filter for High + Outperform ──────────────────────────────────────
    candidates = {
        ticker: data
        for ticker, data in all_stocks.items()
        if data.get("rank", "").capitalize() == "High" and data.get("outlook", "").capitalize() == "Outperform"
    }
    log.info(f"Filtered to {len(candidates)} with Rank=High AND Outlook=Outperform")

    # ── Find new stocks ───────────────────────────────────────────────────
    new_stocks = {
        ticker: data
        for ticker, data in candidates.items()
        if ticker not in current_tickers
    }

    if not new_stocks:
        log.info("✓ No new stocks found — watchlist up to date.")
        return

    log.info("")
    log.info(f"🔍 DISCOVERED {len(new_stocks)} NEW STOCKS:")
    log.info("")
    for ticker in sorted(new_stocks.keys()):
        log.info(f"   {ticker}")

    if DRY_RUN:
        log.info("")
        log.info("(--dry-run: no changes made)")
        return

    # ── Add to ranks.json ─────────────────────────────────────────────────
    log.info("")
    log.info("Adding new stocks to ranks.json …")
    updated = current.copy()
    for ticker, data in new_stocks.items():
        updated[ticker] = {
            "rank": data["rank"],
            "outlook": data["outlook"],
            "tech": "HOLD",  # default until first technical scrape
        }

    with open(RANKS_FILE, "w") as f:
        json.dump(updated, f, indent=2)

    log.info(f"✓ ranks.json updated: {len(current)} → {len(updated)} tickers")
    log.info("")
    log.info("NEXT STEPS:")
    log.info("  1. Review discovery.log for new stocks")
    log.info("  2. Remove any unwanted tickers from ranks.json (e.g., thinly traded, high risk)")
    log.info("  3. Run 'python bot/scrape_kavout.py --signal' to fetch technical data")
    log.info("  4. Monitor new positions in bot.log over next few days")
    log.info("")


if __name__ == "__main__":
    asyncio.run(main())
