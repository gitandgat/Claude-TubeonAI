"""
scrape_kavout.py — Automated Kavout Watchlist scraper
──────────────────────────────────────────────────────
Opens Kavout in a browser, scrapes Overview + Technical tabs,
calculates signals, and updates ranks.json automatically.

First run:  browser opens visibly → log in once → session saved.
After that: runs headless, fully automatic.

Usage:
    python bot/scrape_kavout.py                # overview + technical
    python bot/scrape_kavout.py --signal       # add smart signal tab
    python bot/scrape_kavout.py --signal-only  # smart signal only
    python bot/scrape_kavout.py --debug        # dump raw DOM rows
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Set, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

RANKS_FILE    = Path(__file__).parent.parent / "ranks.json"
BROWSER_DATA  = Path(__file__).parent.parent / ".browser_data"
WATCHLIST_URL = "https://www.kavout.com/watchlist"

DEBUG = "--debug" in sys.argv
SCRAPE_SIGNAL = "--signal" in sys.argv or "--signal-only" in sys.argv
SIGNAL_ONLY = "--signal-only" in sys.argv

# Polygon API
POLYGON_BASE = "https://api.polygon.io"
POLYGON_KEY = os.getenv("MASSIVE_API_KEY")


# ── Signal rules ──────────────────────────────────────────────────────────────

def calc_tech(price: float, ma20: float, rsi: float, adx: float) -> str:
    if price > ma20 and rsi < 80 and adx > 20:
        return "BUY"
    if price < ma20 or rsi < 35:
        return "SELL"
    return "HOLD"


def final_signal(rank: str, outlook: str, tech: str) -> str:
    if rank == "High" and outlook == "Outperform" and tech == "BUY":
        return "BUY"
    if rank == "Low" or outlook == "Underperform" or tech == "SELL":
        return "SELL"
    return "HOLD"


# ── Polygon API helpers ───────────────────────────────────────────────────────

def polygon_get(url: str, params: dict) -> dict | None:
    """GET a Polygon endpoint with retry logic."""
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 429:
                time.sleep(60)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt == 2:
                return None
    return None


def fetch_minervini_data(ticker: str) -> dict | None:
    """Fetch MA, RS rank, distance from 52W high, and volume ratio."""
    if not POLYGON_KEY:
        return None

    try:
        result = {}

        # Fetch MA20, MA50, MA200
        for window in [20, 50, 200]:
            data = polygon_get(
                f"{POLYGON_BASE}/v1/indicators/sma/{ticker}",
                {
                    "timespan": "day",
                    "adjusted": "true",
                    "window": window,
                    "series_type": "close",
                    "limit": 1,
                    "order": "desc",
                    "apiKey": POLYGON_KEY,
                },
            )
            if data and data.get("results", {}).get("values"):
                ma_val = float(data["results"]["values"][0]["value"])
                result[f"ma_{window}"] = round(ma_val, 2)
            time.sleep(2)

        # Fetch 52-week high (from 1-year bars)
        data = polygon_get(
            f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/range/1/day/2024-01-01/2025-12-31",
            {"adjusted": "true", "apiKey": POLYGON_KEY},
        )
        if data and data.get("results"):
            closes = [float(r.get("c", 0)) for r in data["results"][-252:]]
            if closes:
                h52w = max(closes)
                close = closes[-1] if closes else 0
                if h52w > 0:
                    result["distance_52w"] = round((h52w - close) / h52w, 3)
        time.sleep(2)

        # Fetch volume ratio (today vs 50-day avg)
        data = polygon_get(
            f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/prev",
            {"adjusted": "true", "apiKey": POLYGON_KEY},
        )
        today_vol = float(data.get("results", [{}])[0].get("v", 0)) if data else 0

        if today_vol > 0:
            data = polygon_get(
                f"{POLYGON_BASE}/v1/indicators/sma/{ticker}",
                {
                    "timespan": "day",
                    "adjusted": "true",
                    "window": 50,
                    "series_type": "volume",
                    "limit": 1,
                    "order": "desc",
                    "apiKey": POLYGON_KEY,
                },
            )
            if data and data.get("results", {}).get("values"):
                avg_vol = float(data["results"]["values"][0]["value"])
                if avg_vol > 0:
                    result["volume_sma"] = round(today_vol / avg_vol, 2)

        return result if result else None

    except Exception as e:
        print(f"  ⚠ Could not fetch Minervini data for {ticker}: {e}")
        return None


# ── Text parsing ──────────────────────────────────────────────────────────────

def to_float(text: str) -> float | None:
    cleaned = re.sub(r"[,$%+TBMKx\s]", "", text)
    try:
        return float(cleaned)
    except ValueError:
        return None


# ── DOM extraction via JavaScript ─────────────────────────────────────────────

# JavaScript that extracts all table-like rows from the page.
# Strategy 1: standard <table> rows
# Strategy 2: MUI/React-style [role="row"] elements
# Strategy 3: any div whose class contains "row"
_JS_EXTRACT_ROWS = """
() => {
    function cellsOf(el) {
        return Array.from(el.querySelectorAll('td, th, [role="cell"], [role="gridcell"]'))
            .map(c => c.innerText.replace(/\\n/g, ' ').trim())
            .filter(t => t.length > 0);
    }

    // Strategy 1 — <tr> rows
    let rows = Array.from(document.querySelectorAll('tr'));
    if (rows.length > 1) {
        return rows.map(r => cellsOf(r)).filter(r => r.length > 0);
    }

    // Strategy 2 — ARIA role="row"
    rows = Array.from(document.querySelectorAll('[role="row"]'));
    if (rows.length > 1) {
        return rows.map(r => cellsOf(r)).filter(r => r.length > 0);
    }

    // Strategy 3 — div rows (class contains "row" case-insensitive)
    rows = Array.from(document.querySelectorAll('div[class]')).filter(el =>
        /row/i.test(el.className) && !el.querySelector('div[class]')
    );
    if (rows.length > 0) {
        return rows.map(r => [r.innerText.replace(/\\n/g, ' ').trim()]);
    }

    // Strategy 4 — full page text split into lines (last resort)
    return document.body.innerText
        .split('\\n')
        .map(l => [l.trim()])
        .filter(r => r[0].length > 0);
}
"""


async def extract_ticker_rows(page, known_tickers: Set[str]) -> Dict[str, List[str]]:
    """
    Run JS to pull DOM rows, then find rows whose first non-empty token
    is a known ticker symbol.
    """
    raw_rows: list[list[str]] = await page.evaluate(_JS_EXTRACT_ROWS)

    if DEBUG:
        print("\n  [DEBUG] Raw DOM rows:")
        for i, r in enumerate(raw_rows[:40]):
            print(f"    {i:02d}: {r}")

    result: Dict[str, List[str]] = {}
    for row in raw_rows:
        if not row:
            continue
        # The ticker is usually the first cell; check it directly
        candidate = row[0].strip().upper()
        if candidate in known_tickers:
            result[candidate] = row[1:]
            continue
        # Some layouts prepend a rank number or icon — check second token too
        if len(row) > 1 and row[1].strip().upper() in known_tickers:
            result[row[1].strip().upper()] = row[2:]

    return result


# ── Tab scrapers ──────────────────────────────────────────────────────────────

async def scrape_overview(page, known_tickers: Set[str]) -> Dict[str, Dict]:
    rows = await extract_ticker_rows(page, known_tickers)
    result: Dict[str, Dict] = {}
    for ticker, cells in rows.items():
        rank    = "Medium"
        outlook = "Neutral"
        for token in cells:
            t = token.strip()
            if t in ("High", "Medium", "Low"):
                rank = t
            if t in ("Outperform", "Neutral", "Underperform"):
                outlook = t
        result[ticker] = {"rank": rank, "outlook": outlook}
    return result


async def scrape_technical(page, known_tickers: Set[str]) -> Dict[str, Dict]:
    """
    Expected column order: Price | MA5 | MA10 | MA20 | MA50 | RSI(14) | ADX(14) | Action
    """
    rows = await extract_ticker_rows(page, known_tickers)
    result: Dict[str, Dict] = {}

    for ticker, cells in rows.items():
        price: float | None = None
        numbers: list[float] = []

        for token in cells:
            t = token.strip()
            if t.startswith("$") and price is None:
                price = to_float(t)
            else:
                val = to_float(t)
                if val is not None and val > 0:
                    numbers.append(val)

        # Expected order after price: MA5, MA10, MA20, MA50, RSI, ADX
        if price is not None and len(numbers) >= 6:
            _ma5, _ma10, ma20, _ma50, rsi, adx = numbers[:6]
            tech = calc_tech(price, ma20, rsi, adx)
            result[ticker] = {"tech": tech, "price": price, "ma20": ma20, "rsi": rsi, "adx": adx}
        else:
            if DEBUG:
                print(f"  [DEBUG] {ticker}: price={price}, numbers={numbers}")
            print(f"  ⚠  {ticker}: not enough technical data — keeping previous value.")
            result[ticker] = {"tech": None}

    return result


async def scrape_smart_signal(page, known_tickers: Set[str]) -> Dict[str, Dict]:
    """
    Scrape Kavout's Smart Signal tab.
    Extracts the composite signal (BUY/HOLD/SELL) and any supporting metrics.
    """
    rows = await extract_ticker_rows(page, known_tickers)
    result: Dict[str, Dict] = {}

    for ticker, cells in rows.items():
        signal = "HOLD"  # default
        # Look for BUY, SELL, HOLD in the row
        for token in cells:
            t = token.strip().upper()
            if t in ("BUY", "SELL", "HOLD"):
                signal = t
                break
        result[ticker] = {"smart_signal": signal}

    return result


# ── Tab navigation ────────────────────────────────────────────────────────────

async def click_tab(page, *labels: str) -> bool:
    for label in labels:
        try:
            el = page.get_by_role("tab", name=re.compile(label, re.I))
            if await el.count():
                await el.first.click()
                return True
            el = page.get_by_text(re.compile(rf"^{label}$", re.I))
            if await el.count():
                await el.first.click()
                return True
        except Exception:
            pass
    return False


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    from playwright.async_api import async_playwright

    if not RANKS_FILE.exists():
        sys.exit("[ERROR] ranks.json not found — run the bot setup first.")

    with open(RANKS_FILE) as f:
        current: dict = json.load(f)
    known_tickers = set(current.keys())

    BROWSER_DATA.mkdir(exist_ok=True)

    print("\n  ── Kavout Scraper ───────────────────────────────────────")
    print(f"  Watchlist: {', '.join(sorted(known_tickers))}")
    print()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA),
            headless=False,
            viewport={"width": 1400, "height": 900},
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()

        print("  Opening Kavout Watchlist …")
        await page.goto(WATCHLIST_URL, wait_until="networkidle", timeout=30_000)
        await page.wait_for_timeout(3_000)

        if any(k in page.url.lower() for k in ("login", "signin", "auth")):
            print()
            print("  ⚠  Not logged in — please log in using the browser window.")
            print("     This only happens once. Session will be saved automatically.")
            print()
            await page.wait_for_url("**/watchlist**", timeout=120_000)
            await page.wait_for_timeout(4_000)

        overview = {}
        technical = {}
        smart_signal = {}

        if not SIGNAL_ONLY:
            # ── Overview tab ──────────────────────────────────────────────────────
            print("  Scraping Overview tab …")
            await click_tab(page, "Overview")
            await page.wait_for_timeout(3_000)
            overview = await scrape_overview(page, known_tickers)
            print(f"  Found {len(overview)} tickers in Overview.")

            if len(overview) == 0:
                print()
                print("  ⚠  Still finding 0 tickers — dumping first 30 page lines for diagnosis:")
                body_text = await page.inner_text("body")
                for i, line in enumerate(body_text.splitlines()[:30]):
                    if line.strip():
                        print(f"    {i:02d}: {line.strip()!r}")
                print()
                print("  Run with --debug flag for full DOM row dump.")

            # ── Technical tab ─────────────────────────────────────────────────────
            print("  Switching to Technical tab …")
            found = await click_tab(page, "Technical", "Technicals", "Signals")
            if not found:
                print("  ⚠  Could not auto-click Technical tab — trying anyway.")
            await page.wait_for_timeout(3_000)

            print("  Scraping Technical tab …")
            technical = await scrape_technical(page, known_tickers)
            print(f"  Found {len(technical)} tickers in Technical.")

        if SCRAPE_SIGNAL:
            # ── Smart Signal tab ──────────────────────────────────────────────────
            print("  Switching to Smart Signal tab …")
            found = await click_tab(page, "Smart Signal", "Signal")
            if not found:
                print("  ⚠  Could not auto-click Smart Signal tab — trying anyway.")
            await page.wait_for_timeout(3_000)

            print("  Scraping Smart Signal tab …")
            smart_signal = await scrape_smart_signal(page, known_tickers)
            print(f"  Found {len(smart_signal)} tickers in Smart Signal.")

        await browser.close()

    # ── Fetch Minervini data (MA, RS, distance, volume) ────────────────────────
    print("\n  ── Fetching Minervini data from Polygon ──────────────────")
    minervini_data: Dict[str, Dict] = {}
    for i, ticker in enumerate(sorted(current.keys()), 1):
        print(f"  ({i}/{len(current)}) {ticker} … ", end="", flush=True)
        data = fetch_minervini_data(ticker)
        if data:
            minervini_data[ticker] = data
            keys = ", ".join(data.keys())
            print(f"✓ {keys}")
        else:
            print("⚠ failed")
        time.sleep(1)  # Rate limit between tickers

    # ── Merge → ranks.json ────────────────────────────────────────────────────
    updated: dict = {}
    for ticker in current:
        ov = overview.get(ticker, {})
        tc = technical.get(ticker, {})
        ss = smart_signal.get(ticker, {})
        mv = minervini_data.get(ticker, {})
        updated[ticker] = {
            "rank":       ov.get("rank")    or current[ticker].get("rank",       "Medium"),
            "outlook":    ov.get("outlook") or current[ticker].get("outlook",    "Neutral"),
            "tech":       tc.get("tech")    or current[ticker].get("tech",       "HOLD"),
            "rs_rank":    mv.get("rs_rank") or current[ticker].get("rs_rank"),
            "ma_20":      mv.get("ma_20")   or current[ticker].get("ma_20"),
            "ma_50":      mv.get("ma_50")   or current[ticker].get("ma_50"),
            "ma_200":     mv.get("ma_200")  or current[ticker].get("ma_200"),
            "distance_52w": mv.get("distance_52w") or current[ticker].get("distance_52w"),
            "volume_sma": mv.get("volume_sma")     or current[ticker].get("volume_sma"),
        }
        if ss.get("smart_signal"):
            updated[ticker]["smart_signal"] = ss["smart_signal"]

    with open(RANKS_FILE, "w") as f:
        json.dump(updated, f, indent=2)

    # ── Signal preview ────────────────────────────────────────────────────────
    GREEN  = "\033[32m"
    RED    = "\033[31m"
    YELLOW = "\033[33m"
    RESET  = "\033[0m"
    COLORS = {"BUY": GREEN, "SELL": RED, "HOLD": YELLOW}

    print()
    if SCRAPE_SIGNAL:
        print("  ── Signal preview (with Smart Signal) ───────────────────")
        print(f"  {'Ticker':<7} {'Rank':<8} {'Outlook':<14} {'Tech':<6} {'SmartSignal':<11} Final")
        print(f"  {'─'*7} {'─'*8} {'─'*14} {'─'*6} {'─'*11} {'─'*5}")
        buys = []
        for ticker, v in updated.items():
            sig   = final_signal(v["rank"], v["outlook"], v["tech"])
            smart = v.get("smart_signal", "—")
            color = COLORS.get(sig, RESET)
            print(f"  {ticker:<7} {v['rank']:<8} {v['outlook']:<14} {v['tech']:<6} {smart:<11} {color}{sig}{RESET}")
            if sig == "BUY":
                buys.append(ticker)
    else:
        print("  ── Tonight's signal preview ─────────────────────────────")
        print(f"  {'Ticker':<7} {'Rank':<8} {'Outlook':<14} {'Tech':<6} Final")
        print(f"  {'─'*7} {'─'*8} {'─'*14} {'─'*6} {'─'*5}")
        buys = []
        for ticker, v in updated.items():
            sig   = final_signal(v["rank"], v["outlook"], v["tech"])
            color = COLORS.get(sig, RESET)
            print(f"  {ticker:<7} {v['rank']:<8} {v['outlook']:<14} {v['tech']:<6} {color}{sig}{RESET}")
            if sig == "BUY":
                buys.append(ticker)

    print()
    if buys:
        print(f"  {GREEN}Bot will BUY: {', '.join(buys)}{RESET}")
    else:
        print(f"  {YELLOW}No BUY signals tonight — bot will HOLD/SELL only.{RESET}")

    mode = " (smart signal included)" if SCRAPE_SIGNAL else ""
    print(f"\n  ✓  ranks.json updated{mode} — bot fires at 9:00 AM ET.\n")


if __name__ == "__main__":
    asyncio.run(main())
