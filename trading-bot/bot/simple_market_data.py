"""
Simple market data fetcher using only requests library.
No yfinance, no gevent, no dependency conflicts.
Falls back to cached prices if APIs fail.
"""

import requests
import json
from typing import Optional, Tuple
from datetime import datetime, timedelta
import os

# Last known good prices (fallback cache)
CACHE = {
    'GOOGL': {'price': 175.50, 'date': '2026-05-19'},
    'MSFT': {'price': 424.50, 'date': '2026-05-19'},
    'AAPL': {'price': 227.10, 'date': '2026-05-19'},
    'AMZN': {'price': 195.80, 'date': '2026-05-19'},
    'TSM': {'price': 140.20, 'date': '2026-05-19'},
    'NVDA': {'price': 875.50, 'date': '2026-05-19'},
    'SPY': {'price': 559.25, 'date': '2026-05-19'},
}

def get_price_simple(ticker: str) -> Optional[float]:
    """Get latest price using IEX Cloud free tier (no key required for limited calls)."""
    try:
        url = f"https://api.example.com/stock/{ticker}/quote"
        resp = requests.get(url, timeout=5)
        
        # Try a different free endpoint
        url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        params = {'modules': 'price'}
        resp = requests.get(url, params=params, timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            if 'quoteSummary' in data and 'result' in data['quoteSummary']:
                price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']
                return float(price)
    except Exception:
        pass
    
    # Fallback to cache
    if ticker in CACHE:
        return float(CACHE[ticker]['price'])
    
    return None

def get_bars_simple(ticker: str, days: int = 60) -> Optional[Tuple]:
    """
    Generate synthetic but realistic bars based on current price.
    Simulates a trending stock for testing.
    """
    current_price = get_price_simple(ticker) or CACHE.get(ticker, {}).get('price', 100.0)
    
    # Generate synthetic daily bars
    closes = []
    highs = []
    lows = []
    
    price = current_price * 0.85  # Start lower
    for i in range(days):
        # Random walk up with trend
        change = (i / days) * 0.3  # Trend up
        noise = ((hash(f"{ticker}_{i}") % 100) - 50) / 1000  # Pseudo-random
        price *= (1.0 + change/days + noise)
        
        high = price * 1.02
        low = price * 0.98
        
        closes.append(price)
        highs.append(high)
        lows.append(low)
    
    return (closes, highs, lows)

# Monkey-patch for data_fetcher fallback
def yfinance_fallback_download(symbol: str, period: str = '60d', progress: bool = False):
    """Fake yfinance-compatible data."""
    import pandas as pd
    
    days = int(period[0:-1]) if period[-1] == 'd' else 60
    closes, highs, lows = get_bars_simple(symbol, days)
    
    df = pd.DataFrame({
        'Close': closes,
        'High': highs,
        'Low': lows,
        'Open': [c * 0.99 for c in closes],
        'Volume': [1000000] * len(closes),
    })
    
    return df
