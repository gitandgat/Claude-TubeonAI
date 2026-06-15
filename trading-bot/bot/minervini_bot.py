"""
minervini_bot.py — Mark Minervini Trend Template Trading Bot
─────────────────────────────────────────────────────────────

Entry: Minervini Trend Template (4 checks: MA alignment, RS>70, 25% from high, volume)
Exit:  Hard stop loss (-7%), take profit (+20%), time exit (~180 days), trailing stop (3% below high)
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
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional
import pytz

import requests
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from dotenv import load_dotenv

from data_fetcher import fetch_previous_close, fetch_daily_bars, fetch_minervini_metrics
from universe import get_universe
from universe_screener import screen_universe
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
MAX_PER_SECTOR = 2  # Diversification: at most 2 positions in any one GICS sector

# Trailing stop — DISABLED based on 24-month backtest (Jun 15 2026).
# The tight 3% trail (armed at +5%) HALVED returns: it scalped winners at
# +2-5% while losers ran to the full ATR stop — the inverse of "let winners
# run." Backtest: trail ON = +47.8%/Sharpe 1.40; trail OFF = +103%/Sharpe 2.01
# over the same window. Winners now ride to the +4×ATR target; the −2×ATR hard
# stop still cuts every loser fast. Re-enable (flip USE_TRAILING_STOP) only with
# a regime filter — a trail earns its keep in choppy/bear markets, not trends.
USE_TRAILING_STOP = False
TRAILING_STOP_PCT = 3.0
TRAILING_ACTIVATION_PCT = 5.0

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
    """Get volume ratio from cached values, return None if unavailable."""
    cached = get_cached_minervini_data(ticker, ranks)
    if cached["volume_sma"] is not None:
        return float(cached["volume_sma"])
    return None  # Return None when data unavailable (Polygon rate limit, etc.)


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
        # ── Full-universe screen: S&P 500, true percentile RS, accumulation ──
        # Replaces the 14-stock Kavout watchlist. Kavout still rides along as a
        # quality-overlay tag (kavout_endorsed) but no longer limits the universe.
        universe = get_universe()
        screened = screen_universe(universe, kavout_ranks=ranks)
        log.info("Screen surfaced %d Trend-Template candidates (RS-ranked)", len(screened))

        # Sector diversification: count sectors already held so we cap exposure
        held_sectors = Counter(
            universe.get(t) or get_stock_sector(t) or "Unknown" for t in positions
        )
        entries_made = 0

        for cand in screened:
            ticker = cand["ticker"]
            alpaca_ticker = TICKER_ALIASES.get(ticker, ticker)

            if len(positions) + entries_made >= MAX_OPEN_POSITIONS:
                log.info("Reached MAX_OPEN_POSITIONS (%d) — done entering", MAX_OPEN_POSITIONS)
                break
            if alpaca_ticker in positions:
                continue  # already holding

            sector = cand["sector"]
            if held_sectors[sector] >= MAX_PER_SECTOR:
                log.info("┌── %s │ SKIP — sector '%s' already at cap (%d)",
                         ticker, sector, MAX_PER_SECTOR)
                continue

            real_price = cand["price"]
            ma_20, ma_50, ma_200 = cand["ma_20"], cand["ma_50"], cand["ma_200"]
            rs_rank = cand["rs_rank"]
            distance_52w_pct = cand["distance_52w"]
            volume_ratio = cand["volume_ratio"]
            closes, highs, lows = cand["closes"], cand["highs"], cand["lows"]

            tag = " ★Kavout" if cand["kavout_endorsed"] else ""
            log.info("┌── %s │ RS=%d │ %s%s", ticker, rs_rank, sector, tag)
            vol_str = f"{volume_ratio:.2f}x" if volume_ratio is not None else "N/A"
            log.info("│   Price=$%.2f MA20=$%.2f MA50=$%.2f MA200=$%.2f │ 52W=%.1f%% vol=%s",
                     real_price, ma_20, ma_50, ma_200, distance_52w_pct * 100, vol_str)

            # ATR-based stop loss and take profit
            atr = calculate_atr(highs, lows, closes, period=14)
            if atr is None:
                log.warning("└── %s │ SKIP — could not calculate ATR", ticker)
                continue
            stop_loss = calculate_atr_stop_loss(highs, lows, closes, real_price, atr_multiplier=2.0)
            take_profit = calculate_take_profit_price(real_price, atr=atr, profit_target_pct=20.0)
            if stop_loss is None:
                log.warning("└── %s │ SKIP — invalid stop loss calculation", ticker)
                continue

            # Position sizing (risk-based), scaled by sector strength
            qty = calculate_position_size(
                float(account.equity), real_price, stop_loss,
                max_risk_pct=MAX_RISK_PER_TRADE_PCT,
            )
            sector_weight = calculate_sector_weight_multiplier(ticker, sector_scores)
            qty = int(qty * sector_weight)

            # Cap at the per-position ceiling by TRIMMING (not rejecting). With a
            # diverse universe of lower-priced names, tight-ATR risk sizing often
            # lands a few % over 20%; rejecting outright would block most trades.
            max_qty_by_cap = int((float(account.equity) * MAX_POSITION_PCT / 100) / real_price)
            if qty > max_qty_by_cap:
                log.info("│   Trimming %d→%d shares to respect %.0f%% position cap",
                         qty, max_qty_by_cap, MAX_POSITION_PCT)
                qty = max_qty_by_cap
            if qty < 1:
                log.warning("└── %s │ SKIP — position size < 1 share", ticker)
                continue

            # Position limits (count + final sanity; size already capped above)
            position_value = real_price * qty
            is_valid, reason = validate_position_limits(
                float(account.equity), position_value, len(positions) + entries_made,
                max_positions=MAX_OPEN_POSITIONS, max_position_pct=MAX_POSITION_PCT,
            )
            if not is_valid:
                log.warning("└── %s │ Position limit: %s", ticker, reason)
                continue

            # Intraday entry confirmation (market hours). Dry runs skip it so the
            # full buy path can be exercised outside trading hours.
            intraday_ok, intraday_reason = should_enter_intraday(
                ticker, real_price, skip_intraday_check=DRY_RUN
            )
            if not intraday_ok:
                log.warning("└── %s │ Intraday check failed: %s", ticker, intraday_reason)
                continue

            log.info(
                "└── ENTRY: BUY %d %s @ $%.2f (stop=$%.2f target=$%.2f ATR=%.2f)",
                qty, ticker, real_price, stop_loss, take_profit, atr,
            )
            place_order(client, alpaca_ticker, OrderSide.BUY, qty)

            if not DRY_RUN:
                alert_entry_signal(
                    ticker=ticker, entry_price=real_price, qty=qty,
                    stop_loss=stop_loss, take_profit=take_profit,
                    rs_rank=rs_rank, sector=sector,
                    notes=f"RS {rs_rank}, ATR=${atr:.2f}" + (" Kavout★" if cand["kavout_endorsed"] else ""),
                )
                tracker.open_trade(
                    ticker, datetime.now(ET), real_price, qty, stop_loss, take_profit,
                )
                kv = ranks.get(ticker, {})
                tracker.log_signal(
                    datetime.now(ET), ticker, real_price,
                    ma_20=ma_20, ma_50=ma_50, ma_200=ma_200,
                    rs_rank=rs_rank, distance_52w=distance_52w_pct,
                    volume_ratio=volume_ratio, trend_template_pass=True, signal="BUY",
                    kavout_rank=kv.get("rank"), kavout_outlook=kv.get("outlook"),
                    kavout_tech=kv.get("tech"),
                )

            held_sectors[sector] += 1
            entries_made += 1
            time.sleep(13)  # Rate limit between entries

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

            # Normalize entry_date — tolerate naive timestamps (assume ET)
            entry_dt = trade["entry_date"]
            if entry_dt.tzinfo is None:
                entry_dt = ET.localize(entry_dt)

            # Peak tracking (kept for logging + optional trailing stop)
            peak = max(trade.get("highest_price_seen") or 0, trade["entry_price"])
            if current_price > peak:
                peak = current_price
                tracker.update_trade_highest_price(trade["trade_id"], peak)

            # Trailing stop (DISABLED by default — see USE_TRAILING_STOP note).
            # Backtest proved the tight trail scalps winners and halves returns.
            trailing_stop = None
            if USE_TRAILING_STOP:
                trail_pct = trade.get("trailing_stop_pct") or TRAILING_STOP_PCT
                activation_level = trade["entry_price"] * (1 + TRAILING_ACTIVATION_PCT / 100)
                if peak >= activation_level:
                    trailing_stop = peak * (1 - trail_pct / 100)

            # Check exit conditions: hard stop → target → (trailing) → time.
            # With the trail off, winners ride to the +4×ATR target; losers are
            # still cut fast at the −2×ATR hard stop.
            exit_reason = None
            if current_price <= trade["stop_loss_level"]:
                exit_reason = "STOP_LOSS"
            elif current_price >= trade["take_profit_level"]:
                exit_reason = "TAKE_PROFIT"
            elif trailing_stop is not None and current_price <= trailing_stop:
                exit_reason = "TRAILING_STOP"
            elif (datetime.now(ET) - entry_dt).days > 180:
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

                if DRY_RUN:
                    # Don't mutate tracker state on dry runs — no order was
                    # actually placed, so the position is still open.
                    log.info("└── %s │ [DRY-RUN] tracker left OPEN", ticker)
                else:
                    alert_exit_signal(
                        ticker=ticker,
                        exit_price=current_price,
                        qty=qty_held,
                        exit_reason=exit_reason,
                        entry_price=trade["entry_price"],
                        profit_loss_pct=profit_loss_pct,
                    )
                    tracker.close_trade(
                        trade["trade_id"],
                        datetime.now(ET),
                        current_price,
                        qty_held,
                        exit_reason,
                    )
            else:
                unrealized_pct = ((current_price - trade["entry_price"]) / trade["entry_price"]) * 100
                trail_str = f"${trailing_stop:.2f}" if trailing_stop is not None else "off"
                log.info(
                    "└── %s │ HOLD @ $%.2f (entry=$%.2f, peak=$%.2f, unrealized=%+.2f%%) │ "
                    "stop=$%.2f target=$%.2f trail=%s",
                    ticker,
                    current_price,
                    trade["entry_price"],
                    peak,
                    unrealized_pct,
                    trade["stop_loss_level"],
                    trade["take_profit_level"],
                    trail_str,
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
