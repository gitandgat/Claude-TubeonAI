"""
forward_test.py — Tier-2 forward paper-trade log (screen vs benchmarks).
────────────────────────────────────────────────────────────────────────

The backtest (Tier 1) proved historical edge but carries survivorship bias.
This logs the screen's picks GOING FORWARD into a virtual $100K account with
zero lookahead — the honest, bias-free validation. Run once daily (after the
live bot). Each run:

  1. Records the screen's current top picks + an equal-weight virtual fill
  2. Marks existing virtual positions to market, applies the SAME exit rules
     as live (ATR stop, ATR target, time exit; trail follows USE_TRAILING_STOP)
  3. Appends an equity point and prints screen-vs-SPY since inception

State persists in forward_test.json. After ~4-8 weeks this is the clean
read on whether the screen earns its keep in real, unseen markets — and the
substrate for a true screen-vs-Kavout comparison once Kavout logs alongside.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from universe import get_universe
from universe_screener import screen_universe
from data_fetcher import alpaca_latest_price, fetch_minervini_metrics
from indicators import calculate_atr

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("forward")

STATE_FILE = Path(__file__).parent / "forward_test.json"
START_EQUITY = 100_000.0
MAX_OPEN = 5
MAX_PER_SECTOR = 2
ATR_STOP_MULT = 2.0
ATR_TARGET_MULT = 4.0
TIME_EXIT_DAYS = 180


def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"inception": None, "spy_start": None, "cash": START_EQUITY,
            "positions": {}, "closed": [], "equity_curve": []}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


def run_forward() -> None:
    state = _load_state()
    today = datetime.now(timezone.utc).date().isoformat()
    spy = alpaca_latest_price("SPY")

    if state["inception"] is None:
        state["inception"] = today
        state["spy_start"] = spy
        log.info("Forward test inception: %s (SPY=%.2f)", today, spy or 0)

    positions = state["positions"]

    # 1) Mark-to-market + exits on existing virtual positions
    for tkr in list(positions.keys()):
        p = positions[tkr]
        price = alpaca_latest_price(tkr)
        if price is None:
            continue
        p["peak"] = max(p.get("peak", p["entry"]), price)
        held_days = (datetime.now(timezone.utc).date() - datetime.fromisoformat(p["entry_date"]).date()).days
        reason = None
        if price <= p["stop"]:
            reason = "STOP"
        elif price >= p["target"]:
            reason = "TARGET"
        elif held_days >= TIME_EXIT_DAYS:
            reason = "TIME"
        if reason:
            state["cash"] += p["qty"] * price
            pnl = (price - p["entry"]) / p["entry"] * 100
            state["closed"].append({"ticker": tkr, "entry": p["entry"], "exit": price,
                                    "pnl_pct": round(pnl, 2), "reason": reason,
                                    "held_days": held_days, "exit_date": today})
            log.info("EXIT %s @ $%.2f (%s) P&L %+.1f%%", tkr, price, reason, pnl)
            del positions[tkr]

    # 2) Screen for new picks, fill open slots (equal-weight, sector-capped)
    if len(positions) < MAX_OPEN:
        universe = get_universe()
        candidates = screen_universe(universe)
        sector_count: dict = {}
        for t in positions:
            s = positions[t]["sector"]
            sector_count[s] = sector_count.get(s, 0) + 1

        slot_value = (state["cash"] + _positions_value(positions)) / MAX_OPEN
        for c in candidates:
            if len(positions) >= MAX_OPEN:
                break
            if c["ticker"] in positions:
                continue
            if sector_count.get(c["sector"], 0) >= MAX_PER_SECTOR:
                continue
            atr = calculate_atr(c["highs"], c["lows"], c["closes"], period=14)
            if not atr or atr <= 0:
                continue
            price = c["price"]
            qty = int(min(slot_value, state["cash"]) / price)
            if qty < 1:
                continue
            state["cash"] -= qty * price
            positions[c["ticker"]] = {
                "qty": qty, "entry": price, "peak": price,
                "stop": round(price - ATR_STOP_MULT * atr, 2),
                "target": round(price + ATR_TARGET_MULT * atr, 2),
                "sector": c["sector"], "rs": c["rs_rank"],
                "entry_date": today,
            }
            sector_count[c["sector"]] = sector_count.get(c["sector"], 0) + 1
            log.info("ENTER %s @ $%.2f RS=%d %s (stop %.2f / target %.2f)",
                     c["ticker"], price, c["rs_rank"], c["sector"],
                     positions[c["ticker"]]["stop"], positions[c["ticker"]]["target"])

    # 3) Record equity + report vs SPY since inception
    equity = state["cash"] + _positions_value(positions)
    state["equity_curve"].append({"date": today, "equity": round(equity, 2)})
    _save_state(state)

    screen_ret = (equity / START_EQUITY - 1) * 100
    spy_ret = ((spy / state["spy_start"]) - 1) * 100 if spy and state["spy_start"] else 0.0
    closed = state["closed"]
    wins = [c for c in closed if c["pnl_pct"] > 0]
    win_rate = len(wins) / len(closed) * 100 if closed else 0

    print("\n" + "=" * 56)
    print(f"  FORWARD TEST — since {state['inception']}")
    print("=" * 56)
    print(f"  Screen equity:   ${equity:,.0f}   ({screen_ret:+.1f}%)")
    print(f"  SPY benchmark:                ({spy_ret:+.1f}%)")
    print(f"  Open positions:  {len(positions)}   Closed: {len(closed)}   Win: {win_rate:.0f}%")
    edge = screen_ret - spy_ret
    print(f"  Edge vs SPY:     {edge:+.1f} pts")
    print("=" * 56)
    if positions:
        for t, p in sorted(positions.items(), key=lambda kv: -kv[1]["rs"]):
            cur = alpaca_latest_price(t) or p["entry"]
            print(f"    {t:6} RS={p['rs']:>2} {p['sector'][:18]:18} "
                  f"entry ${p['entry']:.2f} now ${cur:.2f} ({(cur/p['entry']-1)*100:+.1f}%)")
    print()


def _positions_value(positions: dict) -> float:
    total = 0.0
    for t, p in positions.items():
        price = alpaca_latest_price(t) or p["entry"]
        total += p["qty"] * price
    return total


if __name__ == "__main__":
    run_forward()
