"""
readiness_check.py — Objective go-live gate for real-money deployment.
──────────────────────────────────────────────────────────────────────

Scores the live forward test (forward_test.json) against the go-live
checklist every day and prints a READY / NOT-READY verdict. When ALL gates
pass for the first time, it fires a one-time alert (email + Slack) so the
SYSTEM tells you the moment it's ready — no eyeballing required.

Gates (all must pass):
  1. Closed trades        >= 30      (below this, stats are noise)
  2. Days live            >= 60      (floor; 90+ preferred for regime variety)
  3. Profit factor        >= 1.5     (gross wins / gross losses)
  4. Beats SPY            screen return > SPY return since inception
  5. Beats Kavout         screen return > Kavout return
  6. Regime tested        SPY had a >= 5% drawdown since inception
  7. Drawdown controlled  screen max drawdown not worse than -15%

Run daily (wired into DAILY_CHECK.sh). Verdict is machine-checked, not a
judgment call — readiness is decided by evidence.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from data_fetcher import alpaca_latest_price, alpaca_get_bars

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("readiness")

STATE_FILE = Path(__file__).resolve().parent / "forward_test.json"
READY_FLAG = Path(__file__).resolve().parent / "go_live_ready.flag"
START_EQUITY = 100_000.0

# Gate thresholds
MIN_TRADES = 30
MIN_DAYS = 60
MIN_PROFIT_FACTOR = 1.5
MIN_SPY_PULLBACK_PCT = 5.0      # regime test: index must have wobbled
MAX_DRAWDOWN_PCT = 15.0          # screen drawdown tolerance


def _account_stats(acct: dict) -> dict:
    closed = acct.get("closed", [])
    wins = [c for c in closed if c["pnl_pct"] > 0]
    losses = [c for c in closed if c["pnl_pct"] <= 0]
    gross_w = sum(c["pnl_pct"] for c in wins)
    gross_l = abs(sum(c["pnl_pct"] for c in losses))
    pf = gross_w / gross_l if gross_l > 0 else (float("inf") if gross_w > 0 else 0.0)
    curve = [p["equity"] for p in acct.get("equity_curve", [])]
    max_dd = 0.0
    peak = START_EQUITY
    for v in curve:
        peak = max(peak, v)
        max_dd = min(max_dd, (v - peak) / peak * 100)
    eq = curve[-1] if curve else START_EQUITY
    return {"closed": len(closed), "win_rate": len(wins) / len(closed) * 100 if closed else 0,
            "profit_factor": pf, "return_pct": (eq / START_EQUITY - 1) * 100,
            "max_dd": max_dd, "equity": eq}


def _spy_drawdown_since(inception: str) -> float:
    """Largest SPY peak-to-trough drawdown (%) since inception (regime test)."""
    days = (datetime.now(timezone.utc).date() - datetime.fromisoformat(inception).date()).days + 5
    bars = alpaca_get_bars("SPY", days=max(days, 10))
    if not bars or len(bars["closes"]) < 2:
        return 0.0
    closes = bars["closes"]
    peak, dd = closes[0], 0.0
    for c in closes:
        peak = max(peak, c)
        dd = min(dd, (c - peak) / peak * 100)
    return dd


def evaluate() -> dict:
    if not STATE_FILE.exists():
        print("Forward test has not started yet (no forward_test.json).")
        return {"ready": False}

    state = json.loads(STATE_FILE.read_text())
    inception = state.get("inception")
    if not inception:
        print("Forward test not yet initialized.")
        return {"ready": False}

    days_live = (datetime.now(timezone.utc).date() - datetime.fromisoformat(inception).date()).days
    screen = _account_stats(state["accounts"]["screen"])
    kavout = _account_stats(state["accounts"]["kavout"])

    spy = alpaca_latest_price("SPY")
    spy_start = state.get("spy_start")
    spy_ret = (spy / spy_start - 1) * 100 if spy and spy_start else 0.0
    spy_dd = _spy_drawdown_since(inception)

    gates = [
        ("Closed trades >= %d" % MIN_TRADES, screen["closed"] >= MIN_TRADES,
         f"{screen['closed']}"),
        ("Days live >= %d" % MIN_DAYS, days_live >= MIN_DAYS, f"{days_live}"),
        ("Profit factor >= %.1f" % MIN_PROFIT_FACTOR,
         screen["closed"] >= MIN_TRADES and screen["profit_factor"] >= MIN_PROFIT_FACTOR,
         f"{screen['profit_factor']:.2f}"),
        ("Beats SPY", screen["return_pct"] > spy_ret,
         f"{screen['return_pct']:+.1f}% vs {spy_ret:+.1f}%"),
        ("Beats Kavout", screen["return_pct"] > kavout["return_pct"],
         f"{screen['return_pct']:+.1f}% vs {kavout['return_pct']:+.1f}%"),
        ("Regime tested (SPY pullback >= %.0f%%)" % MIN_SPY_PULLBACK_PCT,
         spy_dd <= -MIN_SPY_PULLBACK_PCT, f"SPY DD {spy_dd:.1f}%"),
        ("Drawdown <= %.0f%%" % MAX_DRAWDOWN_PCT, screen["max_dd"] >= -MAX_DRAWDOWN_PCT,
         f"{screen['max_dd']:.1f}%"),
    ]
    ready = all(passed for _, passed, _ in gates)
    passed_n = sum(1 for _, p, _ in gates if p)

    print("\n" + "=" * 60)
    print(f"  GO-LIVE READINESS — day {days_live} since {inception}")
    print("=" * 60)
    for label, passed, detail in gates:
        print(f"  [{'✓' if passed else ' '}] {label:<40}{detail:>15}")
    print("-" * 60)
    print(f"  {passed_n}/{len(gates)} gates passed")
    if ready:
        print("  ✅ READY — criteria met. Begin phased real-money deployment")
        print("     (start 10-25% of intended capital, scale over 2-3 months).")
    else:
        print("  ⏳ NOT READY — keep paper-trading. This is expected early on.")
    print("=" * 60 + "\n")

    if ready and not READY_FLAG.exists():
        _fire_ready_alert(gates, screen, days_live)
        READY_FLAG.write_text(json.dumps(
            {"ready_at": datetime.now(timezone.utc).isoformat(), "days_live": days_live}, indent=2))

    return {"ready": ready, "passed": passed_n, "total": len(gates),
            "days_live": days_live, "screen": screen}


def _fire_ready_alert(gates, screen, days_live) -> None:
    try:
        from alerts import send_email, send_slack_message
        lines = "\n".join(f"  [{'PASS' if p else 'FAIL'}] {lbl}: {d}" for lbl, p, d in gates)
        body = (f"The Minervini bot has PASSED all go-live criteria after "
                f"{days_live} days of forward testing.\n\n"
                f"Forward return: {screen['return_pct']:+.1f}%  |  "
                f"Win rate: {screen['win_rate']:.0f}%  |  "
                f"Profit factor: {screen['profit_factor']:.2f}  |  "
                f"Trades: {screen['closed']}\n\n{lines}\n\n"
                f"NEXT STEP: begin phased real-money deployment — start at "
                f"10-25% of intended capital and scale over 2-3 months. Do NOT "
                f"go all-in at once.")
        send_email("🟢 Trading bot READY for real money", body)
        send_slack_message("🟢 Minervini bot passed ALL go-live gates — ready for phased real-money deployment.")
        log.info("READY alert sent (email + Slack).")
    except Exception as e:
        log.warning("Could not send READY alert: %s", e)


if __name__ == "__main__":
    evaluate()
