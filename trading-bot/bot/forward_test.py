"""
forward_test.py — Tier-2 forward paper-trade: Screen vs Kavout vs SPY.
─────────────────────────────────────────────────────────────────────

Two virtual $100K accounts run forward with ZERO lookahead — the honest,
survivorship-free validation a historical backtest can't give (and the ONLY
way to compare against Kavout, whose past ratings were never stored):

  • "screen"  — picks from the full S&P 500 screen (Minervini + percentile RS)
  • "kavout"  — picks from Kavout's High/Outperform names in ranks.json

Both accounts use IDENTICAL exit rules (ATR stop, ATR target, 180d time),
equal-weight sizing, and a 2-per-sector cap — so the ONLY variable is stock
SELECTION. SPY is the shared benchmark. Run once daily after the live bot.

State persists in forward_test.json. After ~4-8 weeks this is the clean read
on whether the screen actually out-selects Kavout in real, unseen markets.

CAVEAT: Kavout here is its real configured output — a small, infrequently
refreshed watchlist. A broader/fresher Kavout feed would be a stronger
opponent; this measures Kavout AS IT ACTUALLY EXISTS in this system.
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from universe import get_universe
from universe_screener import screen_universe
from data_fetcher import alpaca_latest_price, alpaca_get_bars
from indicators import calculate_atr

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("forward")

# .resolve() so paths are correct whether run via absolute path (scheduler)
# or as a relative invocation (cd bot && python forward_test.py)
STATE_FILE = Path(__file__).resolve().parent / "forward_test.json"
RANKS_FILE = Path(__file__).resolve().parent.parent / "ranks.json"
START_EQUITY = 100_000.0
MAX_OPEN = 5
MAX_PER_SECTOR = 2
ATR_STOP_MULT = 2.0
ATR_TARGET_MULT = 4.0
TIME_EXIT_DAYS = 180
ACCOUNTS = ("screen", "kavout")


def _new_account() -> dict:
    return {"cash": START_EQUITY, "positions": {}, "closed": [], "equity_curve": []}


def _load_state() -> dict:
    if STATE_FILE.exists():
        s = json.loads(STATE_FILE.read_text())
        if "accounts" in s:
            return s
        # migrate single-account schema → dual-account (reset, day-1 only)
        log.info("Migrating forward_test.json to dual-account schema")
    return {"inception": None, "spy_start": None,
            "accounts": {a: _new_account() for a in ACCOUNTS}}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


def _positions_value(positions: dict) -> float:
    total = 0.0
    for t, p in positions.items():
        price = alpaca_latest_price(t) or p["entry"]
        total += p["qty"] * price
    return total


# ── Candidate sources (the only thing that differs between accounts) ──────────

def _screen_candidates() -> list:
    """Full S&P 500 screen output (already RS-sorted, with bars + sector)."""
    return screen_universe(get_universe())


def _kavout_candidates() -> list:
    """Kavout's High/Outperform names, shaped like screen candidates."""
    if not RANKS_FILE.exists():
        return []
    ranks = json.loads(RANKS_FILE.read_text())
    universe = get_universe()
    picks = [(t, e) for t, e in ranks.items()
             if e.get("rank") == "High" and e.get("outlook") == "Outperform"]
    out = []
    for tkr, entry in picks:
        # Retry: single-symbol fetches can be throttled right after the screen's
        # 500-stock batch. Don't let a transient None fake a "Kavout picked nothing".
        bars = None
        for attempt in range(3):
            bars = alpaca_get_bars(tkr, days=60)
            if bars and len(bars["closes"]) >= 15:
                break
            time.sleep(1.5)
        if not bars or len(bars["closes"]) < 15:
            log.warning("  Kavout pick %s: bars unavailable after retries — skipped", tkr)
            continue
        out.append({
            "ticker": tkr,
            "sector": universe.get(tkr) or "Unknown",
            "price": bars["closes"][-1],
            "highs": bars["highs"], "lows": bars["lows"], "closes": bars["closes"],
            "rs_rank": int(entry.get("rs_rank") or 50),
            "kavout_endorsed": True,
        })
    out.sort(key=lambda c: c["rs_rank"], reverse=True)
    return out


# ── Shared position management (identical for both accounts) ──────────────────

def _manage_account(acct: dict, candidates: list, today: str) -> None:
    positions = acct["positions"]

    # Exits
    for tkr in list(positions.keys()):
        p = positions[tkr]
        price = alpaca_latest_price(tkr)
        if price is None:
            continue
        p["peak"] = max(p.get("peak", p["entry"]), price)
        held = (datetime.fromisoformat(today) - datetime.fromisoformat(p["entry_date"])).days
        reason = ("STOP" if price <= p["stop"] else
                  "TARGET" if price >= p["target"] else
                  "TIME" if held >= TIME_EXIT_DAYS else None)
        if reason:
            acct["cash"] += p["qty"] * price
            pnl = (price - p["entry"]) / p["entry"] * 100
            acct["closed"].append({"ticker": tkr, "entry": p["entry"], "exit": price,
                                   "pnl_pct": round(pnl, 2), "reason": reason,
                                   "held_days": held, "exit_date": today})
            log.info("  EXIT %s @ $%.2f (%s) %+.1f%%", tkr, price, reason, pnl)
            del positions[tkr]

    # Entries (equal-weight, sector-capped)
    if len(positions) >= MAX_OPEN:
        return
    sector_count: dict = {}
    for t in positions:
        sector_count[positions[t]["sector"]] = sector_count.get(positions[t]["sector"], 0) + 1
    slot_value = (acct["cash"] + _positions_value(positions)) / MAX_OPEN

    for c in candidates:
        if len(positions) >= MAX_OPEN:
            break
        if c["ticker"] in positions or sector_count.get(c["sector"], 0) >= MAX_PER_SECTOR:
            continue
        atr = calculate_atr(c["highs"], c["lows"], c["closes"], period=14)
        if not atr or atr <= 0:
            continue
        price = c["price"]
        qty = int(min(slot_value, acct["cash"]) / price)
        if qty < 1:
            continue
        acct["cash"] -= qty * price
        positions[c["ticker"]] = {
            "qty": qty, "entry": price, "peak": price,
            "stop": round(price - ATR_STOP_MULT * atr, 2),
            "target": round(price + ATR_TARGET_MULT * atr, 2),
            "sector": c["sector"], "rs": c["rs_rank"], "entry_date": today,
        }
        sector_count[c["sector"]] = sector_count.get(c["sector"], 0) + 1
        log.info("  ENTER %s @ $%.2f RS=%d %s", c["ticker"], price, c["rs_rank"], c["sector"])


def run_forward() -> None:
    state = _load_state()
    today = datetime.now(timezone.utc).date().isoformat()
    spy = alpaca_latest_price("SPY")

    if state["inception"] is None:
        state["inception"] = today
        state["spy_start"] = spy
        log.info("Forward test inception: %s (SPY=%.2f)", today, spy or 0)

    log.info("── SCREEN account ──")
    _manage_account(state["accounts"]["screen"], _screen_candidates(), today)
    log.info("── KAVOUT account ──")
    _manage_account(state["accounts"]["kavout"], _kavout_candidates(), today)

    for name in ACCOUNTS:
        acct = state["accounts"][name]
        eq = acct["cash"] + _positions_value(acct["positions"])
        acct["equity_curve"].append({"date": today, "equity": round(eq, 2)})

    _save_state(state)
    _report(state, spy)


def _report(state: dict, spy: float) -> None:
    spy_ret = ((spy / state["spy_start"]) - 1) * 100 if spy and state["spy_start"] else 0.0
    print("\n" + "=" * 60)
    print(f"  FORWARD HEAD-TO-HEAD — since {state['inception']}")
    print("=" * 60)
    print(f"  {'Account':<10}{'Equity':>13}{'Return':>10}{'Open':>6}{'Closed':>8}{'Win%':>7}")
    print("-" * 60)
    rows = {}
    for name in ACCOUNTS:
        acct = state["accounts"][name]
        eq = acct["cash"] + _positions_value(acct["positions"])
        ret = (eq / START_EQUITY - 1) * 100
        closed = acct["closed"]
        wins = [c for c in closed if c["pnl_pct"] > 0]
        wr = len(wins) / len(closed) * 100 if closed else 0
        rows[name] = ret
        print(f"  {name:<10}${eq:>11,.0f}{ret:>9.1f}%{len(acct['positions']):>6}"
              f"{len(closed):>8}{wr:>6.0f}%")
    print(f"  {'SPY':<10}{'—':>13}{spy_ret:>9.1f}%")
    print("-" * 60)
    print(f"  Screen vs Kavout: {rows['screen']-rows['kavout']:+.1f} pts   "
          f"Screen vs SPY: {rows['screen']-spy_ret:+.1f} pts")
    print("=" * 60)
    for name in ACCOUNTS:
        pos = state["accounts"][name]["positions"]
        if pos:
            held = ", ".join(f"{t}(RS{p['rs']})" for t, p in
                             sorted(pos.items(), key=lambda kv: -kv[1]["rs"]))
            print(f"  {name}: {held}")
    print()


if __name__ == "__main__":
    run_forward()
