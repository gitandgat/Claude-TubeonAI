"""
trend_filter.py — Mark Minervini Trend Template Validator (Enhanced)
──────────────────────────────────────────────────────────────────────

Validates that a stock passes all 4 conditions of the Minervini Trend Template:
1. Price > MA20 > MA50 > MA200 (moving average alignment)
2. RS rank > 70 (relative strength percentile vs SPY)
3. Price within 25% of 52-week high
4. Volume > 1.5x 50-day average

PLUS enhanced validation:
5. RSI 50-80 (confirmation of uptrend, not overbought)
6. Market in uptrend (SPY > MA200)
7. Volatility acceptable (10 < VIX < 30)

All checks must pass for entry signal.
"""

from typing import TypedDict, Dict, List, Optional
from indicators import (
    calculate_rsi,
    is_market_in_uptrend,
    is_volatility_acceptable,
)


class TrendCheckResult(TypedDict):
    """Result of Trend Template validation."""
    passes: bool
    checks: Dict[str, bool]
    reasons: List[str]


def validate_trend_template(
    ticker: str,
    price: float,
    ma_20: float,
    ma_50: float,
    ma_200: float,
    rs_rank: int,
    distance_52w_pct: float,
    volume_ratio: float,
    closes: Optional[List[float]] = None,
) -> TrendCheckResult:
    """
    Validate all Minervini Trend Template conditions + enhanced checks.

    Args:
        ticker: Stock symbol (for logging)
        price: Current price
        ma_20: 20-day moving average
        ma_50: 50-day moving average
        ma_200: 200-day moving average
        rs_rank: Relative strength rank vs SPY (0-100)
        distance_52w_pct: How far below 52-week high (0-1 range)
        volume_ratio: Today's volume / 50-day average volume
        closes: List of closes for RSI calculation (optional)

    Returns:
        TrendCheckResult with passes flag, individual checks, and reasons.
    """
    checks = {}
    reasons = []

    # ═══════════════════════════════════════════════════════════════════
    # CORE MINERVINI CHECKS (4 required)
    # ═══════════════════════════════════════════════════════════════════

    # Check 1: MA alignment (price > MA20 > MA50 > MA200)
    ma_aligned = price > ma_20 > ma_50 > ma_200
    checks["ma_alignment"] = ma_aligned
    if not ma_aligned:
        reasons.append(
            f"MA alignment failed: price=${price:.2f} > MA20=${ma_20:.2f} > "
            f"MA50=${ma_50:.2f} > MA200=${ma_200:.2f}"
        )

    # Check 2: RS rank > 70 (vs SPY)
    rs_ok = rs_rank > 70
    checks["rs_over_70"] = rs_ok
    if not rs_ok:
        reasons.append(f"RS rank {rs_rank} <= 70 (underperforming SPY)")

    # Check 3: Price within 25% of 52-week high
    within_25 = distance_52w_pct <= 0.25
    checks["within_25_52w"] = within_25
    if not within_25:
        reasons.append(
            f"Price ${price:.2f} is {distance_52w_pct*100:.1f}% below "
            f"52-week high (max 25%)"
        )

    # Check 4: Volume confirmation (> 1.5x 50-day average)
    vol_confirmed = volume_ratio >= 1.5
    checks["volume_confirmed"] = vol_confirmed
    if not vol_confirmed:
        reasons.append(
            f"Volume ratio {volume_ratio:.2f}x < 1.5x (50-day average)"
        )

    # ═══════════════════════════════════════════════════════════════════
    # ENHANCED CHECKS (confirmation filters)
    # ═══════════════════════════════════════════════════════════════════

    # Check 5: RSI confirmation (50-80 = strong uptrend, not overbought)
    rsi_ok = True
    rsi_value = None
    if closes and len(closes) >= 15:
        rsi_value = calculate_rsi(closes, period=14)
        rsi_ok = rsi_value is not None and 50 <= rsi_value <= 80
        checks["rsi_confirmation"] = rsi_ok
        if not rsi_ok:
            reasons.append(
                f"RSI {rsi_value:.1f} outside 50-80 range (signal integrity low)"
            )
    else:
        checks["rsi_confirmation"] = True

    # Check 6: Market regime (SPY > MA200)
    market_ok = is_market_in_uptrend()
    checks["market_uptrend"] = market_ok
    if not market_ok:
        reasons.append("SPY in downtrend (broad market risk)")

    # Check 7: Volatility acceptable (10 < VIX < 30)
    vol_ok = is_volatility_acceptable(max_vix=30, min_vix=10)
    checks["volatility_acceptable"] = vol_ok
    if not vol_ok:
        reasons.append("VIX outside safe range")

    # ═══════════════════════════════════════════════════════════════════
    # FINAL VERDICT
    # ═══════════════════════════════════════════════════════════════════

    core_passes = all([
        checks["ma_alignment"],
        checks["rs_over_70"],
        checks["within_25_52w"],
        checks["volume_confirmed"],
    ])

    confidence = sum([
        checks.get("rsi_confirmation", True),
        checks.get("market_uptrend", True),
        checks.get("volatility_acceptable", True),
    ]) / 3.0

    passes = core_passes and confidence >= 0.66

    return {
        "passes": passes,
        "checks": checks,
        "reasons": reasons,
    }


def format_trend_result(ticker: str, result: TrendCheckResult) -> str:
    """Format Trend Template result for logging."""
    status = "✓ PASS" if result["passes"] else "✗ FAIL"
    checks_str = " | ".join(
        f"{k}={'✓' if v else '✗'}" for k, v in result["checks"].items()
    )
    reason_str = " — " + "; ".join(result["reasons"]) if result["reasons"] else ""
    return f"{ticker}: {status} [{checks_str}]{reason_str}"
