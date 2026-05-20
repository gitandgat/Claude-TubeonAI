"""
diagnose_trend.py — Debug why Trend Template validation fails
Analyzes a single stock to show which conditions fail and when.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
import os
import sys

import requests
from dotenv import load_dotenv

from trend_filter import validate_trend_template

load_dotenv()

POLYGON_BASE = "https://api.polygon.io"
POLYGON_KEY = os.getenv("MASSIVE_API_KEY")

def polygon_get(url: str, params: dict) -> Optional[Dict]:
    """GET a Polygon endpoint."""
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Polygon request failed: {e}")
        return None

def calculate_sma(closes, window: int) -> Optional[float]:
    """Calculate SMA from a list of closes."""
    if len(closes) < window:
        return None
    return sum(closes[-window:]) / window

def diagnose_ticker(ticker: str, months: int = 12):
    """Analyze why Trend Template fails for a stock."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30 * months)).strftime("%Y-%m-%d")

    print(f"\n{'='*70}")
    print(f"Diagnosing {ticker} ({start_date} to {end_date})")
    print(f"{'='*70}\n")

    # Fetch bars
    url = f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
    data = polygon_get(url, {"adjusted": "true", "apiKey": POLYGON_KEY})

    if not data or not data.get("results"):
        print(f"{ticker}: No bars found")
        return

    bars = sorted(data["results"], key=lambda x: x["t"])
    print(f"Loaded {len(bars)} bars\n")

    # Stats on failing checks
    ma_failures = 0
    rs_failures = 0
    distance_failures = 0
    volume_failures = 0
    all_pass_count = 0

    # Show first few failures
    failure_samples = []

    start_idx = max(0, len(bars) - 50)
    for i in range(start_idx, len(bars)):
        bar = bars[i]
        bar_date = datetime.fromtimestamp(bar["t"] / 1000).strftime("%Y-%m-%d")
        close = float(bar["c"])
        volume = float(bar["v"])

        closes = [float(b["c"]) for b in bars[:i+1]]
        ma_20 = calculate_sma(closes, 20)
        ma_50 = calculate_sma(closes, 50)
        ma_200 = calculate_sma(closes, 200)

        if not (ma_20 and ma_50 and ma_200):
            continue

        # 52-week high
        closes_52w = [float(b["c"]) for b in bars[max(0, i - 252):i+1]]
        h52w = max(closes_52w) if closes_52w else close
        distance_52w = (h52w - close) / h52w if h52w > 0 else 0

        # Volume ratio
        volumes_50d = [float(b["v"]) for b in bars[max(0, i-50):i+1]]
        avg_vol_50d = sum(volumes_50d) / len(volumes_50d) if volumes_50d else 1
        volume_ratio = volume / avg_vol_50d if avg_vol_50d > 0 else 0

        rs_rank = 75  # Simplified

        result = validate_trend_template(
            ticker, close, ma_20, ma_50, ma_200, rs_rank, distance_52w, volume_ratio
        )

        if result["passes"]:
            all_pass_count += 1
            print(f"✓ {bar_date}: TREND PASSES!")
            print(f"  Price: ${close:.2f}, MA20: ${ma_20:.2f}, MA50: ${ma_50:.2f}, MA200: ${ma_200:.2f}")
            print(f"  52W High: ${h52w:.2f} (distance: {distance_52w*100:.1f}%)")
            print(f"  Volume ratio: {volume_ratio:.2f}x\n")
        else:
            for reason in result["reasons"]:
                if "MA alignment" in reason:
                    ma_failures += 1
                elif "RS rank" in reason:
                    rs_failures += 1
                elif "52-week" in reason:
                    distance_failures += 1
                elif "Volume" in reason:
                    volume_failures += 1

            if len(failure_samples) < 3:
                failure_samples.append({
                    "date": bar_date,
                    "reasons": result["reasons"],
                    "close": close,
                    "ma_20": ma_20,
                    "ma_50": ma_50,
                    "ma_200": ma_200,
                    "distance_52w": distance_52w,
                    "volume_ratio": volume_ratio,
                })

    print(f"\nDiagnostics over last 50 bars:")
    print(f"  Passed all checks: {all_pass_count}")
    print(f"  MA alignment failures: {ma_failures}")
    print(f"  RS rank failures: {rs_failures}")
    print(f"  Distance from 52W high failures: {distance_failures}")
    print(f"  Volume ratio failures: {volume_failures}")

    if failure_samples:
        print(f"\nSample failures:")
        for sample in failure_samples:
            print(f"\n  {sample['date']}:")
            print(f"    Price: ${sample['close']:.2f}")
            print(f"    MAs: 20=${sample['ma_20']:.2f}, 50=${sample['ma_50']:.2f}, 200=${sample['ma_200']:.2f}")
            print(f"    Distance from 52W high: {sample['distance_52w']*100:.1f}%")
            print(f"    Volume ratio: {sample['volume_ratio']:.2f}x")
            for reason in sample['reasons']:
                print(f"    ✗ {reason}")

if __name__ == "__main__":
    ticker = "AAPL"
    months = 12

    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    if "--months" in sys.argv:
        idx = sys.argv.index("--months")
        months = int(sys.argv[idx + 1])

    diagnose_ticker(ticker, months)
