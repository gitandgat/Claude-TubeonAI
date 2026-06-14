"""
Multi-source data fetcher with fallback logic.
Primary: Alpaca (real-time, same broker that executes trades)
Fallbacks: Finnhub → Polygon → Alltick → AlphaVantage → Twelve Data → yfinance

NOTE: patch_yfinance (the synthetic-data mock) must NEVER be imported here —
it silently replaces real prices with fake ones. The bot screened GOOGL at
$164 vs a real $355 for four days in June 2026 because of it.
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


_ALPACA_CLIENT = None


def _alpaca_client():
    """Lazy singleton for Alpaca's historical data client."""
    global _ALPACA_CLIENT
    if _ALPACA_CLIENT is None:
        from alpaca.data.historical import StockHistoricalDataClient
        _ALPACA_CLIENT = StockHistoricalDataClient(
            os.getenv("ALPACA_API_KEY") or os.getenv("APCA_API_KEY_ID"),
            os.getenv("ALPACA_SECRET_KEY") or os.getenv("APCA_API_SECRET_KEY"),
        )
    return _ALPACA_CLIENT


def alpaca_get_bars(ticker: str, days: int = 60) -> Optional[dict]:
    """
    Fetch daily OHLCV bars from Alpaca.
    Returns {"closes": [...], "highs": [...], "lows": [...], "volumes": [...]}
    or None on failure (caller falls through to the next source).
    """
    try:
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame
        bars = _alpaca_client().get_stock_bars(StockBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=days),
        ))
        if ticker not in bars.data or not bars[ticker]:
            return None
        return {
            "closes": [b.close for b in bars[ticker]],
            "highs": [b.high for b in bars[ticker]],
            "lows": [b.low for b in bars[ticker]],
            "volumes": [b.volume for b in bars[ticker]],
        }
    except Exception as e:
        log.debug("%s: Alpaca bars failed — %s", ticker, e)
        return None


def alpaca_get_bars_batch(symbols: list, days: int = 300) -> dict:
    """
    Batch-fetch daily bars for many symbols in one Alpaca request per chunk.
    This is what makes screening 500 stocks feasible — Alpaca returns all
    requested symbols together and the SDK auto-paginates.

    Returns {symbol: {"closes": [...], "highs": [...], "lows": [...],
    "volumes": [...]}} for every symbol that returned data.
    """
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame

    out: dict = {}
    client = _alpaca_client()
    start = datetime.now() - timedelta(days=days)
    CHUNK = 50  # symbols per request — keeps each response well-bounded

    def _fetch(chunk: list) -> None:
        """Fetch a chunk; on failure (e.g. one invalid symbol), split and
        retry so a single bad ticker can't sink its 49 neighbours."""
        if not chunk:
            return
        try:
            bars = client.get_stock_bars(StockBarsRequest(
                symbol_or_symbols=chunk,
                timeframe=TimeFrame.Day,
                start=start,
            ))
        except Exception as e:
            if len(chunk) == 1:
                log.debug("Skipping unfetchable symbol %s: %s", chunk[0], e)
                return
            mid = len(chunk) // 2
            _fetch(chunk[:mid])
            _fetch(chunk[mid:])
            return
        for sym in chunk:
            if sym not in bars.data or not bars[sym]:
                continue
            rows = bars[sym]
            out[sym] = {
                "closes": [b.close for b in rows],
                "highs": [b.high for b in rows],
                "lows": [b.low for b in rows],
                "volumes": [b.volume for b in rows],
            }

    for i in range(0, len(symbols), CHUNK):
        _fetch(symbols[i:i + CHUNK])

    log.info("Alpaca batch: fetched bars for %d/%d symbols", len(out), len(symbols))
    return out


def alpaca_latest_price(ticker: str) -> Optional[float]:
    """Latest trade price from Alpaca, or None on failure."""
    try:
        from alpaca.data.requests import StockLatestTradeRequest
        trades = _alpaca_client().get_stock_latest_trade(
            StockLatestTradeRequest(symbol_or_symbols=ticker)
        )
        return float(trades[ticker].price)
    except Exception as e:
        log.debug("%s: Alpaca latest trade failed — %s", ticker, e)
        return None


def fetch_minervini_metrics(ticker: str) -> Optional[dict]:
    """
    Compute live Minervini metrics from ~300 days of real Alpaca bars:
    MA20/50/200, distance from 52-week high (0-1), volume ratio vs 50-day
    average, and the close series (for RSI). Returns None if data unavailable.
    """
    data = alpaca_get_bars(ticker, days=300)
    if not data or len(data["closes"]) < 60:
        return None
    closes, vols = data["closes"], data["volumes"]
    n = len(closes)
    ma_20 = sum(closes[-20:]) / 20
    ma_50 = sum(closes[-50:]) / 50
    ma_200 = sum(closes[-200:]) / 200 if n >= 200 else sum(closes) / n
    hi_52w = max(closes)
    avg_vol_50 = sum(vols[-50:]) / 50
    return {
        "price": closes[-1],
        "ma_20": ma_20,
        "ma_50": ma_50,
        "ma_200": ma_200,
        "distance_52w": (hi_52w - closes[-1]) / hi_52w if hi_52w > 0 else 0.0,
        "volume_ratio": vols[-1] / avg_vol_50 if avg_vol_50 > 0 else None,
        "closes": closes,
        "bars_used": n,
    }


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
    Fetch latest/previous close price with fallback chain:
    Alpaca → yfinance → Finnhub → Polygon → Alltick → AlphaVantage → Twelve Data
    """
    # Try Alpaca first (real-time, same broker executing the trades)
    price = alpaca_latest_price(ticker)
    if price is not None:
        return price

    # Try yfinance (free, unlimited)
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
    Fetch daily bars with fallback chain.
    Returns: (closes, highs, lows) tuples
    Fallback chain: Alpaca → yfinance → Finnhub → Polygon → Alltick → AlphaVantage → Twelve Data
    """
    # Try Alpaca first (real-time, same broker executing the trades)
    data = alpaca_get_bars(ticker, days=days)
    if data and len(data["closes"]) >= 14:
        return (data["closes"], data["highs"], data["lows"])

    # Try yfinance (free, unlimited)
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
