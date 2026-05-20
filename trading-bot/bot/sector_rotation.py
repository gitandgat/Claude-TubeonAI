"""
sector_rotation.py — Sector-Based Position Weighting
──────────────────────────────────────────────────────

Implements sector rotation logic to:
1. Identify sector strength (relative to SPY)
2. Weight position sizes by sector momentum
3. Avoid overconcentration in weak sectors
4. Favor entries in strong sectors

Major sectors:
- Technology (XLLY, QQQ exposure)
- Healthcare (XLV)
- Financials (XLF)
- Industrials (XLI)
- Energy (XLE)
- Consumer Staples (XLP)
- Consumer Discretionary (XLY)
- Materials (XLB)
- Utilities (XLU)
- Real Estate (XLRE)
- Communications (XLC)
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging
import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

POLYGON_BASE = "https://api.polygon.io"
POLYGON_KEY = os.getenv("MASSIVE_API_KEY")
CACHE_FILE = Path(__file__).parent / ".sector_cache.json"

log = logging.getLogger(__name__)

# Sector ETF tickers
SECTOR_ETFS = {
    "Technology": "XLK",
    "Healthcare": "XLV",
    "Financials": "XLF",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Consumer Staples": "XLP",
    "Consumer Discretionary": "XLY",
    "Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Communications": "XLC",
}

# Stock to sector mapping (subset - you can expand)
STOCK_SECTORS = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "NVDA": "Technology",
    "TSLA": "Consumer Discretionary",
    "JNJ": "Healthcare",
    "PFE": "Healthcare",
    "JPM": "Financials",
    "BAC": "Financials",
    "XOM": "Energy",
    "CVX": "Energy",
    "DD": "Materials",
    "AMZN": "Consumer Discretionary",
    "GOOGL": "Communications",
    "META": "Communications",
    "IBM": "Technology",
}


def polygon_get(url: str, params: dict) -> Optional[Dict]:
    """GET a Polygon endpoint."""
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.warning(f"Polygon request failed: {e}")
        return None


def fetch_sector_return(sector_etf: str, days: int = 30) -> Optional[float]:
    """
    Calculate N-day return for a sector ETF.
    Returns: percentage change (e.g., 5.2 for +5.2%)
    """
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days+10)).strftime("%Y-%m-%d")

        url = f"{POLYGON_BASE}/v2/aggs/ticker/{sector_etf}/range/1/day/{start_date}/{end_date}"
        data = polygon_get(url, {"adjusted": "true", "apiKey": POLYGON_KEY})

        if not data or not data.get("results") or len(data["results"]) < 2:
            return None

        closes = [float(b["c"]) for b in data["results"]]
        if len(closes) < 2:
            return None

        return ((closes[-1] - closes[0]) / closes[0]) * 100

    except Exception:
        return None


def get_sector_strength_scores() -> Dict[str, float]:
    """
    Calculate relative strength score for each sector (with daily caching).

    Returns: {sector_name: strength_score (0-100)}
    """
    # Check cache validity (same trading day)
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE) as f:
                cached = json.load(f)
            cached_date = cached.get("date")
            today = datetime.now().strftime("%Y-%m-%d")
            if cached_date == today:
                log.debug("Using cached sector scores from today")
                return cached.get("scores", {})
        except Exception as e:
            log.debug(f"Cache read failed, fetching fresh: {e}")

    sector_scores = {}

    for sector_name, etf in SECTOR_ETFS.items():
        try:
            # Get 30-day return for sector
            sector_return = fetch_sector_return(etf, days=30)
            if sector_return is None:
                sector_scores[sector_name] = 50  # Neutral if data unavailable
                continue

            # Get SPY return for baseline
            spy_return = fetch_sector_return("SPY", days=30)
            if spy_return is None:
                spy_return = 0

            # Score: 50 = neutral (equal to SPY), 100 = outperforming, 0 = underperforming
            relative_outperformance = sector_return - spy_return
            score = 50 + (relative_outperformance * 2)  # Scale factor
            score = max(0, min(100, score))  # Clamp to 0-100

            sector_scores[sector_name] = score
            log.debug(f"{sector_name} (ETF: {etf}): return={sector_return:.1f}%, score={score:.0f}")

        except Exception as e:
            log.warning(f"Error calculating score for {sector_name}: {e}")
            sector_scores[sector_name] = 50

    # Cache for the full trading day
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "scores": sector_scores
            }, f)
    except Exception as e:
        log.debug(f"Cache write failed: {e}")

    return sector_scores


def get_stock_sector(ticker: str) -> Optional[str]:
    """
    Get sector for a stock.
    For unknown stocks, return None (can be looked up via Polygon API if needed).
    """
    return STOCK_SECTORS.get(ticker.upper())


def calculate_sector_weight_multiplier(
    ticker: str,
    strength_scores: Dict[str, float],
) -> float:
    """
    Calculate position size multiplier based on sector strength.

    Strong sectors (>60): 1.2x position size
    Normal sectors (40-60): 1.0x position size
    Weak sectors (<40): 0.8x position size

    Returns: multiplier (0.8 - 1.2)
    """
    sector = get_stock_sector(ticker)
    if not sector:
        return 1.0  # Default to neutral if sector unknown

    strength = strength_scores.get(sector, 50)

    if strength > 60:
        return 1.2  # Strong sector
    elif strength < 40:
        return 0.8  # Weak sector
    else:
        return 1.0  # Normal sector


def should_favor_sector(sector_name: str, strength_scores: Dict[str, float]) -> bool:
    """
    Determine if entries in this sector should be favored.

    Returns: True if sector strength is above 60
    """
    strength = strength_scores.get(sector_name, 50)
    return strength > 60


def get_strongest_sectors(
    strength_scores: Dict[str, float],
    top_n: int = 3,
) -> List[str]:
    """
    Get top N strongest sectors by score.
    """
    sorted_sectors = sorted(strength_scores.items(), key=lambda x: x[1], reverse=True)
    return [sector for sector, _ in sorted_sectors[:top_n]]


def get_weakest_sectors(
    strength_scores: Dict[str, float],
    bottom_n: int = 3,
) -> List[str]:
    """
    Get bottom N weakest sectors by score.
    """
    sorted_sectors = sorted(strength_scores.items(), key=lambda x: x[1])
    return [sector for sector, _ in sorted_sectors[:bottom_n]]
