"""
universe.py — Tradable stock universe with GICS sector classification.
─────────────────────────────────────────────────────────────────────

Replaces the 14-stock Kavout watchlist with the full S&P 500. Minervini's
edge comes from screening a BROAD universe daily — leadership rotates across
sectors, so a handful of correlated mega-caps hides most opportunities.

Primary source: datasets/s-and-p-500-companies (keyless, maintained CSV).
Cached weekly to universe_cache.json. Falls back to a diversified hardcoded
list (all 11 GICS sectors) if the fetch fails, so the bot always has breadth.
"""

import csv
import io
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional

import requests

log = logging.getLogger(__name__)

CACHE_FILE = Path(__file__).parent / "universe_cache.json"
CACHE_TTL_SECONDS = 7 * 24 * 3600  # refresh weekly
SP500_CSV_URL = (
    "https://raw.githubusercontent.com/datasets/"
    "s-and-p-500-companies/main/data/constituents.csv"
)

# Diversified fallback spanning all 11 GICS sectors (used only if the CSV
# fetch fails AND no cache exists). Not the full index — just enough liquid
# breadth that the screener still sees rotation across sectors.
FALLBACK_UNIVERSE: Dict[str, str] = {
    # Information Technology
    "AAPL": "Information Technology", "MSFT": "Information Technology",
    "NVDA": "Information Technology", "AVGO": "Information Technology",
    "ORCL": "Information Technology", "CRM": "Information Technology",
    "AMD": "Information Technology", "ADBE": "Information Technology",
    "CSCO": "Information Technology", "ACN": "Information Technology",
    "PLTR": "Information Technology", "NOW": "Information Technology",
    # Communication Services
    "GOOGL": "Communication Services", "META": "Communication Services",
    "NFLX": "Communication Services", "DIS": "Communication Services",
    "T": "Communication Services", "VZ": "Communication Services",
    "TMUS": "Communication Services",
    # Consumer Discretionary
    "AMZN": "Consumer Discretionary", "TSLA": "Consumer Discretionary",
    "HD": "Consumer Discretionary", "MCD": "Consumer Discretionary",
    "NKE": "Consumer Discretionary", "LOW": "Consumer Discretionary",
    "BKNG": "Consumer Discretionary", "ULTA": "Consumer Discretionary",
    # Consumer Staples
    "WMT": "Consumer Staples", "PG": "Consumer Staples",
    "COST": "Consumer Staples", "KO": "Consumer Staples",
    "PEP": "Consumer Staples", "MDLZ": "Consumer Staples",
    # Health Care
    "UNH": "Health Care", "JNJ": "Health Care", "LLY": "Health Care",
    "ABBV": "Health Care", "MRK": "Health Care", "TMO": "Health Care",
    "ELV": "Health Care", "ISRG": "Health Care", "VRTX": "Health Care",
    # Financials
    "BRK-B": "Financials", "JPM": "Financials", "V": "Financials",
    "MA": "Financials", "BAC": "Financials", "WFC": "Financials",
    "GS": "Financials", "MS": "Financials", "AXP": "Financials",
    # Industrials
    "CAT": "Industrials", "GE": "Industrials", "RTX": "Industrials",
    "HON": "Industrials", "UNP": "Industrials", "BA": "Industrials",
    "DE": "Industrials", "LMT": "Industrials",
    # Energy
    "XOM": "Energy", "CVX": "Energy", "COP": "Energy",
    "SLB": "Energy", "EOG": "Energy", "MPC": "Energy",
    # Utilities
    "NEE": "Utilities", "DUK": "Utilities", "SO": "Utilities",
    "CEG": "Utilities",
    # Real Estate
    "PLD": "Real Estate", "AMT": "Real Estate", "EQIX": "Real Estate",
    # Materials
    "LIN": "Materials", "SHW": "Materials", "FCX": "Materials",
    "NEM": "Materials",
}


def _load_cache() -> Optional[Dict[str, str]]:
    if not CACHE_FILE.exists():
        return None
    try:
        cached = json.loads(CACHE_FILE.read_text())
        if time.time() - cached.get("fetched_at", 0) > CACHE_TTL_SECONDS:
            return None  # stale
        constituents = cached.get("constituents", {})
        return constituents or None
    except (json.JSONDecodeError, OSError) as e:
        log.debug("Universe cache read failed: %s", e)
        return None


def _save_cache(constituents: Dict[str, str]) -> None:
    try:
        CACHE_FILE.write_text(json.dumps(
            {"fetched_at": time.time(), "constituents": constituents}, indent=2
        ))
    except OSError as e:
        log.warning("Could not write universe cache: %s", e)


def _fetch_sp500_csv() -> Dict[str, str]:
    """Fetch S&P 500 constituents + GICS sectors from the maintained CSV."""
    resp = requests.get(SP500_CSV_URL, timeout=15)
    resp.raise_for_status()
    # Proper CSV parsing — some company names contain quoted commas
    reader = csv.DictReader(io.StringIO(resp.text))
    constituents: Dict[str, str] = {}
    for row in reader:
        # Alpaca uses dashes for class shares (BRK-B), CSV uses dots (BRK.B)
        symbol = (row.get("Symbol") or "").strip().replace(".", "-")
        sector = (row.get("GICS Sector") or "").strip()
        if symbol:
            constituents[symbol] = sector or "Unknown"
    return constituents


def get_universe(force_refresh: bool = False) -> Dict[str, str]:
    """
    Return {ticker: gics_sector} for the screening universe.
    Cache (weekly) → live CSV → diversified hardcoded fallback.
    """
    if not force_refresh:
        cached = _load_cache()
        if cached:
            log.info("Universe: %d stocks (cached)", len(cached))
            return cached

    try:
        constituents = _fetch_sp500_csv()
        if len(constituents) >= 400:  # sanity: real S&P 500 is ~503
            _save_cache(constituents)
            log.info("Universe: %d stocks (S&P 500, live)", len(constituents))
            return constituents
        log.warning("S&P 500 CSV returned only %d rows — using fallback", len(constituents))
    except Exception as e:
        log.warning("S&P 500 CSV fetch failed (%s) — using fallback", e)

    # Last resort: stale cache if we have one, else hardcoded
    stale = _load_cache_ignore_ttl()
    if stale:
        log.info("Universe: %d stocks (stale cache fallback)", len(stale))
        return stale
    log.info("Universe: %d stocks (hardcoded fallback)", len(FALLBACK_UNIVERSE))
    return dict(FALLBACK_UNIVERSE)


def _load_cache_ignore_ttl() -> Optional[Dict[str, str]]:
    if not CACHE_FILE.exists():
        return None
    try:
        return json.loads(CACHE_FILE.read_text()).get("constituents") or None
    except (json.JSONDecodeError, OSError):
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    u = get_universe(force_refresh=True)
    from collections import Counter
    by_sector = Counter(u.values())
    print(f"\nTotal: {len(u)} stocks across {len(by_sector)} sectors")
    for sector, n in by_sector.most_common():
        print(f"  {sector:28} {n}")
