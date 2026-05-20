"""
intraday_filter.py — Intraday Entry Confirmation
─────────────────────────────────────────────────

Validates that an entry signal is confirmed on intraday timeframes (5-min, 15-min).
This prevents whipsaw entries during consolidation or pullbacks.

Rules:
1. Check if current 15-min bar shows momentum (higher high, higher low)
2. Check if 5-min close is above 5-min 20-period MA (short-term uptrend)
3. Only allow entries during market hours (9:30 AM - 3:50 PM ET)
"""

from typing import Optional, Dict, List, Tuple
from datetime import datetime
import logging
import os
import requests
from dotenv import load_dotenv

load_dotenv()

POLYGON_BASE = "https://api.polygon.io"
POLYGON_KEY = os.getenv("MASSIVE_API_KEY")

log = logging.getLogger(__name__)


def polygon_get(url: str, params: dict) -> Optional[Dict]:
    """GET a Polygon endpoint with retry logic."""
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 429:
                import time
                log.warning(f"Rate limit (attempt {attempt+1}/3) — waiting 60s...")
                time.sleep(60)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            log.warning(f"Polygon request failed (attempt {attempt+1}/3): {e}")
            if attempt == 2:
                return None
    return None


def is_market_hours() -> bool:
    """Check if current time is during US market hours (9:30 AM - 3:50 PM ET)."""
    import pytz
    et = pytz.timezone("America/New_York")
    now = datetime.now(et)

    # Check if weekday (Mon-Fri)
    if now.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False

    # Check time: 9:30 AM - 3:50 PM
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=50, second=0, microsecond=0)

    return market_open <= now <= market_close


def fetch_intraday_bars(
    ticker: str,
    timeframe: str = "15",
    limit: int = 30,
) -> Optional[Tuple[List[float], List[float], List[float]]]:
    """
    Fetch intraday bars (5-min or 15-min) from Polygon.

    Returns: (closes, highs, lows) or None if unavailable
    """
    try:
        url = f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/range/1/{timeframe}minute/2025-01-01/2025-12-31"
        data = polygon_get(
            url,
            {
                "adjusted": "true",
                "limit": limit,
                "sort": "desc",  # Most recent first
                "apiKey": POLYGON_KEY,
            },
        )

        if not data or not data.get("results") or len(data["results"]) < 5:
            return None

        # Reverse to chronological order (oldest to newest)
        results = list(reversed(data["results"][:limit]))

        closes = [float(b["c"]) for b in results]
        highs = [float(b["h"]) for b in results]
        lows = [float(b["l"]) for b in results]

        return (closes, highs, lows)

    except Exception as exc:
        log.error(f"{ticker}: fetch_intraday_bars failed — {exc}")
        return None


def calculate_sma(closes: List[float], period: int = 20) -> Optional[float]:
    """Calculate simple moving average over N bars."""
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period


def validate_intraday_momentum(
    ticker: str,
    current_price: float,
    min_5min_bars: int = 5,
    min_15min_bars: int = 10,
) -> Dict[str, bool]:
    """
    Validate that intraday bars show momentum for entry.

    Returns:
        {
            "market_hours": bool,
            "has_5min_data": bool,
            "has_15min_data": bool,
            "price_above_5min_ma": bool,
            "momentum_confirmed": bool,
        }
    """
    result = {
        "market_hours": False,
        "has_5min_data": False,
        "has_15min_data": False,
        "price_above_5min_ma": False,
        "momentum_confirmed": False,
    }

    # Check market hours
    if not is_market_hours():
        log.warning(f"{ticker}: Outside market hours — skipping intraday check")
        return result
    result["market_hours"] = True

    # Fetch 5-min bars
    bar_data_5min = fetch_intraday_bars(ticker, timeframe="5", limit=min_5min_bars + 5)
    if bar_data_5min is None:
        log.warning(f"{ticker}: No 5-min bars available")
        return result

    closes_5min, highs_5min, lows_5min = bar_data_5min
    result["has_5min_data"] = True

    # Fetch 15-min bars
    bar_data_15min = fetch_intraday_bars(ticker, timeframe="15", limit=min_15min_bars + 5)
    if bar_data_15min is None:
        log.warning(f"{ticker}: No 15-min bars available")
        return result

    closes_15min, highs_15min, lows_15min = bar_data_15min
    result["has_15min_data"] = True

    # Check if current price is above 5-min 20-MA (short-term uptrend)
    ma_5min = calculate_sma(closes_5min, period=5)  # 5 bars at 5-min = 25-min lookback
    if ma_5min and current_price > ma_5min:
        result["price_above_5min_ma"] = True

    # Check if last 2 bars of 15-min show higher highs and higher lows (momentum)
    if len(closes_15min) >= 2:
        # Higher high: current high > previous high
        higher_high = highs_15min[-1] > highs_15min[-2]
        # Higher low: current low > previous low
        higher_low = lows_15min[-1] > lows_15min[-2]

        if higher_high and higher_low:
            result["momentum_confirmed"] = True
            log.info(f"{ticker}: 15-min momentum confirmed (HH={higher_high}, HL={higher_low})")
        else:
            log.warning(f"{ticker}: 15-min momentum weak (HH={higher_high}, HL={higher_low})")

    return result


def should_enter_intraday(
    ticker: str,
    current_price: float,
    skip_intraday_check: bool = False,
) -> Tuple[bool, str]:
    """
    Determine if intraday conditions allow entry.

    Returns: (should_enter, reason)
    """
    if skip_intraday_check:
        return True, "Intraday check skipped (after-hours setup)"

    # Only check during market hours
    if not is_market_hours():
        return False, "Outside market hours (9:30 AM - 3:50 PM ET)"

    intraday = validate_intraday_momentum(ticker, current_price)

    if not intraday["has_5min_data"]:
        return False, "5-min bars unavailable (illiquid or new listing)"

    if not intraday["has_15min_data"]:
        return False, "15-min bars unavailable"

    if not intraday["price_above_5min_ma"]:
        return False, "Price below 5-min MA (downtrend on intraday)"

    if not intraday["momentum_confirmed"]:
        return False, "15-min momentum not confirmed (consolidating)"

    return True, "Intraday conditions favorable"
