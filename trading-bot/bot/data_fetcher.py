"""
Multi-source data fetcher with fallback logic.
Primary: Polygon
Fallback 1: Alltick
Fallback 2: AlphaVantage
Fallback 3: Finnhub
Fallback 4: Twelve Data
Fallback 5: yfinance
"""

import os
import logging
import time
import requests
from typing import Optional, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

POLYGON_BASE = "https://api.polygon.io"
ALLTICK_BASE = "https://api.alltick.io"
ALPHAVANTAGE_BASE = "https://www.alphavantage.co"
FINNHUB_BASE = "https://finnhub.io/api/v1"
TWELVEDATA_BASE = "https://api.twelvedata.com"

MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")
ALLTICK_API_KEY = os.getenv("ALLTICK_API_KEY")
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")


def polygon_get(url: str, params: dict) -> dict:
    """GET Polygon endpoint — fails on rate limit to trigger fallback chain."""
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.debug("Polygon request failed: %s", e)
        raise


def alltick_get(endpoint: str, params: dict) -> dict:
    """GET Alltick endpoint."""
    url = f"{ALLTICK_BASE}/{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.debug("Alltick request failed: %s", e)
        raise


def alphavantage_get(params: dict) -> dict:
    """GET AlphaVantage endpoint."""
    url = f"{ALPHAVANTAGE_BASE}/query"
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.debug("AlphaVantage request failed: %s", e)
        raise


def finnhub_get(endpoint: str, params: dict) -> dict:
    """GET Finnhub endpoint."""
    url = f"{FINNHUB_BASE}/{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.debug("Finnhub request failed: %s", e)
        raise


def twelvedata_get(endpoint: str, params: dict) -> dict:
    """GET Twelve Data endpoint."""
    url = f"{TWELVEDATA_BASE}/{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.debug("Twelve Data request failed: %s", e)
        raise


def yfinance_get(ticker: str, days: int = 60, min_bars: int = 1) -> Optional[Tuple]:
    """Fetch daily bars from yfinance."""
    try:
        import yfinance as yf
        period = f"{days}d"
        data = yf.download(ticker, period=period, progress=False)
        if data.empty or len(data) < min_bars:
            return None
        closes = data[("Close", ticker)].tolist()
        highs = data[("High", ticker)].tolist()
        lows = data[("Low", ticker)].tolist()
        return (closes, highs, lows)
    except Exception as e:
        log.debug("yfinance request failed for %s: %s", ticker, e)
        return None


def fetch_previous_close(ticker: str) -> Optional[float]:
    """
    Fetch previous close price with fallback chain (free-first, then paid):
    yfinance → Finnhub → Polygon → Alltick → AlphaVantage → Twelve Data
    """
    # Try yfinance first (free, unlimited)
    try:
        result = yfinance_get(ticker, days=5, min_bars=1)
        if result:
            closes, _, _ = result
            if closes:
                return float(closes[-1])
    except Exception as e:
        log.debug("%s: yfinance failed, trying Finnhub — %s", ticker, e)

    # Try Finnhub (free tier: 60 req/min)
    if FINNHUB_API_KEY:
        try:
            data = finnhub_get("quote", {"symbol": ticker, "token": FINNHUB_API_KEY})
            if data.get("c"):
                return float(data["c"])
        except Exception as e:
            log.debug("%s: Finnhub failed, trying Polygon — %s", ticker, e)

    # Try Polygon (paid, but already subscribed)
    if MASSIVE_API_KEY:
        try:
            url = f"{POLYGON_BASE}/v1/open-close/{ticker}/{datetime.now().strftime('%Y-%m-%d')}"
            data = polygon_get(url, {"adjusted": "true", "apiKey": MASSIVE_API_KEY})
            if data and data.get("close"):
                return float(data["close"])
        except Exception as e:
            log.debug("%s: Polygon failed, trying Alltick — %s", ticker, e)

    # Try Alltick
    if ALLTICK_API_KEY:
        try:
            data = alltick_get("stocks/quote", {"symbol": ticker, "apikey": ALLTICK_API_KEY})
            if data.get("data") and data["data"].get("close"):
                return float(data["data"]["close"])
        except Exception as e:
            log.debug("%s: Alltick failed, trying AlphaVantage — %s", ticker, e)

    # Try AlphaVantage
    if ALPHAVANTAGE_API_KEY:
        try:
            data = alphavantage_get({
                "function": "GLOBAL_QUOTE",
                "symbol": ticker,
                "apikey": ALPHAVANTAGE_API_KEY
            })
            if data.get("Global Quote") and data["Global Quote"].get("05. price"):
                return float(data["Global Quote"]["05. price"])
        except Exception as e:
            log.debug("%s: AlphaVantage failed, trying Twelve Data — %s", ticker, e)

    # Try Twelve Data
    if TWELVEDATA_API_KEY:
        try:
            data = twelvedata_get("quote", {"symbol": ticker, "apikey": TWELVEDATA_API_KEY})
            if data.get("price"):
                return float(data["price"])
        except Exception as e:
            log.debug("%s: Twelve Data failed — %s", ticker, e)

    log.error("%s: Could not fetch previous close from any source", ticker)
    return None


def fetch_daily_bars(ticker: str, days: int = 60) -> Optional[Tuple]:
    """
    Fetch daily bars (OHLCV) with fallback chain (free-first, then paid).
    Returns: (closes, highs, lows) tuples
    Fallback chain: yfinance → Finnhub → Polygon → Alltick → AlphaVantage → Twelve Data
    """
    # Try yfinance first (free, unlimited)
    try:
        result = yfinance_get(ticker, days=days, min_bars=14)
        if result:
            return result
    except Exception as e:
        log.debug("%s: yfinance failed, trying Finnhub — %s", ticker, e)

    # Try Finnhub (free tier: 60 req/min)
    if FINNHUB_API_KEY:
        try:
            data = finnhub_get("stock/candle", {
                "symbol": ticker,
                "resolution": "D",
                "from": int((datetime.now() - timedelta(days=days + 30)).timestamp()),
                "to": int(datetime.now().timestamp()),
                "token": FINNHUB_API_KEY
            })
            if data.get("o") and len(data["o"]) >= 14:
                closes = data["c"]
                highs = data["h"]
                lows = data["l"]
                return (closes, highs, lows)
        except Exception as e:
            log.debug("%s: Finnhub bars failed, trying Polygon — %s", ticker, e)

    # Try Polygon (paid, but already subscribed)
    if MASSIVE_API_KEY:
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days + 30)).strftime("%Y-%m-%d")
            url = f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
            data = polygon_get(url, {"adjusted": "true", "apiKey": MASSIVE_API_KEY})
            if data and data.get("results") and len(data["results"]) >= 14:
                bars = data["results"]
                closes = [float(b["c"]) for b in bars]
                highs = [float(b["h"]) for b in bars]
                lows = [float(b["l"]) for b in bars]
                return (closes, highs, lows)
        except Exception as e:
            log.debug("%s: Polygon bars failed, trying Alltick — %s", ticker, e)

    # Try Alltick
    if ALLTICK_API_KEY:
        try:
            data = alltick_get("stocks/bars", {
                "symbol": ticker,
                "interval": "1day",
                "limit": 100,
                "apikey": ALLTICK_API_KEY
            })
            if data.get("data") and len(data["data"]) >= 14:
                bars = data["data"]
                closes = [float(b["c"]) for b in bars]
                highs = [float(b["h"]) for b in bars]
                lows = [float(b["l"]) for b in bars]
                return (closes, highs, lows)
        except Exception as e:
            log.debug("%s: Alltick bars failed, trying AlphaVantage — %s", ticker, e)

    # Try AlphaVantage
    if ALPHAVANTAGE_API_KEY:
        try:
            data = alphavantage_get({
                "function": "TIME_SERIES_DAILY",
                "symbol": ticker,
                "outputsize": "full",
                "apikey": ALPHAVANTAGE_API_KEY
            })
            time_series = data.get("Time Series (Daily)", {})
            if len(time_series) >= 14:
                dates = sorted(time_series.keys())[-100:]
                closes = [float(time_series[d]["4. close"]) for d in dates]
                highs = [float(time_series[d]["2. high"]) for d in dates]
                lows = [float(time_series[d]["3. low"]) for d in dates]
                return (closes, highs, lows)
        except Exception as e:
            log.debug("%s: AlphaVantage bars failed, trying Twelve Data — %s", ticker, e)

    # Try Twelve Data
    if TWELVEDATA_API_KEY:
        try:
            data = twelvedata_get("time_series", {
                "symbol": ticker,
                "interval": "1day",
                "outputsize": 120,
                "apikey": TWELVEDATA_API_KEY
            })
            if data.get("status") == "ok" and data.get("values"):
                values = data["values"]
                if len(values) >= 14:
                    closes = [float(v["close"]) for v in values]
                    highs = [float(v["high"]) for v in values]
                    lows = [float(v["low"]) for v in values]
                    return (closes, highs, lows)
        except Exception as e:
            log.debug("%s: Twelve Data bars failed — %s", ticker, e)

    log.warning("%s: Could not fetch daily bars from any source", ticker)
    return None
