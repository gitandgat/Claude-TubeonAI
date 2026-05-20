"""
Bot C — Hybrid (Fixed Minervini + Adaptive Position Sizing)
───────────────────────────────────────────────────────────
Paper trading on Alpaca.
Minervini entry/exit rules are FIXED, only position sizing adapts:
- max_risk_pct: 0.5-2.0 (adjusts based on drawdown)
- All other parameters fixed (RS_THRESHOLD=70, ATR_MULTIPLIER=2.0, VIX_MAX=30)
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

ALPACA_KEY_C = os.getenv("ALPACA_API_KEY_C")
ALPACA_SECRET_C = os.getenv("ALPACA_SECRET_KEY_C")
if not ALPACA_KEY_C or not ALPACA_SECRET_C:
    sys.exit("[FATAL] Missing ALPACA_API_KEY_C or ALPACA_SECRET_KEY_C")

RANKS_FILE = Path(__file__).parent.parent / "ranks.json"
DB_PATH = "bots.db"
ET = pytz.timezone("America/New_York")

trading_client = TradingClient(api_key=ALPACA_KEY_C, secret_key=ALPACA_SECRET_C, paper=True)

# Fixed parameters (never change for Bot C)
RS_THRESHOLD = 70
ATR_MULTIPLIER = 2.0
VIX_MAX = 30
VIX_MIN = 10
TAKE_PROFIT_PCT = 20.0
MAX_OPEN_POSITIONS = 5
MAX_POSITION_PCT = 20.0

# Adaptive only
DEFAULT_MAX_RISK_PCT = 1.25

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot_c.log"),
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


def load_bot_max_risk_pct() -> float:
    """Load Bot C max_risk_pct from database, or use default."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT new_params FROM bot_adaptations WHERE bot_variant = 'C' ORDER BY adapted_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            params = json.loads(row[0])
            return params.get("max_risk_pct", DEFAULT_MAX_RISK_PCT)
    except Exception as e:
        log.warning("Could not load max_risk_pct from database: %s", e)

    return DEFAULT_MAX_RISK_PCT


def run_bot() -> None:
    """Main Bot C loop with adaptive position sizing."""
    sep = "─" * 70
    log.info(sep)
    log.info("Bot C (Hybrid) started │ %s", datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"))
    log.info(sep)

    ranks = load_stock_ranks()

    try:
        account_info = trading_client.get_account()
        equity = float(account_info.equity)
        cash = float(account_info.cash)
    except Exception as e:
        log.error("Failed to fetch Alpaca account info: %s", e)
        sys.exit("[FATAL] Cannot connect to Alpaca")

    engine = AdaptationEngine("C", db_path=DB_PATH)

    # Adapt only position sizing
    old_max_risk = load_bot_max_risk_pct()
    new_params = engine.suggest_c_params({"max_risk_pct": old_max_risk})
    new_max_risk = new_params["max_risk_pct"]

    if old_max_risk != new_max_risk:
        log.info("ADAPTATION: max_risk_pct updated: %.2f → %.2f", old_max_risk, new_max_risk)
        engine.log_adaptation({"max_risk_pct": old_max_risk}, new_params)
        max_risk_pct = new_max_risk
    else:
        max_risk_pct = old_max_risk

    log.info("Using fixed Minervini rules with max_risk_pct=%.2f", max_risk_pct)
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
    volatility_ok = is_volatility_acceptable(max_vix=VIX_MAX, min_vix=VIX_MIN)

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

            stop_loss = calculate_atr_stop_loss(highs, lows, closes, close, atr_multiplier=ATR_MULTIPLIER)
            take_profit = calculate_take_profit_price(close, atr=atr, profit_target_pct=TAKE_PROFIT_PCT)

            if stop_loss is None:
                log.warning("└── %s │ SKIP — invalid stop loss", ticker)
                continue

            qty = calculate_position_size(
                equity,
                close,
                stop_loss,
                max_risk_pct=max_risk_pct,
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
                max_positions=MAX_OPEN_POSITIONS, max_position_pct=MAX_POSITION_PCT,
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
                    notes=f"Bot C (hybrid), ATR=${atr:.2f}, risk_pct={max_risk_pct:.2f}",
                )
            except Exception as e:
                log.error("└── %s │ Order failed: %s", ticker, e)

            time.sleep(0.2)  # Spread API load

    log.info(sep)
    log.info("Bot C run completed")


if __name__ == "__main__":
    run_bot()
