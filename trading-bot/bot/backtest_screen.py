"""
backtest_screen.py — Point-in-time backtest of the S&P 500 screen vs SPY.
─────────────────────────────────────────────────────────────────────────

Validates whether the live selection engine (Minervini Trend Template + true
percentile RS + recent-accumulation) actually has edge — measured against the
only benchmark that matters: SPY buy-and-hold.

FAITHFUL BY CONSTRUCTION: candidate selection calls the SAME
`validate_trend_template` the live bot uses, fed point-in-time slices. Exit
math mirrors minervini_bot exactly (stop = entry − 2·ATR, target = entry +
4·ATR, trailing arms +5%/trails 3%, time-exit 180d). Sizing is risk-based
capped at 20% (5 positions, ≤2 per GICS sector) — same as live.

HONEST CAVEATS (printed in the report):
  • Survivorship: uses TODAY's S&P 500 membership over history → optimistic
  • Sample size: a 5-position swing strategy yields a thin trade count
  • Regime: results are conditional on the period's market regime
  • No live Kavout history exists, so this is screen-vs-SPY, not screen-vs-Kavout
    (that requires the Tier-2 forward test)

Usage:
    python bot/backtest_screen.py --months 24
    python bot/backtest_screen.py --months 12 --rebalance-days 5
"""

from __future__ import annotations

import argparse
import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

from universe import get_universe
from trend_filter import validate_trend_template

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("backtest")

# Strategy params — mirror minervini_bot.py exactly
MAX_OPEN = 5
MAX_PER_SECTOR = 2
MAX_RISK_PCT = 1.25
MAX_POSITION_PCT = 20.0
ATR_STOP_MULT = 2.0
ATR_TARGET_MULT = 4.0
TRAIL_ACTIVATION_PCT = 5.0
TRAIL_PCT = 3.0
TIME_EXIT_DAYS = 180
MIN_PRICE = 10.0
MIN_DOLLAR_VOLUME = 20_000_000
ACCUM_LOOKBACK = 10
ACCUM_VOL_MULT = 1.5
START_EQUITY = 100_000.0


def _fetch_vix_history() -> pd.Series:
    """Daily VIX close from FRED (keyless), indexed by date."""
    try:
        start = (datetime.now() - timedelta(days=1100)).strftime("%Y-%m-%d")
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS&cosd={start}"
        df = pd.read_csv(url)
        df.columns = ["date", "vix"]
        df["date"] = pd.to_datetime(df["date"])
        df["vix"] = pd.to_numeric(df["vix"], errors="coerce")
        return df.dropna().set_index("date")["vix"]
    except Exception as e:
        log.warning("VIX history fetch failed (%s) — volatility gate disabled in backtest", e)
        return pd.Series(dtype=float)


def _fetch_dated(symbols: list, days: int) -> dict:
    """Fetch bars WITH dates (needed for calendar alignment), cached."""
    cache = Path(__file__).parent / "backtest_dated.pkl"
    if cache.exists() and (datetime.now().timestamp() - cache.stat().st_mtime) < 24 * 3600:
        log.info("Loading cached dated bars")
        with open(cache, "rb") as f:
            return pickle.load(f)

    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    from alpaca.data.enums import Adjustment
    import os

    client = StockHistoricalDataClient(
        os.getenv("ALPACA_API_KEY") or os.getenv("APCA_API_KEY_ID"),
        os.getenv("ALPACA_SECRET_KEY") or os.getenv("APCA_API_SECRET_KEY"),
    )
    start = datetime.now() - timedelta(days=days)
    out: dict = {}
    CHUNK = 50

    def fetch(chunk):
        if not chunk:
            return
        try:
            bars = client.get_stock_bars(StockBarsRequest(
                symbol_or_symbols=chunk, timeframe=TimeFrame.Day, start=start,
                adjustment=Adjustment.ALL,  # split+dividend adjusted (raw splits = fake -95% crashes)
            ))
        except Exception:
            if len(chunk) == 1:
                return
            mid = len(chunk) // 2
            fetch(chunk[:mid]); fetch(chunk[mid:])
            return
        for sym in chunk:
            if sym in bars.data and bars[sym]:
                out[sym] = {
                    "dates": [b.timestamp.date() for b in bars[sym]],
                    "close": [b.close for b in bars[sym]],
                    "high": [b.high for b in bars[sym]],
                    "low": [b.low for b in bars[sym]],
                    "volume": [b.volume for b in bars[sym]],
                }

    for i in range(0, len(symbols), CHUNK):
        fetch(symbols[i:i + CHUNK])
        log.info("  fetched %d/%d", min(i + CHUNK, len(symbols)), len(symbols))

    with open(cache, "wb") as f:
        pickle.dump(out, f)
    return out


def run_backtest(months: int = 24, rebalance_days: int = 5,
                 trail_activation_pct: float = TRAIL_ACTIVATION_PCT,
                 trail_pct: float = TRAIL_PCT,
                 use_trail: bool = True,
                 end_date: str = None) -> dict:
    universe = get_universe()
    sectors = dict(universe)
    symbols = list(universe.keys()) + ["SPY"]
    sectors["SPY"] = "Benchmark"

    lookback_days = months * 31 + 420  # backtest window + ~14mo for MA200/RS
    dated = _fetch_dated(symbols, days=lookback_days)
    if "SPY" not in dated:
        raise RuntimeError("SPY bars unavailable — cannot benchmark")

    # Master calendar from SPY
    master = pd.DatetimeIndex(pd.to_datetime(dated["SPY"]["dates"]))
    tickers = [s for s in dated if s != "SPY"]

    def series(sym, field):
        s = pd.Series(dated[sym][field], index=pd.to_datetime(dated[sym]["dates"]))
        return s[~s.index.duplicated()].reindex(master)

    close = pd.DataFrame({s: series(s, "close") for s in tickers})
    high = pd.DataFrame({s: series(s, "high") for s in tickers})
    low = pd.DataFrame({s: series(s, "low") for s in tickers})
    vol = pd.DataFrame({s: series(s, "volume") for s in tickers})
    spy = pd.Series(dated["SPY"]["close"], index=pd.to_datetime(dated["SPY"]["dates"])).reindex(master)

    # Hard cutoff: truncate everything to on/before end_date for a clean
    # out-of-sample window (e.g. end 2023-12-31 to exclude the trail-decision era)
    if end_date:
        keep = master <= pd.Timestamp(end_date)
        master = master[keep]
        close, high, low, vol = close[keep], high[keep], low[keep], vol[keep]
        spy = spy[keep]
        log.info("Truncated to <= %s", end_date)

    log.info("Aligned %d tickers over %d trading days (%s → %s)",
             len(tickers), len(master), master[0].date(), master[-1].date())

    # ── Vectorized point-in-time features ─────────────────────────────────
    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()
    hi252 = close.rolling(252, min_periods=200).max()
    volavg50 = vol.rolling(50).mean()
    dollar_vol = volavg50 * close
    dist52 = (hi252 - close) / hi252
    vol_ratio = vol / volavg50

    # Recent accumulation: up-close on >=1.5x avg vol within last N sessions
    up_day = close > close.shift(1)
    vol_spike = vol >= ACCUM_VOL_MULT * volavg50
    accum_day = up_day & vol_spike
    accum_recent = accum_day.rolling(ACCUM_LOOKBACK).max().fillna(0).astype(bool)

    # IBD weighted RS-raw, then cross-sectional percentile per day
    rs_raw = (
        0.40 * (close / close.shift(63)) +
        0.20 * (close / close.shift(126)) +
        0.20 * (close / close.shift(189)) +
        0.20 * (close / close.shift(252))
    )
    rs_pct = rs_raw.rank(axis=1, pct=True) * 100  # 0-100 across universe per day

    # RSI(14) Wilder, vectorized
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)

    # ATR(14) for stops/targets
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()]).groupby(level=0).max()
    tr = tr.reindex(close.index)
    atr = tr.rolling(14).mean()

    spy_ma200 = spy.rolling(200).mean()
    vix = _fetch_vix_history().reindex(master).ffill()

    # ── Walk forward ──────────────────────────────────────────────────────
    start_idx = max(252, len(master) - months * 21)  # ~21 trading days/month
    equity = START_EQUITY
    cash = START_EQUITY
    positions: dict = {}  # ticker -> {qty, entry, stop, target, peak, entry_idx}
    equity_curve = []
    trades = []

    def sector_counts():
        c = {}
        for t in positions:
            sec = sectors.get(t, "Unknown")
            c[sec] = c.get(sec, 0) + 1
        return c

    for i in range(start_idx, len(master)):
        date = master[i]
        px = close.iloc[i]

        # 1) EXITS (checked daily, using intraday high/low touch)
        for tkr in list(positions.keys()):
            p = positions[tkr]
            day_high = high.iat[i, close.columns.get_loc(tkr)]
            day_low = low.iat[i, close.columns.get_loc(tkr)]
            cur = px[tkr]
            if pd.isna(cur):
                continue
            p["peak"] = max(p["peak"], day_high if not pd.isna(day_high) else cur)
            armed = use_trail and p["peak"] >= p["entry"] * (1 + trail_activation_pct / 100)
            trail = p["peak"] * (1 - trail_pct / 100) if armed else None

            exit_price = reason = None
            if not pd.isna(day_low) and day_low <= p["stop"]:
                exit_price, reason = p["stop"], "STOP"
            elif not pd.isna(day_high) and day_high >= p["target"]:
                exit_price, reason = p["target"], "TARGET"
            elif trail is not None and not pd.isna(day_low) and day_low <= trail:
                exit_price, reason = trail, "TRAIL"
            elif (i - p["entry_idx"]) >= TIME_EXIT_DAYS:
                exit_price, reason = cur, "TIME"

            if exit_price:
                cash += p["qty"] * exit_price
                pnl_pct = (exit_price - p["entry"]) / p["entry"] * 100
                trades.append({"ticker": tkr, "pnl_pct": pnl_pct, "reason": reason,
                               "bars_held": i - p["entry_idx"]})
                del positions[tkr]

        # 2) ENTRIES (weekly rebalance)
        if (i - start_idx) % rebalance_days == 0 and len(positions) < MAX_OPEN:
            mkt_ok = bool(spy.iat[i] > spy_ma200.iat[i]) if not pd.isna(spy_ma200.iat[i]) else True
            vix_val = vix.iat[i] if i < len(vix) and not pd.isna(vix.iat[i]) else None
            vol_ok = (10 <= vix_val <= 30) if vix_val is not None else True

            if mkt_ok and vol_ok:
                # Build candidate list via the LIVE template function
                cands = []
                for tkr in tickers:
                    if tkr in positions or pd.isna(px[tkr]):
                        continue
                    if pd.isna(ma200.iat[i, close.columns.get_loc(tkr)]):
                        continue
                    j = close.columns.get_loc(tkr)
                    price = px[tkr]
                    if price < MIN_PRICE or pd.isna(dollar_vol.iat[i, j]) or dollar_vol.iat[i, j] < MIN_DOLLAR_VOLUME:
                        continue
                    rsi_val = rsi.iat[i, j]
                    res = validate_trend_template(
                        tkr, price,
                        ma20.iat[i, j], ma50.iat[i, j], ma200.iat[i, j],
                        int(rs_pct.iat[i, j]) if not pd.isna(rs_pct.iat[i, j]) else 0,
                        dist52.iat[i, j] if not pd.isna(dist52.iat[i, j]) else 1.0,
                        vol_ratio.iat[i, j] if not pd.isna(vol_ratio.iat[i, j]) else None,
                        closes=None,  # pass RSI directly below via accumulation-style override
                        accumulation_signal=bool(accum_recent.iat[i, j]),
                        market_uptrend=mkt_ok,
                        volatility_ok=vol_ok,
                    )
                    # RSI check (template skips it when closes=None) — apply here to match live
                    rsi_ok = (not pd.isna(rsi_val)) and 50 <= rsi_val <= 80
                    if res["checks"].get("ma_alignment") and res["checks"].get("rs_over_70") \
                       and res["checks"].get("within_25_52w") and res["checks"].get("volume_confirmed") \
                       and rsi_ok:
                        cands.append((tkr, rs_pct.iat[i, j]))

                cands.sort(key=lambda c: c[1], reverse=True)
                sc = sector_counts()
                for tkr, _rs in cands:
                    if len(positions) >= MAX_OPEN:
                        break
                    sec = sectors.get(tkr, "Unknown")
                    if sc.get(sec, 0) >= MAX_PER_SECTOR:
                        continue
                    j = close.columns.get_loc(tkr)
                    price = px[tkr]
                    a = atr.iat[i, j]
                    if pd.isna(a) or a <= 0:
                        continue
                    stop = price - ATR_STOP_MULT * a
                    target = price + ATR_TARGET_MULT * a
                    if stop <= 0 or stop >= price:
                        continue
                    risk_qty = int((equity * MAX_RISK_PCT / 100) / (price - stop))
                    cap_qty = int((equity * MAX_POSITION_PCT / 100) / price)
                    qty = min(risk_qty, cap_qty)
                    if qty < 1 or qty * price > cash:
                        continue
                    cash -= qty * price
                    positions[tkr] = {"qty": qty, "entry": price, "stop": stop,
                                      "target": target, "peak": price, "entry_idx": i}
                    sc[sec] = sc.get(sec, 0) + 1

        # 3) mark-to-market equity
        mv = sum(p["qty"] * px[t] for t, p in positions.items() if not pd.isna(px[t]))
        equity = cash + mv
        equity_curve.append((date, equity))

    return _report(equity_curve, trades, spy, master, start_idx, months)


def _report(equity_curve, trades, spy, master, start_idx, months) -> dict:
    eq = pd.Series({d: v for d, v in equity_curve})
    ret = eq.iloc[-1] / eq.iloc[0] - 1
    days = (eq.index[-1] - eq.index[0]).days or 1
    cagr = (eq.iloc[-1] / eq.iloc[0]) ** (365 / days) - 1

    daily = eq.pct_change().dropna()
    sharpe = (daily.mean() / daily.std() * np.sqrt(252)) if daily.std() > 0 else 0
    roll_max = eq.cummax()
    max_dd = ((eq - roll_max) / roll_max).min() * 100

    spy_win = spy.iloc[start_idx:]
    spy_ret = spy_win.iloc[-1] / spy_win.iloc[0] - 1
    spy_daily = spy_win.pct_change().dropna()
    spy_sharpe = (spy_daily.mean() / spy_daily.std() * np.sqrt(252)) if spy_daily.std() > 0 else 0
    spy_dd = ((spy_win - spy_win.cummax()) / spy_win.cummax()).min() * 100

    wins = [t for t in trades if t["pnl_pct"] > 0]
    losses = [t for t in trades if t["pnl_pct"] <= 0]
    win_rate = len(wins) / len(trades) * 100 if trades else 0
    avg_win = np.mean([t["pnl_pct"] for t in wins]) if wins else 0
    avg_loss = np.mean([t["pnl_pct"] for t in losses]) if losses else 0
    gross_w = sum(t["pnl_pct"] for t in wins)
    gross_l = abs(sum(t["pnl_pct"] for t in losses))
    pf = gross_w / gross_l if gross_l > 0 else float("inf")
    avg_hold = np.mean([t["bars_held"] for t in trades]) if trades else 0

    print("\n" + "=" * 64)
    print(f"  SCREEN BACKTEST vs SPY  ({months} months, {len(master)-start_idx} trading days)")
    print("=" * 64)
    print(f"{'Metric':<22}{'SCREEN':>14}{'SPY (B&H)':>14}")
    print("-" * 64)
    print(f"{'Total return':<22}{ret*100:>13.1f}%{spy_ret*100:>13.1f}%")
    print(f"{'CAGR':<22}{cagr*100:>13.1f}%{((spy_win.iloc[-1]/spy_win.iloc[0])**(365/days)-1)*100:>13.1f}%")
    print(f"{'Sharpe':<22}{sharpe:>14.2f}{spy_sharpe:>14.2f}")
    print(f"{'Max drawdown':<22}{max_dd:>13.1f}%{spy_dd:>13.1f}%")
    print("-" * 64)
    print(f"{'Trades':<22}{len(trades):>14}")
    print(f"{'Win rate':<22}{win_rate:>13.1f}%")
    print(f"{'Avg win':<22}{avg_win:>13.1f}%")
    print(f"{'Avg loss':<22}{avg_loss:>13.1f}%")
    print(f"{'Profit factor':<22}{pf:>14.2f}")
    print(f"{'Avg hold (days)':<22}{avg_hold:>14.0f}")
    print("=" * 64)
    verdict = "BEATS" if ret > spy_ret else "LAGS"
    print(f"  VERDICT: screen {verdict} SPY by {abs(ret-spy_ret)*100:.1f} pts "
          f"(DD {max_dd:.0f}% vs {spy_dd:.0f}%)")
    print("=" * 64)
    print("  CAVEATS: survivorship (today's S&P 500 over history) inflates results;")
    print("  thin sample; regime-conditional. This is screen-vs-SPY, not vs Kavout.")
    print("=" * 64 + "\n")

    return {"return": ret, "spy_return": spy_ret, "sharpe": sharpe, "max_dd": max_dd,
            "trades": len(trades), "win_rate": win_rate, "profit_factor": pf,
            "trade_pnls": [t["pnl_pct"] for t in trades],
            "equity_curve": list(eq.items()), "spy_window": list(spy_win.items())}


def monte_carlo(trade_pnls, n_sims: int = 5000, seed: int = 42) -> dict:
    """
    Bootstrap the trade returns to test whether the EDGE is robust or luck.
    Resamples trades WITH replacement n_sims times. We report per-trade
    EXPECTANCY (mean return per trade) with a confidence interval and the
    probability the edge is positive — NOT a compounded total return, because
    positions run concurrently (≤5 at once) so sequential compounding would
    massively overstate the outcome. Expectancy is the honest, size-agnostic
    measure of whether there's a real edge.
    """
    pnls = np.array(trade_pnls)  # in %
    n = len(pnls)
    if n < 10:
        print("\n  Monte Carlo skipped — need >=10 trades.\n")
        return {}
    rng = np.random.default_rng(seed)
    means, path_dds = [], []
    for _ in range(n_sims):
        sample = rng.choice(pnls, size=n, replace=True)
        means.append(sample.mean())
        # Equal-weight equity path (each trade = one unit) for a drawdown read
        equity = np.cumprod(1 + sample / 100.0)
        peak = np.maximum.accumulate(equity)
        path_dds.append(((equity - peak) / peak).min() * 100)
    means, path_dds = np.array(means), np.array(path_dds)
    out = {
        "exp_p5": np.percentile(means, 5), "exp_p50": np.percentile(means, 50),
        "exp_p95": np.percentile(means, 95),
        "prob_edge_positive": (means > 0).mean() * 100,
    }
    print("\n" + "=" * 64)
    print(f"  MONTE CARLO — {n_sims} bootstraps of {n} trades")
    print("=" * 64)
    print(f"  Expectancy per trade:  p5 {out['exp_p5']:+.2f}%   "
          f"median {out['exp_p50']:+.2f}%   p95 {out['exp_p95']:+.2f}%")
    print(f"  Probability edge is positive: {out['prob_edge_positive']:.0f}%")
    print("  (Edge is real only if the p5 expectancy stays clearly positive.)")
    print("=" * 64 + "\n")
    return out


def walk_forward(equity_curve, spy_window) -> dict:
    """
    Per-calendar-year consistency check (the meaningful form of walk-forward for
    a PARAMETER-FREE strategy — there's nothing to re-optimize, so what matters
    is whether the edge shows up period after period, not in one lucky stretch).
    """
    # Build clean, chronologically-sorted series with proper DatetimeIndex
    eq = pd.Series(dict(equity_curve))
    eq.index = pd.to_datetime(eq.index)
    eq = eq[~eq.index.duplicated()].sort_index().dropna()
    spy = pd.Series(dict(spy_window))
    spy.index = pd.to_datetime(spy.index)
    spy = spy[~spy.index.duplicated()].sort_index().reindex(eq.index).ffill()
    print("\n" + "=" * 64)
    print("  WALK-FORWARD — return by calendar year (out-of-sample by period)")
    print("=" * 64)
    print(f"  {'Year':<8}{'SCREEN':>12}{'SPY':>12}{'Edge':>12}{'':>6}")
    print("-" * 64)
    wins = 0
    rows = {}
    for y in sorted(eq.index.year.unique()):
        seg = eq[eq.index.year == y]
        sseg = spy[spy.index.year == y]
        if len(seg) < 2 or len(sseg) < 2:
            continue
        scr = (seg.iloc[-1] / seg.iloc[0] - 1) * 100
        spr = (sseg.iloc[-1] / sseg.iloc[0] - 1) * 100
        flag = "✓" if scr > spr else " "
        wins += scr > spr
        rows[y] = (scr, spr)
        print(f"  {y:<8}{scr:>11.1f}%{spr:>11.1f}%{scr-spr:>+11.1f}%{flag:>4}")
    print("-" * 64)
    print(f"  Screen beat SPY in {wins}/{len(rows)} years")
    print("=" * 64 + "\n")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=24)
    ap.add_argument("--rebalance-days", type=int, default=5)
    # Default OFF to match the live bot (USE_TRAILING_STOP=False in minervini_bot).
    # --trail re-enables the tight 5%/3% trail for comparison.
    ap.add_argument("--trail", action="store_true", help="enable tight trailing stop (default: off, matches live)")
    ap.add_argument("--end-date", type=str, default=None,
                    help="hard cutoff YYYY-MM-DD for out-of-sample testing (e.g. 2023-12-31)")
    ap.add_argument("--validate", action="store_true",
                    help="also run walk-forward (per-year) + Monte Carlo bootstrap")
    args = ap.parse_args()
    res = run_backtest(months=args.months, rebalance_days=args.rebalance_days,
                       use_trail=args.trail, end_date=args.end_date)
    if args.validate:
        walk_forward(res["equity_curve"], res["spy_window"])
        monte_carlo(res["trade_pnls"])
