"""
Trading Bot — bot.py
────────────────────
Market data:  Massive.com / Polygon.io REST API
Trade exec:   Alpaca (paper trading by default)
Signals:      Kavout Stock Rank (0-100) + 20-day SMA crossover

Stock Ranks live in ranks.json — run update_ranks.py each morning to refresh.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import pytz

import requests
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from dotenv import load_dotenv

load_dotenv()

# ── Environment variables ────────────────────────────────────────────────────
ALPACA_API_KEY    = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
MASSIVE_API_KEY   = os.getenv("MASSIVE_API_KEY")   # Polygon.io key (Massive.com)
PAPER_TRADING     = os.getenv("PAPER_TRADING", "true").lower() == "true"

_missing = [k for k, v in {
    "ALPACA_API_KEY":    ALPACA_API_KEY,
    "ALPACA_SECRET_KEY": ALPACA_SECRET_KEY,
    "MASSIVE_API_KEY":   MASSIVE_API_KEY,
}.items() if not v]
if _missing:
    sys.exit(f"[FATAL] Missing environment variables: {', '.join(_missing)}")

# ── Trade sizing ─────────────────────────────────────────────────────────────
MAX_POSITION_SIZE = 1_000  # Max dollars to spend per new position

# ── Kavout Stock Rank ─────────────────────────────────────────────────────────
# Loaded fresh from ranks.json on every run — edit that file, not this one.
# To update ranks: python bot/update_ranks.py
RANKS_FILE = Path(__file__).parent.parent / "ranks.json"


def load_stock_ranks() -> dict[str, float]:
    """Read ranks.json at runtime so today's scores are always picked up."""
    if not RANKS_FILE.exists():
        sys.exit(f"[FATAL] ranks.json not found at {RANKS_FILE}. Run update_ranks.py first.")
    with open(RANKS_FILE) as f:
        return json.load(f)

# ── Polygon.io (Massive.com) ─────────────────────────────────────────────────
POLYGON_BASE = "https://api.polygon.io"

ET = pytz.timezone("America/New_York")

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ── Market data helpers ───────────────────────────────────────────────────────

def polygon_get(url: str, params: dict) -> dict:
    """GET a Polygon endpoint, retrying once after 60 s on a 429."""
    for attempt in range(3):
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 429:
            wait = 60
            log.warning("Polygon rate limit hit — waiting %ds (attempt %d/3)", wait, attempt + 1)
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError("Polygon rate limit: max retries exceeded.")


def fetch_previous_close(ticker: str) -> float | None:
    """Return the previous trading day's closing price from Polygon.io."""
    url = f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/prev"
    try:
        data = polygon_get(url, {"adjusted": "true", "apiKey": MASSIVE_API_KEY})
        if not data.get("resultsCount"):
            log.warning("%s: No previous-close data returned by Polygon.", ticker)
            return None
        return float(data["results"][0]["c"])
    except Exception as exc:
        log.error("%s: fetch_previous_close failed — %s", ticker, exc)
        return None


def fetch_sma20(ticker: str) -> float | None:
    """Return the latest 20-day SMA from Polygon.io's indicators endpoint."""
    url = f"{POLYGON_BASE}/v1/indicators/sma/{ticker}"
    try:
        data = polygon_get(url, {
            "timespan":    "day",
            "adjusted":    "true",
            "window":      20,
            "series_type": "close",
            "limit":       1,
            "order":       "desc",
            "apiKey":      MASSIVE_API_KEY,
        })
        values = data.get("results", {}).get("values", [])
        if not values:
            log.warning("%s: No SMA20 data returned by Polygon.", ticker)
            return None
        return float(values[0]["value"])
    except Exception as exc:
        log.error("%s: fetch_sma20 failed — %s", ticker, exc)
        return None


def fetch_real_time_quote(ticker: str) -> tuple[float, str] | None:
    """
    Fetch the last trade price. Tries v3 API first; falls back to previous close on free tier.
    Returns (price, timestamp) or None if unavailable.
    """
    url = f"{POLYGON_BASE}/v3/quotes/last/{ticker}"
    try:
        data = polygon_get(url, {"apiKey": MASSIVE_API_KEY})
        result = data.get("results", {})
        if not result:
            log.debug("%s: v3 quotes/last returned no results, falling back to previous close", ticker)
        else:
            price = result.get("last_price")
            timestamp = result.get("last_quote", {}).get("exchange_timestamp")
            if price is not None:
                return (float(price), timestamp or "rt-quote")
    except Exception as exc:
        if "404" in str(exc) or "NOT_AUTHORIZED" in str(exc):
            log.debug("%s: v3 endpoint unavailable (free tier), falling back to previous close", ticker)
        else:
            log.debug("%s: fetch_real_time_quote attempt failed — %s", ticker, exc)

    price = fetch_previous_close(ticker)
    if price is not None:
        return (price, "previous-close")

    return None


def validate_quote_freshness(ticker: str, quote_timestamp: str, max_age_minutes: int = 5) -> bool:
    """
    Validate that the quote is recent enough (within max_age_minutes).
    Accepts ISO 8601 timestamps, "rt-quote" (real-time), and "previous-close" (end-of-day).
    """
    if quote_timestamp in ("unknown", "rt-quote"):
        return True

    if quote_timestamp == "previous-close":
        log.warning("%s: Using previous close (end-of-day) instead of real-time quote", ticker)
        return True

    try:
        from datetime import datetime, timezone
        quote_time = datetime.fromisoformat(quote_timestamp.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        age_minutes = (now - quote_time).total_seconds() / 60

        if age_minutes > max_age_minutes:
            log.warning(
                "%s: Quote is %.1f minutes old (max: %d) — SKIP trade",
                ticker, age_minutes, max_age_minutes
            )
            return False

        return True
    except Exception as exc:
        log.warning("%s: Could not parse quote timestamp — %s", ticker, exc)
        return True


# ── Signal logic ──────────────────────────────────────────────────────────────

def determine_signal(ticker: str, close: float, sma20: float, ranks: dict) -> str:
    """
    Three-factor confluence: Kavout Stock Rank + Outlook + Technical Signal + SMA20.

    BUY  — Rank=High AND Outlook=Outperform AND Tech=BUY AND close > SMA20
    SELL — Rank=Low  OR Outlook=Underperform OR Tech=SELL OR close < SMA20
    HOLD — everything else
    """
    entry   = ranks.get(ticker, {})
    rank    = entry.get("rank",    "Medium")
    outlook = entry.get("outlook", "Neutral")
    tech    = entry.get("tech",    "HOLD")

    if rank == "High" and outlook == "Outperform" and tech == "BUY" and close > sma20:
        return "BUY"
    if rank == "Low" or outlook == "Underperform" or tech == "SELL" or close < sma20:
        return "SELL"
    return "HOLD"


# BRK-B is listed as "BRK-B" in Kavout but Alpaca uses "BRK/B"
TICKER_ALIASES: dict[str, str] = {"BRK-B": "BRK/B"}


# ── Alpaca helpers ────────────────────────────────────────────────────────────

def get_client() -> TradingClient:
    return TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=PAPER_TRADING)


def get_open_positions(client: TradingClient) -> dict[str, float]:
    """Return {ticker: qty} for all currently held positions."""
    return {p.symbol: float(p.qty) for p in client.get_all_positions()}


def calculate_shares(close: float) -> int:
    """Whole shares that fit within MAX_POSITION_SIZE at the given price."""
    if close <= 0:
        return 0
    return max(int(MAX_POSITION_SIZE / close), 1)


def place_order(
    client: TradingClient,
    ticker: str,
    side: OrderSide,
    qty: int,
) -> None:
    """Submit a DAY market order and log the outcome."""
    order_req = MarketOrderRequest(
        symbol=ticker,
        qty=qty,
        side=side,
        time_in_force=TimeInForce.DAY,
    )
    try:
        order = client.submit_order(order_req)
        log.info(
            "ORDER PLACED │ %s %d %s │ order_id=%s",
            side.value.upper(), qty, ticker, order.id,
        )
    except Exception as exc:
        log.error("ORDER FAILED │ %s %s │ %s", ticker, side.value.upper(), exc)


# ── Main bot loop ─────────────────────────────────────────────────────────────

def run_bot() -> None:
    """Iterate through watchlist from ranks.json, evaluate signals, and execute trades."""
    sep = "─" * 62
    log.info(sep)
    log.info(
        "Bot run started │ %s │ paper=%s",
        datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
        PAPER_TRADING,
    )
    log.info(sep)

    # Load ranks fresh — picks up whatever update_ranks.py wrote this morning
    ranks    = load_stock_ranks()
    watchlist = list(ranks.keys())
    log.info("Watchlist (%d tickers): %s", len(watchlist), watchlist)

    client  = get_client()
    account = client.get_account()
    log.info(
        "Account │ equity=$%s │ buying_power=$%s",
        f"{float(account.equity):,.2f}",
        f"{float(account.buying_power):,.2f}",
    )

    positions = get_open_positions(client)
    log.info("Open positions: %s", list(positions.keys()) or "none")
    log.info(sep)

    for ticker in watchlist:
        log.info("┌── %s", ticker)

        close = fetch_previous_close(ticker)
        sma20 = fetch_sma20(ticker)

        if close is None or sma20 is None:
            log.warning("└── %s │ SKIP — missing market data", ticker)
            continue

        entry   = ranks.get(ticker, {})
        rank    = entry.get("rank",    "Medium")
        outlook = entry.get("outlook", "Neutral")
        tech    = entry.get("tech",    "HOLD")
        vs_sma  = ((close - sma20) / sma20) * 100
        signal  = determine_signal(ticker, close, sma20, ranks)

        # Use Alpaca-compatible ticker symbol (e.g. BRK/B instead of BRK-B)
        alpaca_ticker = TICKER_ALIASES.get(ticker, ticker)
        held     = alpaca_ticker in positions
        qty_held = positions.get(alpaca_ticker, 0)

        log.info(
            "│   close=$%.2f │ SMA20=$%.2f (%+.1f%%) │ rank=%s │ outlook=%s │ tech=%s │ signal=%s",
            close, sma20, vs_sma, rank, outlook, tech, signal,
        )

        if signal == "BUY" and not held:
            # Validate real-time quote before placing BUY order
            quote_data = fetch_real_time_quote(ticker)
            if quote_data:
                real_price, quote_ts = quote_data
                if validate_quote_freshness(ticker, quote_ts):
                    qty = calculate_shares(real_price)
                    log.info("└── ENTERING: BUY %d shares @ $%.2f (RT quote)", qty, real_price)
                    place_order(client, alpaca_ticker, OrderSide.BUY, qty)
                else:
                    log.warning("└── BUY signal but quote too stale — SKIP")
            else:
                log.warning("└── BUY signal but no real-time quote — SKIP")

        elif signal == "SELL" and held:
            # Validate real-time quote before placing SELL order
            quote_data = fetch_real_time_quote(ticker)
            if quote_data:
                real_price, quote_ts = quote_data
                if validate_quote_freshness(ticker, quote_ts):
                    qty = int(qty_held)
                    log.info("└── EXITING:  SELL %d shares @ $%.2f (RT quote)", qty, real_price)
                    place_order(client, alpaca_ticker, OrderSide.SELL, qty)
                else:
                    log.warning("└── SELL signal but quote too stale — SKIP")
            else:
                log.warning("└── SELL signal but no real-time quote — SKIP")

        elif signal == "BUY" and held:
            log.info("└── Already holding %.0f shares — HOLD.", qty_held)

        else:
            log.info("└── No action (%s).", signal)

        # Brief pause to stay friendly with Polygon's free-tier rate limit.
        time.sleep(13)

    log.info(sep)
    log.info("Bot run complete.")
    log.info(sep)


if __name__ == "__main__":
    run_bot()
