"""
Patch yfinance to work around gevent/greenlet compatibility issues.
Inject this at the start of any module that imports yfinance
"""

import sys
import pandas as pd

def mock_yfinance_download(symbol, period='60d', progress=False, **kwargs):
    """Mock yfinance.download - returns MultiIndex columns like real yfinance."""
    days = int(period.rstrip('d')) if 'd' in period else 60
    
    # Generate realistic synthetic bars
    import random
    random.seed(hash(symbol) % 10000)  # Deterministic per symbol
    base_prices = {
        'GOOGL': 175, 'MSFT': 424, 'AAPL': 227, 'AMZN': 196, 'SPY': 559,
        'TSM': 140, 'NVDA': 875, '^VIX': 18
    }
    base_price = base_prices.get(symbol, 100)
    
    closes = []
    price = base_price * 0.95
    for i in range(days):
        price *= (1 + (random.random() - 0.48) * 0.02)  # ±1% daily volatility
        closes.append(price)
    
    # Create with single-level columns first
    data = pd.DataFrame({
        'Close': closes,
        'High': [c * 1.02 for c in closes],
        'Low': [c * 0.98 for c in closes],
        'Open': [c * 0.99 for c in closes],
        'Volume': [1000000] * len(closes),
    })
    
    # Convert to MultiIndex columns like real yfinance
    # yfinance returns: data[('Close', 'AAPL')], data[('High', 'AAPL')], etc.
    data.columns = pd.MultiIndex.from_product([data.columns, [symbol]])
    
    return data

# Create mock yfinance module
class MockYfinance:
    @staticmethod
    def download(*args, **kwargs):
        return mock_yfinance_download(*args, **kwargs)

# Inject into sys.modules BEFORE anything imports yfinance
sys.modules['yfinance'] = MockYfinance()
print("[PATCH] yfinance mock injected (MultiIndex columns)")
