"""
Bot B — Adaptive Parameter Tuning
──────────────────────────────────
Paper trading on Alpaca.
Adjusts parameters daily based on recent trading performance:
- rs_threshold: 60-85 (default 70)
- atr_multiplier: 1.5-3.0 (default 2.0)
- vix_max: 25-40 (default 30)
- max_risk_pct: 0.5-2.0 (default 1.25)
"""

import patch_yfinance  # Apply yfinance mock to avoid gevent conflicts
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import pytz
import sqlite3

import requests
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, OrderSide, TimeInForce

from adaptation_engine import AdaptationEngine
from data_fetcher import fetch_previous_close, fetch_daily_bars
from trend_filter import validate_trend_template, format_trend_result
from position_manager import (
    calculate_position_size,
    calculate_take_profit_price,
    calculate_atr_stop_loss,
    validate_position_limits,
)
from indicators import calculate_rs_rank, is_market_in_uptrend, is_volatility_acceptable, calculate_atr
from intraday_filter import should_enter_intraday
from sector_rotation import (
    get_sector_strength_scores,
    get_stock_sector,
    calculate_sector_weight_multiplier,
    get_strongest_sectors,
)
from alerts import alert_entry_signal, alert_exit_signal

load_dotenv()

DRY_RUN = "--dry-run" in sys.argv or os.getenv("DRY_RUN", "").lower() == "true"

MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")
if not MASSIVE_API_KEY:
    sys.exit("[FATAL] Missing MASSIVE_API_KEY")

ALPACA_KEY_B = os.getenv("ALPACA_API_KEY_B")
ALPACA_SECRET_B = os.getenv("ALPACA_SECRET_KEY_B")
if not ALPACA_KEY_B or not ALPACA_SECRET_B:
    sys.exit("[FATAL] Missing ALPACA_API_KEY_B or ALPACA_SECRET_KEY_B")

RANKS_FILE = Path(__file__).parent.parent / "ranks.json"
DB_PATH = "bots.db"
ET = pytz.timezone("America/New_York")

trading_client = TradingClient(api_key=ALPACA_KEY_B, secret_key=ALPACA_SECRET_B, paper=True)

# Default parameters (will be overridden by AdaptationEngine)
DEFAULT_PARAMS = {
    "rs_threshold": 70,
    "atr_multiplier": 2.0,
    "vix_max": 30,
    "vix_min": 10,
    "max_risk_pct": 1.25,
    "take_profit_pct": 20.0,
    "max_open_positions": 5,
    "max_position_pct": 20.0,
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot_b.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def load_stock_ranks() -> Dict:
    """Load ranks.json."""
    if not RANKS_FILE.exists():
        sys.exit(f"[FATAL] ranks.json not found. Run scrape_kavout.py first.")
    with open(RANKS_FILE) as f:
        return json.load(f)


def load_bot_params() -> Dict:
    """Load Bot B parameters from database, or use defaults."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT new_params FROM bot_adaptations WHERE bot_variant = 'B' ORDER BY adapted_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
    except Exception as e:
        log.warning("Could not load params from database: %s", e)

    return DEFAULT_PARAMS


def run_bot() -> None:
    """Main Bot B loop with adaptive parameters."""
    sep = "─" * 70
    log.info(sep)
    log.info("Bot B (Adaptive) started │ %s", datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"))
    log.info(sep)

    ranks = load_stock_ranks()

    try:
        account_info = trading_client.get_account()
        equity = float(account_info.equity)
        cash = float(account_info.cash)
    except Exception as e:
        log.error("Failed to fetch Alpaca account info: %s", e)
        sys.exit("[FATAL] Cannot connect to Alpaca")

    engine = AdaptationEngine("B", db_path=DB_PATH)

    # Load current parameters and suggest new ones based on recent performance
    current_params = load_bot_params()
    new_params = engine.suggest_b_params(current_params)

    if current_params != new_params:
        log.info("ADAPTATION: Parameters updated")
        log.info("  rs_threshold: %d → %d", current_params["rs_threshold"], new_params["rs_threshold"])
        log.info("  atr_multiplier: %.1f → %.1f", current_params["atr_multiplier"], new_params["atr_multiplier"])
        log.info("  vix_max: %d → %d", current_params["vix_max"], new_params["vix_max"])
        log.info("  max_risk_pct: %.2f → %.2f", current_params["max_risk_pct"], new_params["max_risk_pct"])
        engine.log_adaptation(current_params, new_params)
        current_params = new_params

    log.info("Using parameters: rs_threshold=%d, atr_multiplier=%.1f, vix_max=%d, max_risk_pct=%.2f",
            current_params["rs_threshold"], current_params["atr_multiplier"],
            current_params["vix_max"], current_params["max_risk_pct"])

    log.info("Alpaca Account │ equity=$%s │ cash=$%s", f"{equity:,.2f}", f"{cash:,.2f}")

    try:
        positions = trading_client.get_all_positions()
        open_tickers = [p.symbol for p in positions]
    except Exception as e:
        log.warning("Could not fetch open positions: %s", e)
        open_tickers = []

    log.info("Open positions: %s", open_tickers or "none")

    # Entry phase
    log.info(sep)
    log.info("ENTRY PHASE: Screening for Minervini Trend Template setups…")

    sector_scores = get_sector_strength_scores()
    strongest = get_strongest_sectors(sector_scores, top_n=3)
    log.info("Strongest sectors: %s", ", ".join(strongest))

    market_uptrend = is_market_in_uptrend()
    volatility_ok = is_volatility_acceptable(
        max_vix=current_params["vix_max"], min_vix=current_params["vix_min"]
    )

    log.info("Market regime: %s", "UPTREND" if market_uptrend else "⚠️  NO UPTREND")
    log.info("Volatility: %s", "OK" if volatility_ok else "⚠️  OUTSIDE RANGE")

    if not market_uptrend or not volatility_ok:
        log.warning("Market conditions unfavorable — skipping entry screening")
    else:
        candidates = [
            t for t, entry in ranks.items()
            if entry.get("rank") == "High" and entry.get("outlook") == "Outperform"
        ]
        log.info("Kavout pre-filter: %d High/Outperform candidates", len(candidates))

        for ticker in candidates:
            log.info("┌── %s", ticker)

            close = fetch_previous_close(ticker)
            bar_data = fetch_daily_bars(ticker, days=60)

            if close is None or bar_data is None:
                log.warning("└── %s │ SKIP — missing market data", ticker)
                continue

            closes, highs, lows = bar_data
            rs_rank = calculate_rs_rank(ticker)

            ma_data = ranks.get(ticker, {})
            ma_20 = ma_data.get("ma_20")
            ma_50 = ma_data.get("ma_50")
            ma_200 = ma_data.get("ma_200")
            distance_52w = ma_data.get("distance_52w") or 0.0
            volume_ratio = ma_data.get("volume_sma") or 1.0

            if not all([ma_20, ma_50, ma_200]):
                log.warning("└── %s │ SKIP — missing MA data", ticker)
                continue

            trend_result = validate_trend_template(
                ticker, close, ma_20, ma_50, ma_200, rs_rank, distance_52w, volume_ratio, closes=closes
            )

            log.info("│   Price=$%.2f │ RS=%d │ Distance=%.1f%% │ Vol=%.2fx",
                    close, rs_rank, distance_52w * 100, volume_ratio)
            log.info("│   %s", format_trend_result(ticker, trend_result))

            if not trend_result["passes"]:
                log.info("└── %s │ SKIP — Trend Template failed", ticker)
                continue

            if ticker in open_tickers:
                log.info("└── %s │ Already holding — SKIP", ticker)
                continue

            atr = calculate_atr(highs, lows, closes, period=14)
            if atr is None:
                log.warning("└── %s │ SKIP — could not calculate ATR", ticker)
                continue

            stop_loss = calculate_atr_stop_loss(
                highs, lows, closes, close, atr_multiplier=current_params["atr_multiplier"]
            )
            take_profit = calculate_take_profit_price(
                close, atr=atr, profit_target_pct=current_params["take_profit_pct"]
            )

            if stop_loss is None:
                log.warning("└── %s │ SKIP — invalid stop loss", ticker)
                continue

            qty = calculate_position_size(
                equity,
                close,
                stop_loss,
                max_risk_pct=current_params["max_risk_pct"],
            )

            sector = get_stock_sector(ticker)
            sector_weight = calculate_sector_weight_multiplier(ticker, sector_scores)
            qty_weighted = int(qty * sector_weight)

            if qty_weighted < 1:
                log.warning("└── %s │ Position size too small (qty=%d)", ticker, qty)
                continue

            qty = qty_weighted
            position_value = close * qty
            is_valid, reason = validate_position_limits(
                equity, position_value, len(open_tickers),
                max_positions=current_params["max_open_positions"],
                max_position_pct=current_params["max_position_pct"],
            )
            if not is_valid:
                log.warning("└── %s │ Position limit: %s", ticker, reason)
                continue

            intraday_ok, intraday_reason = should_enter_intraday(ticker, close)
            if not intraday_ok:
                log.warning("└── %s │ Intraday check failed: %s", ticker, intraday_reason)
                continue

            log.info(
                "└── ENTRY: BUY %d shares @ $%.2f (stop=$%.2f, target=$%.2f, ATR=%.2f)",
                qty, close, stop_loss, take_profit, atr,
            )

            try:
                order = MarketOrderRequest(
                    symbol=ticker,
                    qty=qty,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                )
                trading_client.submit_order(order)
                log.info("└── Order submitted: BUY %d %s @ market", qty, ticker)

                alert_entry_signal(
                    ticker=ticker,
                    entry_price=close,
                    qty=qty,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    rs_rank=rs_rank,
                    sector=sector,
                    notes=f"Bot B (adaptive), ATR=${atr:.2f}",
                )
            except Exception as e:
                log.error("└── %s │ Order failed: %s", ticker, e)

            time.sleep(0.2)  # Spread API load

    log.info(sep)
    log.info("Bot B run completed")


if __name__ == "__main__":
    run_bot()
