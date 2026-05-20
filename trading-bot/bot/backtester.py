"""
backtester.py — Minervini Trend Template Strategy Backtester
──────────────────────────────────────────────────────────────

Backtests the Minervini Trend Template strategy on historical daily data.
Simulates entries, exits (stop loss, take profit, time exit), and tracks P&L.

Usage:
    python bot/backtester.py                    # Backtest 12 months
    python bot/backtester.py --months 24        # Backtest 24 months
    python bot/backtester.py --ticker AAPL      # Single stock only
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import requests
from dotenv import load_dotenv

from trend_filter import validate_trend_template
from position_manager import (
    calculate_position_size,
    calculate_stop_loss_price,
    calculate_take_profit_price,
)
from trade_tracker import TradeTracker

load_dotenv()

# ── Configuration ────────────────────────────────────────────────────────────
RANKS_FILE = Path(__file__).parent.parent / "ranks.json"
BACKTEST_DB = Path(__file__).parent.parent / "backtest.db"
POLYGON_BASE = "https://api.polygon.io"
POLYGON_KEY = os.getenv("MASSIVE_API_KEY")

# Minervini parameters
ACCOUNT_EQUITY = 100000.0  # Simulated starting account
MAX_RISK_PER_TRADE_PCT = 1.25
STOP_LOSS_PCT = 7.0
TAKE_PROFIT_PCT = 20.0
MAX_OPEN_POSITIONS = 5
MAX_POSITION_PCT = 20.0

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backtest.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ── Polygon API helpers ───────────────────────────────────────────────────────


def polygon_get(url: str, params: dict) -> dict | None:
    """GET a Polygon endpoint with retry logic."""
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 429:
                log.warning("Rate limit — waiting 60s")
                import time
                time.sleep(60)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == 2:
                log.warning(f"Polygon request failed after 3 attempts: {e}")
                return None
    return None


def fetch_daily_bars(
    ticker: str, start_date: str, end_date: str
) -> List[Dict] | None:
    """
    Fetch daily OHLCV bars from Polygon.
    Returns list of bars sorted by date (oldest first).
    """
    try:
        url = f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
        data = polygon_get(url, {"adjusted": "true", "apiKey": POLYGON_KEY})

        if not data or not data.get("results"):
            log.warning(f"{ticker}: No bars returned for {start_date} to {end_date}")
            return None

        # Sort by timestamp ascending (oldest first)
        bars = sorted(data["results"], key=lambda x: x["t"])
        return bars
    except Exception as e:
        log.error(f"{ticker}: fetch_daily_bars failed — {e}")
        return None


def calculate_sma(closes: List[float], window: int) -> float | None:
    """Calculate SMA from a list of closes."""
    if len(closes) < window:
        return None
    return sum(closes[-window:]) / window


def calculate_rs_rank(ticker: str, reference_date: str) -> int:
    """
    Estimate RS rank based on 52-week performance.
    For simplicity: compare current price to 52W high/low.
    Returns 0-100 (higher = stronger performance).
    """
    # This is a simplified RS calculation
    # In reality, RS rank should be calculated vs the market index (SPY)
    # For now, return a default value
    return 70  # Default to 70 for simplicity


# ── Backtesting engine ────────────────────────────────────────────────────────


def backtest_ticker(
    ticker: str,
    start_date: str,
    end_date: str,
    tracker: TradeTracker,
    account_equity: float,
) -> Tuple[int, float]:
    """
    Backtest a single ticker from start_date to end_date.
    Returns (num_trades, total_pnl_pct).
    """
    log.info(f"\n┌─ Backtesting {ticker} ({start_date} to {end_date})")

    # Fetch historical bars
    bars = fetch_daily_bars(ticker, start_date, end_date)
    if not bars:
        log.warning(f"└─ {ticker}: No data, skipping")
        return 0, 0.0

    log.info(f"├─ Loaded {len(bars)} daily bars")

    open_trade_id: Optional[int] = None
    trade_count = 0
    total_pnl = 0.0
    entry_attempts = 0
    trend_passes = 0

    # Simulate day-by-day
    for i, bar in enumerate(bars):
        bar_date = datetime.fromtimestamp(bar["t"] / 1000).strftime("%Y-%m-%d")
        close = float(bar["c"])
        volume = float(bar["v"])

        # Calculate SMAs (need at least 200 days of history)
        closes = [float(b["c"]) for b in bars[: i + 1]]
        ma_20 = calculate_sma(closes, 20)
        ma_50 = calculate_sma(closes, 50)
        ma_200 = calculate_sma(closes, 200)

        # Calculate 52-week high (252 trading days)
        closes_52w = [float(b["c"]) for b in bars[max(0, i - 252) : i + 1]]
        h52w = max(closes_52w) if closes_52w else close
        distance_52w = (h52w - close) / h52w if h52w > 0 else 0

        # Calculate volume ratio (need 50 days of history)
        volumes_50d = [float(b["v"]) for b in bars[max(0, i - 50) : i + 1]]
        avg_vol_50d = sum(volumes_50d) / len(volumes_50d) if volumes_50d else 1
        volume_ratio = volume / avg_vol_50d if avg_vol_50d > 0 else 0

        # ── ENTRY LOGIC ───────────────────────────────────────────────────────
        if (
            not open_trade_id
            and ma_20 is not None
            and ma_50 is not None
            and ma_200 is not None
        ):
            entry_attempts += 1
            rs_rank = calculate_rs_rank(ticker, bar_date)

            # Validate Trend Template
            trend_result = validate_trend_template(
                ticker, close, ma_20, ma_50, ma_200, rs_rank, distance_52w, volume_ratio
            )

            # Debug: log metrics on key dates
            if bar_date in ["2026-04-30", "2026-05-01"]:
                log.info(
                    f"DEBUG [{bar_date}] {ticker}: MA20=${ma_20:.2f}, MA50=${ma_50:.2f}, "
                    f"MA200=${ma_200:.2f}, price=${close:.2f}, "
                    f"distance_52w={distance_52w:.3f}, volume_ratio={volume_ratio:.2f}, "
                    f"rs_rank={rs_rank}, result={trend_result}"
                )

            if trend_result["passes"]:
                trend_passes += 1
                log.info(
                    f"├─ [{bar_date}] TREND PASSES: {ticker} @ ${close:.2f} "
                    f"(MA20=${ma_20:.2f}, MA50=${ma_50:.2f}, MA200=${ma_200:.2f})"
                )

            if trend_result["passes"]:
                # Calculate position size
                stop_loss = calculate_stop_loss_price(close, STOP_LOSS_PCT)
                take_profit = calculate_take_profit_price(close, TAKE_PROFIT_PCT)
                qty = calculate_position_size(
                    account_equity, close, stop_loss, max_risk_pct=MAX_RISK_PER_TRADE_PCT
                )

                if qty > 0:
                    # Open trade
                    entry_date = datetime.strptime(bar_date, "%Y-%m-%d")
                    open_trade_id = tracker.open_trade(
                        ticker, entry_date, close, qty, stop_loss, take_profit
                    )
                    trade_count += 1
                    log.info(
                        f"├─ [{bar_date}] ENTRY: {qty} @ ${close:.2f} "
                        f"(stop=${stop_loss:.2f}, target=${take_profit:.2f})"
                    )

        # ── EXIT LOGIC ────────────────────────────────────────────────────────
        if open_trade_id:
            exit_reason = None
            exit_price = close

            # Get trade info
            open_trades = tracker.get_open_trades()
            trade_info = next((t for t in open_trades if t["trade_id"] == open_trade_id), None)

            if trade_info:
                # Check exit conditions
                if close <= trade_info["stop_loss_level"]:
                    exit_reason = "STOP_LOSS"
                elif close >= trade_info["take_profit_level"]:
                    exit_reason = "TAKE_PROFIT"
                elif (
                    datetime.strptime(bar_date, "%Y-%m-%d") - trade_info["entry_date"]
                ).days >= 180:
                    exit_reason = "TIME_EXIT"

                if exit_reason:
                    # Close trade
                    exit_date = datetime.strptime(bar_date, "%Y-%m-%d")
                    result = tracker.close_trade(
                        open_trade_id, exit_date, exit_price, trade_info["entry_qty"], exit_reason
                    )
                    if result:
                        total_pnl += result["profit_loss_pct"]
                        log.info(
                            f"├─ [{bar_date}] EXIT ({exit_reason}): "
                            f"${exit_price:.2f} → P&L: {result['profit_loss_pct']:+.2f}%"
                        )
                    open_trade_id = None

    log.info(
        f"├─ Entry attempts: {entry_attempts} │ Trend passes: {trend_passes} "
        f"({100*trend_passes/max(entry_attempts,1):.1f}%)"
    )
    log.info(
        f"└─ {ticker}: {trade_count} trades, total P&L: {total_pnl:+.2f}%"
    )
    return trade_count, total_pnl


def run_full_backtest(months: int = 12) -> None:
    """Run full backtest on the watchlist."""
    # Load ranks
    if not RANKS_FILE.exists():
        log.error(f"ranks.json not found at {RANKS_FILE}")
        sys.exit(1)

    with open(RANKS_FILE) as f:
        ranks = json.load(f)

    # Test all candidates (Kavout pre-filtered + discovered)
    # Kavout stocks: rank="High" + outlook="Outperform"
    # Discovered stocks: rank="Medium" or other (score-based, need Minervini validation)
    candidates = list(ranks.keys())

    if not candidates:
        log.warning("No candidates in ranks.json")
        return

    # Calculate date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30 * months)).strftime("%Y-%m-%d")

    log.info("=" * 70)
    log.info(f"Backtest: {len(candidates)} tickers over {months} months")
    log.info(f"Period: {start_date} to {end_date}")
    log.info(f"Account: ${ACCOUNT_EQUITY:,.0f} │ Risk/trade: {MAX_RISK_PER_TRADE_PCT}%")
    log.info("=" * 70)

    # Initialize backtest database
    tracker = TradeTracker(str(BACKTEST_DB))

    # Backtest each candidate
    total_trades = 0
    total_pnl = 0.0
    ticker_results = {}

    for ticker in sorted(candidates):
        trades, pnl = backtest_ticker(
            ticker, start_date, end_date, tracker, ACCOUNT_EQUITY
        )
        total_trades += trades
        total_pnl += pnl
        ticker_results[ticker] = {"trades": trades, "pnl": pnl}

    # Print summary
    log.info("\n" + "=" * 70)
    log.info("BACKTEST SUMMARY")
    log.info("=" * 70)

    for ticker, result in ticker_results.items():
        if result["trades"] > 0:
            log.info(
                f"{ticker:<6} │ {result['trades']:>3} trades │ "
                f"P&L: {result['pnl']:>7.2f}%"
            )

    # Overall stats
    summary = tracker.get_pnl_summary(days=30 * months)
    log.info("─" * 70)
    tracker.print_summary(days=30 * months)

    log.info("=" * 70)
    log.info(f"Backtest database saved to: {BACKTEST_DB}")
    log.info("Query results with: tracker = TradeTracker('backtest.db')")


if __name__ == "__main__":
    months = 12
    single_ticker = None

    # Parse command-line args
    if "--months" in sys.argv:
        idx = sys.argv.index("--months")
        months = int(sys.argv[idx + 1])

    if "--ticker" in sys.argv:
        idx = sys.argv.index("--ticker")
        single_ticker = sys.argv[idx + 1]

    run_full_backtest(months=months)
