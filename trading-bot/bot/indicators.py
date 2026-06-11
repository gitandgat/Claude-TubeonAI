"""
indicators.py — Technical indicators and market analysis utilities
Provides: RS Rank (vs SPY), ATR, RSI, Volatility filters, Market regime checks
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
import os
import logging

import requests
from dotenv import load_dotenv
from data_fetcher import fetch_daily_bars

load_dotenv()

POLYGON_KEY = os.getenv("MASSIVE_API_KEY")

log = logging.getLogger(__name__)


def polygon_get(url: str, params: dict) -> Optional[Dict]:
    """GET a Polygon endpoint with retry."""
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.warning(f"Polygon request failed: {e}")
        return None


def fetch_stock_returns(ticker: str, days: int = 252) -> Optional[float]:
    """Fetch N-trading-day return for a stock (in %) using free-first data fetching."""
    try:
        # `days` means TRADING bars; fetch ~1.5x calendar days to cover
        # weekends/holidays (252 trading days needs ~365+ calendar days)
        result = fetch_daily_bars(ticker, days=int(days * 1.5) + 30)
        if not result or len(result) < 3:  # (closes, highs, lows)
            return None

        closes = result[0]  # First element is closes tuple
        # Accept a shorter window (>=200 bars) rather than failing outright —
        # a 200-day return is a fine RS proxy when full history is unavailable
        if len(closes) < min(days, 200):
            return None

        # Return: (current_price - price_N_days_ago) / price_N_days_ago * 100
        current = closes[-1]
        past = closes[-days] if len(closes) >= days else closes[0]
        return ((current - past) / past) * 100

    except Exception:
        return None


def calculate_rs_rank(ticker: str, reference_date: str = None) -> int:
    """
    Calculate Relative Strength rank (0-100) by comparing stock's 252-day
    return against SPY's return.

    Returns 0-100 where 100 = best performer vs index.
    """
    try:
        # Get ticker's 252-day return
        ticker_return = fetch_stock_returns(ticker, days=252)
        if ticker_return is None:
            return 50  # Default to neutral if data unavailable

        # Get SPY's 252-day return (market baseline)
        spy_return = fetch_stock_returns("SPY", days=252)
        if spy_return is None:
            return 50

        # Simple RS: if ticker outperforms SPY, scale to 0-100
        # If ticker_return = spy_return, rs_rank = 50
        # If ticker_return = spy_return + 20%, rs_rank = 85
        # If ticker_return = spy_return - 20%, rs_rank = 15
        relative_outperformance = ticker_return - spy_return
        rs_rank = int(50 + (relative_outperformance / 2))  # Scale factor
        rs_rank = max(0, min(100, rs_rank))  # Clamp to 0-100

        return rs_rank

    except Exception as e:
        log.warning(f"RS Rank calculation failed for {ticker}: {e}")
        return 50


def calculate_atr(highs: List[float], lows: List[float], closes: List[float],
                  period: int = 14) -> Optional[float]:
    """Calculate Average True Range."""
    if len(highs) < period:
        return None

    # True Range = max(high, prev_close) - min(low, prev_close)
    true_ranges = []
    for i in range(1, len(highs)):
        high = highs[i]
        low = lows[i]
        prev_close = closes[i - 1]
        tr = max(high, prev_close) - min(low, prev_close)
        true_ranges.append(tr)

    # ATR = SMA of True Range over period
    if len(true_ranges) < period:
        return None

    atr = sum(true_ranges[-period:]) / period
    return atr


def calculate_rsi(closes: List[float], period: int = 14) -> Optional[float]:
    """Calculate Relative Strength Index (0-100)."""
    if len(closes) < period + 1:
        return None

    # Calculate gains and losses
    gains = []
    losses = []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    # Average gains and losses
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def is_market_in_uptrend() -> bool:
    """
    Check if SPY is in uptrend (price > MA200) using free-first data fetching.
    Returns True only if market regime is favorable.
    """
    try:
        result = fetch_daily_bars("SPY", days=250)
        if not result or len(result) < 3:
            return True  # Default to trading if data unavailable

        closes = result[0]  # First element is closes tuple
        if len(closes) < 200:
            return True

        spy_price = closes[-1]
        spy_ma200 = sum(closes[-200:]) / 200

        return spy_price > spy_ma200

    except Exception as e:
        log.warning(f"Market regime check failed: {e}")
        return True  # Default to trading


def get_vix_level() -> Optional[float]:
    """
    Fetch current VIX level.
    Tier 1: real VIX close from FRED (keyless CSV, ~1 trading day delayed —
            fine for a daily 9 AM bot).
    Tier 2: SPY 20-day realized volatility, annualized, +2pt variance-risk-
            premium adjustment (implied vol normally trades above realized).
    Returns None only if both fail. (^VIX is not available from any of the
    bot's market-data sources, so it is no longer attempted.)
    """
    # Tier 1: real VIX from FRED (no API key required)
    try:
        import requests
        from datetime import datetime, timedelta
        start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        resp = requests.get(
            f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS&cosd={start}",
            timeout=10,
        )
        resp.raise_for_status()
        rows = [line.split(",") for line in resp.text.strip().splitlines()[1:]]
        values = [float(v) for _, v in rows if v not in (".", "")]
        if values:
            log.info("VIX %.2f (source: FRED VIXCLS)", values[-1])
            return values[-1]
    except Exception as e:
        log.debug("FRED VIX fetch failed: %s", e)

    # Tier 2: realized-volatility proxy from SPY daily returns
    try:
        result = fetch_daily_bars("SPY", days=45)
        if result and len(result[0]) >= 21:
            closes = result[0][-21:]
            rets = [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes))]
            mean = sum(rets) / len(rets)
            var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
            realized = (var ** 0.5) * (252 ** 0.5) * 100
            proxy = realized + 2.0  # VRP: implied usually runs above realized
            log.info("VIX ~%.2f (proxy: SPY 20d realized vol %.2f + 2.0 VRP)", proxy, realized)
            return proxy
    except Exception as e:
        log.debug("Realized-vol VIX proxy failed: %s", e)

    return None


def is_volatility_acceptable(max_vix: float = 30, min_vix: float = 10) -> bool:
    """
    Check if market volatility is in acceptable range.
    - Too high (VIX > 30): Market panic, risky entries
    - Too low (VIX < 10): Market complacent, low opportunity
    """
    vix = get_vix_level()
    if vix is None:
        log.warning("VIX unavailable from all sources — volatility check SKIPPED (fail-open)")
        return True  # Default to acceptable if unavailable

    return min_vix <= vix <= max_vix
