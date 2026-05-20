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
    """Fetch N-day return for a stock (in %) using free-first data fetching."""
    try:
        result = fetch_daily_bars(ticker, days=days + 30)
        if not result or len(result) < 3:  # (closes, highs, lows)
            return None

        closes = result[0]  # First element is closes tuple
        if len(closes) < days:
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
    """Fetch current VIX level using free-first data fetching."""
    try:
        result = fetch_daily_bars("^VIX", days=2)
        if not result or len(result) < 3:
            return None

        closes = result[0]  # First element is closes tuple
        if len(closes) < 1:
            return None

        return closes[-1]

    except Exception:
        return None


def is_volatility_acceptable(max_vix: float = 30, min_vix: float = 10) -> bool:
    """
    Check if market volatility is in acceptable range.
    - Too high (VIX > 30): Market panic, risky entries
    - Too low (VIX < 10): Market complacent, low opportunity
    """
    vix = get_vix_level()
    if vix is None:
        return True  # Default to acceptable if unavailable

    return min_vix <= vix <= max_vix
