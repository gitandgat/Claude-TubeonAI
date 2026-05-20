"""
backtest_kavout.py — Backtest the Kavout + SMA20 Strategy
──────────────────────────────────────────────────────────

Backtests the same signal logic used in bot.py:
  - Kavout Stock Rank (High/Medium/Low)
  - Outlook (Outperform/Neutral/Underperform)
  - Technical signals (BUY/HOLD/SELL)
  - SMA20 crossover

Usage:
    python bot/backtest_kavout.py                    # Backtest 12 months
    python bot/backtest_kavout.py --months 24        # Backtest 24 months
    python bot/backtest_kavout.py --ticker AAPL      # Single stock only
    python bot/backtest_kavout.py --months 12 --print-signals  # Debug: print all signals
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

from trade_tracker import TradeTracker

load_dotenv()

# ── Configuration ────────────────────────────────────────────────────────────
RANKS_FILE = Path(__file__).parent.parent / "ranks.json"
BACKTEST_DB = Path(__file__).parent.parent / "backtest_kavout.db"
POLYGON_BASE = "https://api.polygon.io"
POLYGON_KEY = os.getenv("MASSIVE_API_KEY")

# Position sizing (mimic bot.py)
MAX_POSITION_SIZE = 1_000  # Max dollars per position
ACCOUNT_EQUITY = 100_000   # Starting account balance

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backtest_kavout.log"),
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
    """Fetch daily OHLCV bars from Polygon. Returns list sorted by date."""
    try:
        url = f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
        data = polygon_get(url, {"adjusted": "true", "apiKey": POLYGON_KEY})

        if not data or not data.get("results"):
            log.debug(f"{ticker}: No bars returned for {start_date} to {end_date}")
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


# ── Signal logic (mirrors bot.py) ────────────────────────────────────────────

def determine_signal(
    ticker: str,
    close: float,
    sma20: float,
    ranks: dict,
    print_signal: bool = False
) -> str:
    """
    Three-factor confluence: Kavout Stock Rank + Outlook + Technical + SMA20.

    BUY  — Rank=High AND Outlook=Outperform AND Tech=BUY AND close > SMA20
    SELL — Rank=Low  OR Outlook=Underperform OR Tech=SELL OR close < SMA20
    HOLD — everything else
    """
    entry = ranks.get(ticker, {})
    rank = entry.get("rank", "Medium")
    outlook = entry.get("outlook", "Neutral")
    tech = entry.get("tech", "HOLD")

    vs_sma = ((close - sma20) / sma20) * 100 if sma20 > 0 else 0

    # Evaluate conditions
    buy_conditions = [
        rank == "High",
        outlook == "Outperform",
        tech == "BUY",
        close > sma20
    ]
    sell_conditions = [
        rank == "Low",
        outlook == "Underperform",
        tech == "SELL",
        close < sma20
    ]

    if all(buy_conditions):
        signal = "BUY"
    elif any(sell_conditions):
        signal = "SELL"
    else:
        signal = "HOLD"

    if print_signal:
        log.info(
            f"  {ticker} │ rank={rank} outlook={outlook} tech={tech} │ "
            f"close=${close:.2f} SMA20=${sma20:.2f} ({vs_sma:+.1f}%) │ → {signal}"
        )

    return signal


# ── Backtesting engine ───────────────────────────────────────────────────────

def backtest_ticker(
    ticker: str,
    start_date: str,
    end_date: str,
    tracker: TradeTracker,
    ranks: dict,
    print_signals: bool = False,
) -> Tuple[int, float]:
    """
    Backtest a single ticker from start_date to end_date.
    Returns (num_trades, total_pnl_pct).
    """
    log.info(f"\n┌─ Backtesting {ticker}")

    # Fetch historical bars
    bars = fetch_daily_bars(ticker, start_date, end_date)
    if not bars:
        log.warning(f"└─ {ticker}: No data available")
        return 0, 0.0

    log.info(f"├─ Loaded {len(bars)} daily bars")

    open_trade_id: Optional[int] = None
    entry_price: float = 0.0
    entry_qty: int = 0
    trade_count = 0
    total_pnl = 0.0

    # Simulate day-by-day
    for i, bar in enumerate(bars):
        bar_date = datetime.fromtimestamp(bar["t"] / 1000).strftime("%Y-%m-%d")
        close = float(bar["c"])

        # Calculate SMAs
        closes = [float(b["c"]) for b in bars[: i + 1]]
        sma20 = calculate_sma(closes, 20)

        if sma20 is None:
            continue  # Need at least 20 bars

        # ── ENTRY LOGIC ──────────────────────────────────────────────────
        if not open_trade_id:
            signal = determine_signal(ticker, close, sma20, ranks, print_signals)

            if signal == "BUY":
                # Calculate shares
                qty = max(int(MAX_POSITION_SIZE / close), 1)

                # Open trade
                entry_price = close
                entry_qty = qty
                entry_date = datetime.strptime(bar_date, "%Y-%m-%d")
                open_trade_id = tracker.open_trade(
                    ticker, entry_date, close, qty, 0.0, 0.0  # No explicit stops
                )
                trade_count += 1
                log.debug(
                    f"├─ [{bar_date}] ENTRY: {qty} @ ${close:.2f}"
                )

        # ── EXIT LOGIC ───────────────────────────────────────────────────
        if open_trade_id:
            signal = determine_signal(ticker, close, sma20, ranks, print_signals)

            # Exit if signal turns to SELL or if we've held >180 days
            if signal == "SELL":
                exit_date = datetime.strptime(bar_date, "%Y-%m-%d")
                open_trades = tracker.get_open_trades()
                trade_info = next(
                    (t for t in open_trades if t["trade_id"] == open_trade_id),
                    None
                )

                if trade_info:
                    days_held = (exit_date - trade_info["entry_date"]).days
                    if days_held > 180:
                        exit_reason = "TIME_EXIT"
                    else:
                        exit_reason = "SIGNAL_EXIT"

                    result = tracker.close_trade(
                        open_trade_id, exit_date, close, entry_qty, exit_reason
                    )
                    if result:
                        total_pnl += result["profit_loss_pct"]
                        log.debug(
                            f"├─ [{bar_date}] EXIT ({exit_reason}): "
                            f"${close:.2f} → P&L: {result['profit_loss_pct']:+.2f}%"
                        )
                    open_trade_id = None

    # Close any remaining open trade at end of period
    if open_trade_id:
        final_close = float(bars[-1]["c"])
        final_date = datetime.fromtimestamp(bars[-1]["t"] / 1000)
        open_trades = tracker.get_open_trades()
        trade_info = next(
            (t for t in open_trades if t["trade_id"] == open_trade_id),
            None
        )
        if trade_info:
            result = tracker.close_trade(
                open_trade_id, final_date, final_close, entry_qty, "PERIOD_END"
            )
            if result:
                total_pnl += result["profit_loss_pct"]

    log.info(
        f"└─ {ticker}: {trade_count} trades, total P&L: {total_pnl:+.2f}%"
    )
    return trade_count, total_pnl


def run_full_backtest(months: int = 12, single_ticker: str | None = None, print_signals: bool = False) -> None:
    """Run full backtest on the watchlist."""
    # Load ranks
    if not RANKS_FILE.exists():
        log.error(f"ranks.json not found at {RANKS_FILE}")
        sys.exit(1)

    with open(RANKS_FILE) as f:
        ranks = json.load(f)

    # Determine watchlist
    if single_ticker:
        watchlist = [single_ticker.upper()]
    else:
        watchlist = list(ranks.keys())

    if not watchlist:
        log.warning("No tickers in watchlist")
        return

    # Calculate date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30 * months)).strftime("%Y-%m-%d")

    log.info("=" * 70)
    log.info(f"Backtest: {len(watchlist)} tickers over {months} months")
    log.info(f"Period: {start_date} to {end_date}")
    log.info(f"Strategy: Kavout Stock Rank + Outlook + Tech + SMA20 Crossover")
    log.info(f"Account: ${ACCOUNT_EQUITY:,.0f} │ Per-position: ${MAX_POSITION_SIZE:,.0f}")
    log.info("=" * 70)

    # Initialize backtest database
    tracker = TradeTracker(str(BACKTEST_DB))

    # Backtest each ticker
    total_trades = 0
    total_pnl = 0.0
    ticker_results = {}

    for ticker in sorted(watchlist):
        trades, pnl = backtest_ticker(
            ticker, start_date, end_date, tracker, ranks, print_signals
        )
        total_trades += trades
        total_pnl += pnl
        ticker_results[ticker] = {"trades": trades, "pnl": pnl}

    # Print summary
    log.info("\n" + "=" * 70)
    log.info("BACKTEST SUMMARY")
    log.info("=" * 70)

    for ticker, result in sorted(ticker_results.items()):
        if result["trades"] > 0:
            log.info(
                f"{ticker:<8} │ {result['trades']:>3} trades │ "
                f"P&L: {result['pnl']:>8.2f}%"
            )

    # Overall stats
    log.info("─" * 70)
    summary = tracker.get_pnl_summary(days=30 * months)
    tracker.print_summary(days=30 * months)

    log.info("=" * 70)
    log.info(f"Total trades: {total_trades}")
    log.info(f"Total P&L: {total_pnl:+.2f}%")
    log.info(f"Backtest database saved to: {BACKTEST_DB}")
    log.info("=" * 70)


if __name__ == "__main__":
    months = 12
    single_ticker = None
    print_signals = False

    # Parse command-line args
    if "--months" in sys.argv:
        idx = sys.argv.index("--months")
        months = int(sys.argv[idx + 1])

    if "--ticker" in sys.argv:
        idx = sys.argv.index("--ticker")
        single_ticker = sys.argv[idx + 1]

    if "--print-signals" in sys.argv:
        print_signals = True

    run_full_backtest(months=months, single_ticker=single_ticker, print_signals=print_signals)
