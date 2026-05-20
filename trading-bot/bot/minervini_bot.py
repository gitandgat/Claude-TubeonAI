"""
minervini_bot.py — Mark Minervini Trend Template Trading Bot
─────────────────────────────────────────────────────────────

Entry: Minervini Trend Template (4 checks: MA alignment, RS>70, 25% from high, volume)
Exit:  Hard stop loss (-7%), take profit (+20%), time exit (~180 days), trailing stop
Position Sizing: Risk-based (1.25-2.5% per trade), NOT fixed dollars

Two-layer validation:
1. Kavout pre-filter (High rank + Outperform outlook)
2. Minervini validator (all 4 Trend Template checks)
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional
import pytz

import requests
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from dotenv import load_dotenv

from data_fetcher import fetch_previous_close, fetch_daily_bars
from trend_filter import validate_trend_template, format_trend_result
from position_manager import (
    calculate_position_size,
    calculate_take_profit_price,
    calculate_atr_stop_loss,
    validate_position_limits,
)
from indicators import (
    calculate_rs_rank,
    is_market_in_uptrend,
    is_volatility_acceptable,
    calculate_atr,
)
from intraday_filter import should_enter_intraday
from sector_rotation import (
    get_sector_strength_scores,
    get_stock_sector,
    calculate_sector_weight_multiplier,
    get_strongest_sectors,
)
from alerts import (
    alert_entry_signal,
    alert_exit_signal,
    alert_market_condition_change,
)
from trade_tracker import TradeTracker

load_dotenv()

# ── Dry-run mode (for testing without placing orders) ───────────────────────
DRY_RUN = "--dry-run" in sys.argv or os.getenv("DRY_RUN", "").lower() == "true"

# ── Environment variables ────────────────────────────────────────────────────
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")
PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"

_missing = [
    k
    for k, v in {
        "ALPACA_API_KEY": ALPACA_API_KEY,
        "ALPACA_SECRET_KEY": ALPACA_SECRET_KEY,
        "MASSIVE_API_KEY": MASSIVE_API_KEY,
    }.items()
    if not v
]
if _missing:
    sys.exit(f"[FATAL] Missing environment variables: {', '.join(_missing)}")

# ── Configuration ────────────────────────────────────────────────────────────
RANKS_FILE = Path(__file__).parent.parent / "ranks.json"
DB_FILE = Path(__file__).parent.parent / "trading_bot.db"

ET = pytz.timezone("America/New_York")


def load_stock_ranks() -> Dict:
    """Read ranks.json at runtime so today's scores are always picked up."""
    if not RANKS_FILE.exists():
        sys.exit(f"[FATAL] ranks.json not found at {RANKS_FILE}. Run scrape_kavout.py first.")
    with open(RANKS_FILE) as f:
        return json.load(f)

# Minervini Risk Parameters
MAX_RISK_PER_TRADE_PCT = 1.25  # 1.25% of account per trade
STOP_LOSS_PCT = 7.0  # Hard -7% stop
TAKE_PROFIT_PCT = 20.0  # Take profit at +20%
MAX_OPEN_POSITIONS = 5
MAX_POSITION_PCT = 20.0  # Max 20% of account per position

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


def get_cached_minervini_data(ticker: str, ranks: dict) -> dict:
    """Get cached MA, RS, distance, volume from ranks.json (populated by scrape_kavout.py)."""
    entry = ranks.get(ticker, {})
    return {
        "ma_20": entry.get("ma_20"),
        "ma_50": entry.get("ma_50"),
        "ma_200": entry.get("ma_200"),
        "rs_rank": entry.get("rs_rank"),
        "distance_52w": entry.get("distance_52w"),
        "volume_sma": entry.get("volume_sma"),
    }


def get_rs_rank_from_ranks(ticker: str, ranks: dict) -> int:
    """Get RS rank from ranks.json (populated by scrape_kavout.py)."""
    cached = get_cached_minervini_data(ticker, ranks)
    if cached["rs_rank"] is not None:
        return int(cached["rs_rank"])
    return 50  # Default to 50 if not available


def fetch_ma_levels_with_cache(
    ticker: str, ranks: dict
) -> tuple[float, float, float] | None:
    """Fetch MA20/50/200, using cached values from ranks.json when available."""
    cached = get_cached_minervini_data(ticker, ranks)
    if all(cached[k] is not None for k in ["ma_20", "ma_50", "ma_200"]):
        return (float(cached["ma_20"]), float(cached["ma_50"]), float(cached["ma_200"]))
    return None


def fetch_52week_high_with_cache(ticker: str, ranks: dict) -> float | None:
    """Calculate 52-week high from cached distance, or return None if unavailable."""
    cached = get_cached_minervini_data(ticker, ranks)
    if cached["distance_52w"] is not None:
        close = fetch_previous_close(ticker)
        if close:
            distance = float(cached["distance_52w"])
            return close / (1 - distance)
    return None


def fetch_volume_ratio_with_cache(ticker: str, ranks: dict) -> float | None:
    """Get volume ratio from cached values, default to 1.0 if unavailable."""
    cached = get_cached_minervini_data(ticker, ranks)
    if cached["volume_sma"] is not None:
        return float(cached["volume_sma"])
    return 1.0  # Default neutral volume ratio when cache miss


# ── Alpaca helpers ───────────────────────────────────────────────────────────


def get_client() -> TradingClient:
    return TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=PAPER_TRADING)


def get_open_positions(client: TradingClient) -> Dict[str, float]:
    """Return {ticker: qty} for all currently held positions."""
    return {p.symbol: float(p.qty) for p in client.get_all_positions()}


def place_order(
    client: TradingClient,
    ticker: str,
    side: OrderSide,
    qty: int,
) -> None:
    """Submit a DAY market order and log the outcome (or simulate if DRY_RUN)."""
    if DRY_RUN:
        log.info(
            "[DRY-RUN] ORDER WOULD BE PLACED │ %s %d %s",
            side.value.upper(),
            qty,
            ticker,
        )
        return

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
            side.value.upper(),
            qty,
            ticker,
            order.id,
        )
    except Exception as exc:
        log.error("ORDER FAILED │ %s %s │ %s", ticker, side.value.upper(), exc)


# ── Ticker alias handling ────────────────────────────────────────────────────
TICKER_ALIASES: Dict[str, str] = {"BRK-B": "BRK/B"}


# ── Main bot loop ────────────────────────────────────────────────────────────


def run_bot() -> None:
    """
    Main Minervini trading loop:
    1. Evaluate each Kavout-ranked stock
    2. Check Trend Template (4 conditions)
    3. Enter if all pass
    4. Exit on stop loss, take profit, or time
    """
    sep = "─" * 70
    log.info(sep)
    mode_str = "DRY-RUN (no orders placed)" if DRY_RUN else f"paper={PAPER_TRADING}"
    log.info(
        "Bot run started │ %s │ %s │ minervini",
        datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
        mode_str,
    )
    log.info(sep)

    # Initialize tracking
    ranks = load_stock_ranks()
    tracker = TradeTracker(str(DB_FILE))
    client = get_client()
    account = client.get_account()

    log.info(
        "Account │ equity=$%s │ buying_power=$%s",
        f"{float(account.equity):,.2f}",
        f"{float(account.buying_power):,.2f}",
    )

    positions = get_open_positions(client)
    log.info("Open positions: %s", list(positions.keys()) or "none")

    # ── ENTRY PHASE ───────────────────────────────────────────────────────────

    log.info(sep)
    log.info("ENTRY PHASE: Screening for Minervini Trend Template setups…")

    # Calculate sector strength scores
    log.info("Calculating sector strength scores…")
    sector_scores = get_sector_strength_scores()
    strongest = get_strongest_sectors(sector_scores, top_n=3)
    log.info("Strongest sectors: %s", ", ".join(strongest))

    # Pre-trade regime checks
    market_uptrend = is_market_in_uptrend()
    volatility_ok = is_volatility_acceptable(max_vix=30, min_vix=10)

    log.info("Market regime: %s", "UPTREND (SPY > MA200)" if market_uptrend else "⚠️  NO UPTREND")
    log.info("Volatility: %s", "OK (10 ≤ VIX ≤ 30)" if volatility_ok else "⚠️  OUTSIDE RANGE")

    if not market_uptrend or not volatility_ok:
        log.warning("Market conditions unfavorable — skipping entry screening")
    else:
        # Filter for Kavout High + Outperform (pre-filter)
        candidates = [
            t
            for t, entry in ranks.items()
            if entry.get("rank") == "High" and entry.get("outlook") == "Outperform"
        ]
        log.info(f"Kavout pre-filter: {len(candidates)} High/Outperform candidates")

        if not candidates:
            log.info("No Kavout High/Outperform candidates available.")

        for ticker in candidates:
            log.info("┌── %s", ticker)

            # Fetch market data (with cache-aware fallback for MA levels and 52W high)
            close = fetch_previous_close(ticker)
            ma_data = fetch_ma_levels_with_cache(ticker, ranks)
            fifty_two_w = fetch_52week_high_with_cache(ticker, ranks)

            if close is None or ma_data is None or fifty_two_w is None:
                log.warning(
                    "└── %s │ SKIP — missing market data (close=%s, ma=%s, 52w=%s)",
                    ticker,
                    close,
                    ma_data,
                    fifty_two_w,
                )
                continue

            ma_20, ma_50, ma_200 = ma_data
            distance_52w_pct = (fifty_two_w - close) / fifty_two_w

            real_price = close  # Use previous close as the current price

            # Fetch daily bars for ATR and RSI calculation
            bar_data = fetch_daily_bars(ticker, days=60)
            if bar_data is None:
                log.warning("└── %s │ SKIP — insufficient bar data for indicators", ticker)
                continue
            closes, highs, lows = bar_data

            # Calculate real RS Rank vs SPY (using 252-day returns)
            rs_rank = calculate_rs_rank(ticker)

            # Fetch volume ratio (with cache-aware fallback)
            volume_ratio = fetch_volume_ratio_with_cache(ticker, ranks)
            if volume_ratio is None:
                log.warning("└── %s │ SKIP — missing volume data", ticker)
                continue

            # Check Trend Template (now with closes for RSI confirmation)
            trend_result = validate_trend_template(
                ticker,
                real_price,
                ma_20,
                ma_50,
                ma_200,
                rs_rank,
                distance_52w_pct,
                volume_ratio,
                closes=closes,  # For RSI calculation
            )

            log.info("│   Price=$%.2f │ MA20=$%.2f MA50=$%.2f MA200=$%.2f", close, ma_20, ma_50, ma_200)
            log.info("│   RS=%d │ Distance_52W=%.1f%% │ Volume_ratio=%.2fx",
                     rs_rank, distance_52w_pct * 100, volume_ratio)
            log.info("│   %s", format_trend_result(ticker, trend_result))

            if not trend_result["passes"]:
                log.info("└── %s │ SKIP — Trend Template failed", ticker)
                continue

            # Position limit check
            alpaca_ticker = TICKER_ALIASES.get(ticker, ticker)
            if alpaca_ticker in positions:
                log.info("└── %s │ Already holding — SKIP", ticker)
                continue

            # Calculate ATR-based stop loss and take profit
            atr = calculate_atr(highs, lows, closes, period=14)
            if atr is None:
                log.warning("└── %s │ SKIP — could not calculate ATR", ticker)
                continue

            stop_loss = calculate_atr_stop_loss(highs, lows, closes, real_price, atr_multiplier=2.0)
            take_profit = calculate_take_profit_price(real_price, atr=atr, profit_target_pct=20.0)

            if stop_loss is None:
                log.warning("└── %s │ SKIP — invalid stop loss calculation", ticker)
                continue

            # Position sizing with ATR-based stop
            qty = calculate_position_size(
                float(account.equity),
                real_price,
                stop_loss,
                max_risk_pct=MAX_RISK_PER_TRADE_PCT,
            )

            # Apply sector weight multiplier
            sector = get_stock_sector(ticker)
            sector_weight = calculate_sector_weight_multiplier(ticker, sector_scores)
            qty_weighted = int(qty * sector_weight)

            if sector:
                sector_strength = sector_scores.get(sector, 50)
                log.info("│   Sector: %s (strength=%.0f) │ Weight: %.1fx", sector, sector_strength, sector_weight)

            if qty_weighted < 1:
                log.warning("└── %s │ Position size too small after sector weight (qty=%d, weighted=%d)",
                           ticker, qty, qty_weighted)
                continue

            qty = qty_weighted  # Use weighted quantity

            # Validate position limits
            position_value = real_price * qty
            is_valid, reason = validate_position_limits(
                float(account.equity),
                position_value,
                len(positions),
                max_positions=MAX_OPEN_POSITIONS,
                max_position_pct=MAX_POSITION_PCT,
            )
            if not is_valid:
                log.warning("└── %s │ Position limit: %s", ticker, reason)
                continue

            # Intraday entry confirmation (if market hours)
            intraday_ok, intraday_reason = should_enter_intraday(ticker, real_price)
            if not intraday_ok:
                log.warning("└── %s │ Intraday check failed: %s", ticker, intraday_reason)
                continue
            log.info("│   Intraday: %s ✓", intraday_reason)

            # Place buy order
            log.info(
                "└── ENTRY: BUY %d shares @ $%.2f (stop=$%.2f, target=$%.2f, ATR=%.2f)",
                qty,
                real_price,
                stop_loss,
                take_profit,
                atr,
            )
            place_order(client, alpaca_ticker, OrderSide.BUY, qty)

            # Send entry alert
            alert_entry_signal(
                ticker=ticker,
                entry_price=real_price,
                qty=qty,
                stop_loss=stop_loss,
                take_profit=take_profit,
                rs_rank=rs_rank,
                sector=get_stock_sector(ticker),
                notes=f"Intraday confirmed, ATR=${atr:.2f}",
            )

            # Log trade
            trade_id = tracker.open_trade(
                ticker,
                datetime.now(ET),
                real_price,
                qty,
                stop_loss,
                take_profit,
            )

            # Log signal
            entry = ranks.get(ticker, {})
            tracker.log_signal(
                datetime.now(ET),
                ticker,
                real_price,
                ma_20=ma_20,
                ma_50=ma_50,
                ma_200=ma_200,
                rs_rank=rs_rank,
                distance_52w=distance_52w_pct,
                volume_ratio=volume_ratio,
                trend_template_pass=True,
                signal="BUY",
                kavout_rank=entry.get("rank"),
                kavout_outlook=entry.get("outlook"),
                kavout_tech=entry.get("tech"),
            )

            time.sleep(13)  # Rate limit

    # ── EXIT PHASE ────────────────────────────────────────────────────────────

    log.info(sep)
    log.info("EXIT PHASE: Checking open positions for exit conditions…")

    open_trades = tracker.get_open_trades()
    if not open_trades:
        log.info("No open trades to check.")
    else:
        log.info(f"Monitoring {len(open_trades)} open positions…")

        for trade in open_trades:
            ticker = trade["ticker"]
            alpaca_ticker = TICKER_ALIASES.get(ticker, ticker)

            # Fetch current price (using previous close as proxy)
            current_price = fetch_previous_close(ticker)
            if not current_price:
                log.warning("└── %s │ No quote, skip exit check", ticker)
                continue

            # Check exit conditions
            exit_reason = None
            if current_price <= trade["stop_loss_level"]:
                exit_reason = "STOP_LOSS"
            elif current_price >= trade["take_profit_level"]:
                exit_reason = "TAKE_PROFIT"
            elif (datetime.now(ET) - trade["entry_date"]).days > 180:
                exit_reason = "TIME_EXIT"

            if exit_reason:
                qty_held = int(positions.get(alpaca_ticker, 0))
                profit_loss_pct = ((current_price - trade["entry_price"]) / trade["entry_price"]) * 100
                log.info(
                    "└── %s │ EXIT: SELL %d shares @ $%.2f (%s) │ P&L: %+.2f%%",
                    ticker,
                    qty_held,
                    current_price,
                    exit_reason,
                    profit_loss_pct,
                )

                if qty_held > 0:
                    place_order(client, alpaca_ticker, OrderSide.SELL, qty_held)

                # Send exit alert
                alert_exit_signal(
                    ticker=ticker,
                    exit_price=current_price,
                    qty=qty_held,
                    exit_reason=exit_reason,
                    entry_price=trade["entry_price"],
                    profit_loss_pct=profit_loss_pct,
                )

                # Close trade in tracker
                tracker.close_trade(
                    trade["trade_id"],
                    datetime.now(ET),
                    current_price,
                    qty_held,
                    exit_reason,
                )
            else:
                unrealized_pct = ((current_price - trade["entry_price"]) / trade["entry_price"]) * 100
                log.info(
                    "└── %s │ HOLD @ $%.2f (entry=$%.2f, unrealized=%+.2f%%)",
                    ticker,
                    current_price,
                    trade["entry_price"],
                    unrealized_pct,
                )

            time.sleep(13)

    # ── SUMMARY ────────────────────────────────────────────────────────────────

    log.info(sep)
    log.info("Bot run complete.")
    log.info(sep)

    # Print P&L summary
    tracker.print_summary(days=30)


if __name__ == "__main__":
    run_bot()
