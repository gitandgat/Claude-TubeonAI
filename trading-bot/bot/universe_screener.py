"""
universe_screener.py — Full-universe Minervini screen with true RS ranking.
──────────────────────────────────────────────────────────────────────────

Screens the entire S&P 500 each day instead of a 14-stock watchlist:

1. Batch-fetch ~300 days of real bars for every name (Alpaca, ~10 calls)
2. Compute an IBD-style Relative Strength rating — weighted price performance
   (40% most-recent quarter, 20% each of the prior three), then PERCENTILE-rank
   across the whole universe. RS 90 = top 10% of the market. This is the
   authentic Minervini RS, not a rough SPY-pairwise approximation.
3. Apply a liquidity floor (price ≥ $10, ≥ $20M average daily dollar volume)
4. Run the Minervini Trend Template on each survivor
5. Return passers, richest-RS first, tagged with sector for downstream
   diversification capping

Kavout High/Outperform names (if provided) are tagged as a quality overlay
but no longer limit the universe.
"""

import logging
from typing import Dict, List, Optional

from data_fetcher import alpaca_get_bars_batch
from trend_filter import validate_trend_template
from indicators import is_market_in_uptrend, is_volatility_acceptable

log = logging.getLogger(__name__)

# Liquidity floor — keep the bot in names it can actually trade cleanly
MIN_PRICE = 10.0
MIN_DOLLAR_VOLUME = 20_000_000  # 50-day avg close × volume
MIN_BARS_FOR_RS = 200  # ~9.5 months; need history for a meaningful RS

# Accumulation detection: an up-close on >=1.5x average volume within this many
# recent sessions = institutions buying. Far more meaningful than requiring the
# screen to land on the exact breakout day.
ACCUMULATION_LOOKBACK = 10
ACCUMULATION_VOLUME_MULT = 1.5

# IBD weighted-performance windows: (trading-day lookback, weight)
_RS_WINDOWS = [(63, 0.40), (126, 0.20), (189, 0.20), (252, 0.20)]


def _weighted_rs_raw(closes: List[float]) -> Optional[float]:
    """IBD-style weighted price-performance ratio (higher = stronger)."""
    n = len(closes)
    current = closes[-1]
    numerator, weight_sum = 0.0, 0.0
    for lookback, weight in _RS_WINDOWS:
        if n > lookback:
            past = closes[-lookback - 1]
            if past > 0:
                numerator += weight * (current / past)
                weight_sum += weight
    if weight_sum == 0:
        return None
    return numerator / weight_sum


def _percentile_ranks(raw_scores: Dict[str, float]) -> Dict[str, int]:
    """Map raw RS scores to 1-99 percentile ranks across the universe."""
    if not raw_scores:
        return {}
    ordered = sorted(raw_scores.items(), key=lambda kv: kv[1])
    total = len(ordered)
    ranks: Dict[str, int] = {}
    for i, (ticker, _) in enumerate(ordered):
        pct = (i + 0.5) / total * 100  # midpoint percentile, 0-100
        ranks[ticker] = max(1, min(99, round(pct)))
    return ranks


def _has_recent_accumulation(closes: List[float], volumes: List[float]) -> bool:
    """True if any of the last N sessions was an up-close on >=1.5x avg volume."""
    if len(closes) < 51:
        return False
    avg_vol_50 = sum(volumes[-50:]) / 50
    if avg_vol_50 <= 0:
        return False
    for i in range(1, ACCUMULATION_LOOKBACK + 1):
        if closes[-i] > closes[-i - 1] and volumes[-i] >= ACCUMULATION_VOLUME_MULT * avg_vol_50:
            return True
    return False


def _metrics_from_bars(bars: dict) -> Optional[dict]:
    """Compute MA20/50/200, 52w distance, volume ratio, dollar volume."""
    closes, vols = bars["closes"], bars["volumes"]
    n = len(closes)
    if n < 60:
        return None
    ma_20 = sum(closes[-20:]) / 20
    ma_50 = sum(closes[-50:]) / 50
    ma_200 = sum(closes[-200:]) / 200 if n >= 200 else sum(closes) / n
    hi_52w = max(closes[-252:]) if n >= 252 else max(closes)
    avg_vol_50 = sum(vols[-50:]) / 50
    return {
        "price": closes[-1],
        "ma_20": ma_20,
        "ma_50": ma_50,
        "ma_200": ma_200,
        "distance_52w": (hi_52w - closes[-1]) / hi_52w if hi_52w > 0 else 1.0,
        "volume_ratio": vols[-1] / avg_vol_50 if avg_vol_50 > 0 else None,
        "dollar_volume": avg_vol_50 * closes[-1],
        "bars_used": n,
    }


def screen_universe(
    universe: Dict[str, str],
    kavout_ranks: Optional[dict] = None,
) -> List[dict]:
    """
    Screen the universe and return Trend-Template passers, richest-RS first.

    Args:
        universe: {ticker: gics_sector}
        kavout_ranks: optional {ticker: {...}} for the quality overlay tag

    Returns:
        List of candidate dicts (passes==True), each with price, MAs,
        distance_52w, volume_ratio, rs_rank (percentile), sector,
        dollar_volume, closes, and kavout_endorsed.
    """
    symbols = list(universe.keys())
    log.info("Screening universe: %d symbols", len(symbols))

    bars_by_symbol = alpaca_get_bars_batch(symbols, days=300)
    if not bars_by_symbol:
        log.error("No bar data returned — cannot screen universe")
        return []

    # Pass 1: compute metrics + raw RS for every name with enough history
    metrics_by_symbol: Dict[str, dict] = {}
    raw_rs: Dict[str, float] = {}
    for sym, bars in bars_by_symbol.items():
        if len(bars["closes"]) < MIN_BARS_FOR_RS:
            continue
        m = _metrics_from_bars(bars)
        if m is None:
            continue
        rs = _weighted_rs_raw(bars["closes"])
        if rs is None:
            continue
        metrics_by_symbol[sym] = m
        raw_rs[sym] = rs

    rs_ranks = _percentile_ranks(raw_rs)
    log.info("Computed RS percentile for %d symbols", len(rs_ranks))

    kavout_ranks = kavout_ranks or {}

    # Market-wide regime checks computed ONCE (not per stock — that hammered
    # the FRED/SPY endpoints 450+ times per run)
    market_uptrend = is_market_in_uptrend()
    volatility_ok = is_volatility_acceptable(max_vix=30, min_vix=10)

    # Pass 2: liquidity floor + Trend Template
    candidates: List[dict] = []
    liquidity_rejected = 0
    for sym, m in metrics_by_symbol.items():
        if m["price"] < MIN_PRICE or m["dollar_volume"] < MIN_DOLLAR_VOLUME:
            liquidity_rejected += 1
            continue

        rs_rank = rs_ranks[sym]
        bars = bars_by_symbol[sym]
        accumulation = _has_recent_accumulation(bars["closes"], bars["volumes"])
        result = validate_trend_template(
            sym,
            m["price"],
            m["ma_20"], m["ma_50"], m["ma_200"],
            rs_rank,
            m["distance_52w"],
            m["volume_ratio"],
            closes=bars["closes"],
            accumulation_signal=accumulation,
            market_uptrend=market_uptrend,
            volatility_ok=volatility_ok,
        )
        if not result["passes"]:
            continue

        kv = kavout_ranks.get(sym, {})
        candidates.append({
            "ticker": sym,
            "sector": universe.get(sym, "Unknown"),
            "price": m["price"],
            "ma_20": m["ma_20"], "ma_50": m["ma_50"], "ma_200": m["ma_200"],
            "distance_52w": m["distance_52w"],
            "volume_ratio": m["volume_ratio"],
            "rs_rank": rs_rank,
            "dollar_volume": m["dollar_volume"],
            "closes": bars["closes"],
            "highs": bars["highs"],
            "lows": bars["lows"],
            "kavout_endorsed": kv.get("rank") == "High" and kv.get("outlook") == "Outperform",
        })

    candidates.sort(key=lambda c: c["rs_rank"], reverse=True)
    log.info(
        "Screen complete: %d passed Trend Template (%d liquidity-rejected, %d screened)",
        len(candidates), liquidity_rejected, len(metrics_by_symbol),
    )
    return candidates


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    sys.path.insert(0, ".")
    from universe import get_universe

    uni = get_universe()
    passers = screen_universe(uni)
    print(f"\n{'='*70}\nTOP MINERVINI CANDIDATES (S&P 500, RS-ranked)\n{'='*70}")
    print(f"{'TICKER':8}{'SECTOR':26}{'PRICE':>9}{'RS':>5}{'52W%':>7}{'VOL':>6}  KAVOUT")
    for c in passers[:25]:
        print(f"{c['ticker']:8}{c['sector'][:24]:26}{c['price']:>9.2f}"
              f"{c['rs_rank']:>5}{c['distance_52w']*100:>6.1f}%"
              f"{(c['volume_ratio'] or 0):>5.2f}x  {'★' if c['kavout_endorsed'] else ''}")
    print(f"\nTotal passers: {len(passers)}")
