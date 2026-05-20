"""
position_manager.py — Risk-Based Position Sizing (Enhanced)
────────────────────────────────────────────────────────────

Calculates position size based on:
- Account equity and max risk per trade (1.25%)
- Stop loss distance (ATR-based instead of fixed %)
- Dynamic take profit levels (based on volatility)
"""

from typing import Optional, Dict, Tuple, List
from indicators import calculate_atr


def calculate_atr_stop_loss(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    entry_price: float,
    atr_multiplier: float = 2.0,
) -> Optional[float]:
    """
    Calculate stop loss using Average True Range.
    stop_loss = entry_price - (atr_multiplier * ATR)

    Higher ATR = more volatile stock = wider stop
    Lower ATR = stable stock = tighter stop
    """
    atr = calculate_atr(highs, lows, closes, period=14)
    if atr is None:
        return None

    stop_loss = entry_price - (atr_multiplier * atr)
    return max(stop_loss, entry_price * 0.85)  # Ensure not more than 15% below entry


def calculate_position_size(
    account_equity: float,
    entry_price: float,
    stop_loss_price: float,
    max_risk_pct: float = 1.25,
) -> int:
    """
    Calculate position size based on risk-per-trade.

    Risk = account_equity * max_risk_pct / 100
    Position size = Risk / (entry_price - stop_loss_price)

    Example: $100k account, entry $50, stop $46.50
    - Risk: $1,250 (1.25% of $100k)
    - Stop distance: $3.50
    - Shares: 357
    """
    if entry_price <= stop_loss_price or account_equity <= 0:
        return 0

    risk_dollars = account_equity * (max_risk_pct / 100)
    stop_distance = entry_price - stop_loss_price

    if stop_distance <= 0:
        return 0

    shares = int(risk_dollars / stop_distance)
    return max(shares, 1)


def calculate_take_profit_price(
    entry_price: float,
    atr: Optional[float] = None,
    profit_target_pct: float = 20.0,
) -> float:
    """
    Calculate take profit level.

    Static: entry_price * (1 + profit_target_pct / 100)
    Dynamic: entry_price + (4.0 * ATR) if ATR provided

    Higher volatility = wider target window
    """
    if atr is not None and atr > 0:
        return entry_price + (4.0 * atr)

    return entry_price * (1 + profit_target_pct / 100)


def validate_position_limits(
    account_equity: float,
    position_value: float,
    num_open_positions: int,
    max_positions: int = 5,
    max_position_pct: float = 20.0,
) -> Tuple[bool, str]:
    """
    Validate position limits before opening trade.

    Returns: (is_valid, reason_if_invalid)
    """
    # Check max positions
    if num_open_positions >= max_positions:
        return False, f"Max {max_positions} open positions reached"

    # Check max position size (% of account)
    position_pct = (position_value / account_equity) * 100
    if position_pct > max_position_pct:
        return False, f"Position {position_pct:.1f}% exceeds {max_position_pct}% limit"

    return True, ""
