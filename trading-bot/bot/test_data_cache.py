"""
Test data cache — mock market data for testing bot logic without live APIs.
Use when live data sources are unavailable or rate-limited.
"""

from typing import Optional, Tuple
from datetime import datetime, timedelta
import random

TEST_MODE = True

# Synthetic daily bar data: (closes, highs, lows) tuples
SYNTHETIC_DATA = {
    'GOOGL': {
        'closes': [165.32, 166.15, 165.80, 167.45, 168.12, 169.05, 168.75, 170.20, 171.45, 172.10] + [172.50 + i * 0.5 for i in range(50)],
        'highs': [166.20, 167.05, 166.75, 168.40, 169.10, 170.00, 169.70, 171.20, 172.50, 173.15] + [173.50 + i * 0.5 for i in range(50)],
        'lows': [164.50, 165.40, 165.15, 166.80, 167.50, 168.20, 167.90, 169.30, 170.60, 171.25] + [171.50 + i * 0.5 for i in range(50)],
    },
    'MSFT': {
        'closes': [380.45, 381.20, 380.75, 382.10, 383.45, 384.10, 383.80, 385.30, 386.75, 388.20] + [388.50 + i * 0.4 for i in range(50)],
        'highs': [381.40, 382.15, 381.70, 383.10, 384.50, 385.10, 384.80, 386.30, 387.80, 389.30] + [389.50 + i * 0.4 for i in range(50)],
        'lows': [379.60, 380.35, 379.90, 381.25, 382.60, 383.25, 382.95, 384.40, 385.85, 387.30] + [387.50 + i * 0.4 for i in range(50)],
    },
    'AMZN': {
        'closes': [185.30, 186.10, 185.65, 187.20, 188.45, 189.10, 188.80, 190.50, 191.75, 193.20] + [193.50 + i * 0.6 for i in range(50)],
        'highs': [186.25, 187.10, 186.65, 188.25, 189.50, 190.15, 189.85, 191.60, 192.85, 194.30] + [194.50 + i * 0.6 for i in range(50)],
        'lows': [184.50, 185.30, 184.85, 186.40, 187.60, 188.25, 187.95, 189.65, 190.85, 192.25] + [192.50 + i * 0.6 for i in range(50)],
    },
    'SPY': {
        'closes': [445.50, 446.30, 445.80, 447.40, 448.75, 449.50, 449.20, 450.80, 452.15, 453.90] + [454.20 + i * 0.3 for i in range(50)],
        'highs': [446.50, 447.35, 446.85, 448.50, 449.85, 450.60, 450.30, 451.95, 453.30, 455.05] + [455.30 + i * 0.3 for i in range(50)],
        'lows': [444.70, 445.50, 445.00, 446.55, 447.85, 448.60, 448.25, 449.95, 451.25, 452.95] + [453.25 + i * 0.3 for i in range(50)],
    },
    '^VIX': {
        'closes': [18.5, 18.2, 19.1, 17.8, 18.3] + [18.0 + random.uniform(-0.5, 0.5) for _ in range(55)],
        'highs': [19.0, 18.7, 19.6, 18.3, 18.8] + [18.5 + random.uniform(0, 1.0) for _ in range(55)],
        'lows': [18.0, 17.7, 18.6, 17.3, 17.8] + [17.5 + random.uniform(-1.0, 0) for _ in range(55)],
    },
}


def fetch_previous_close_test(ticker: str) -> Optional[float]:
    """Return last close from synthetic data."""
    if ticker in SYNTHETIC_DATA:
        return SYNTHETIC_DATA[ticker]['closes'][-1]
    return None


def fetch_daily_bars_test(ticker: str, days: int = 60) -> Optional[Tuple]:
    """Return (closes, highs, lows) from synthetic data."""
    if ticker not in SYNTHETIC_DATA:
        return None

    data = SYNTHETIC_DATA[ticker]
    closes = data['closes'][-days:] if len(data['closes']) >= days else data['closes']
    highs = data['highs'][-days:] if len(data['highs']) >= days else data['highs']
    lows = data['lows'][-days:] if len(data['lows']) >= days else data['lows']

    return (closes, highs, lows)
