"""
discover_candidates.py — Discover stocks for Minervini Trend Template
──────────────────────────────────────────────────────────────────────

Finds high-quality stocks with:
- Strong relative strength (trending upward)
- Good volume
- Technical strength indicators
- Across multiple sectors

Expands ranks.json watchlist from 3 to 50+ candidates.

Usage:
    python bot/discover_candidates.py                # Discover top 50 stocks
    python bot/discover_candidates.py --top 100      # Top 100 stocks
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()

POLYGON_BASE = "https://api.polygon.io"
POLYGON_KEY = os.getenv("MASSIVE_API_KEY")
RANKS_FILE = Path(__file__).parent.parent / "ranks.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def polygon_get(url: str, params: dict) -> dict | None:
    """GET a Polygon endpoint."""
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.warning(f"Polygon request failed: {e}")
        return None


def get_all_stocks() -> List[str]:
    """Get all active US equity symbols from Polygon."""
    log.info("Fetching all active US stocks from Polygon...")

    url = f"{POLYGON_BASE}/v3/reference/tickers"
    params = {
        "market": "stocks",
        "active": "true",
        "limit": 1000,
        "apiKey": POLYGON_KEY,
    }

    all_tickers = []
    page_token = None

    while True:
        if page_token:
            params["page_token"] = page_token

        data = polygon_get(url, params)
        if not data or not data.get("results"):
            break

        all_tickers.extend([t["ticker"] for t in data["results"]])

        # Stop after 50k tickers (manageable subset)
        if len(all_tickers) >= 50000:
            break

        page_token = data.get("next_url", "").split("page_token=")[-1] if "next_url" in data else None
        if not page_token:
            break

    log.info(f"Found {len(all_tickers)} total stocks")
    return all_tickers[:10000]  # Limit to 10k for practical processing


def score_stock(ticker: str) -> float | None:
    """
    Score a stock based on Minervini-like criteria:
    - YTD performance (momentum)
    - 50-day vs 200-day MA (trend strength)
    - Volume (liquidity)

    Returns score 0-100, or None if data unavailable.
    """
    try:
        # Get latest bar for volume and price
        url = f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/prev"
        latest = polygon_get(url, {"adjusted": "true", "apiKey": POLYGON_KEY})

        if not latest or not latest.get("results"):
            return None

        latest_bar = latest["results"][0]
        latest_price = float(latest_bar.get("c", 0))
        latest_volume = float(latest_bar.get("v", 0))

        if latest_price <= 0 or latest_volume <= 0:
            return None

        # Exclude penny stocks and illiquid stocks
        if latest_price < 5 or latest_volume < 500000:
            return None

        # Get year-to-date bars
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        url = f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
        data = polygon_get(url, {"adjusted": "true", "apiKey": POLYGON_KEY})

        if not data or not data.get("results"):
            return None

        bars = data["results"]
        if len(bars) < 200:  # Not enough history
            return None

        closes = [float(b["c"]) for b in bars]

        # Calculate metrics
        price_ytd_pct = ((closes[-1] - closes[0]) / closes[0]) * 100 if closes[0] > 0 else 0

        # 50-day and 200-day averages
        ma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
        ma_200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else None

        if not ma_50 or not ma_200:
            return None

        # Price above both MAs
        price_above_50 = 1 if latest_price > ma_50 else 0
        price_above_200 = 1 if latest_price > ma_200 else 0
        ma_alignment = 1 if ma_50 > ma_200 else 0

        # Calculate 52-week high
        h52w = max([float(b["c"]) for b in bars[-252:]])
        distance_from_high = ((h52w - latest_price) / h52w) * 100

        # Score components (0-100)
        momentum_score = min(100, max(0, price_ytd_pct + 50))  # -50% to +50% → 0-100
        trend_score = (price_above_50 + price_above_200 + ma_alignment) * 33.33  # 0-100
        proximity_score = max(0, 100 - distance_from_high * 3)  # Closer to high = higher score

        # Weighted score
        score = (momentum_score * 0.3 + trend_score * 0.4 + proximity_score * 0.3)

        return score

    except Exception as e:
        return None


def discover_candidates(top_n: int = 50) -> List[str]:
    """Discover top N stocks by Minervini-like scoring."""
    log.info(f"\nDiscovering top {top_n} candidates...")

    all_stocks = get_all_stocks()
    log.info(f"Scoring {len(all_stocks)} stocks (this may take a few minutes)...")

    scored = []
    for i, ticker in enumerate(all_stocks):
        if i % 100 == 0:
            log.info(f"  Progress: {i}/{len(all_stocks)}")

        score = score_stock(ticker)
        if score is not None and score > 0:
            scored.append((ticker, score))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # Return top N
    top_candidates = [t for t, s in scored[:top_n]]
    log.info(f"\nTop {top_n} candidates by score:")
    for i, (ticker, score) in enumerate(scored[:top_n], 1):
        log.info(f"  {i:2d}. {ticker:<6} score={score:.1f}")

    return top_candidates


def update_ranks_json(new_candidates: List[str]) -> None:
    """Update ranks.json with new candidates."""
    log.info(f"\nUpdating ranks.json with {len(new_candidates)} candidates...")

    # Load existing ranks
    if RANKS_FILE.exists():
        with open(RANKS_FILE) as f:
            ranks = json.load(f)
    else:
        ranks = {}

    # Add new candidates (don't overwrite existing)
    for ticker in new_candidates:
        if ticker not in ranks:
            ranks[ticker] = {
                "rank": "Medium",
                "outlook": "Neutral",
                "tech": "HOLD",
                "rs_rank": None,
                "ma_20": None,
                "ma_50": None,
                "ma_200": None,
                "distance_52w": None,
                "volume_sma": None,
            }

    # Save updated ranks
    with open(RANKS_FILE, "w") as f:
        json.dump(ranks, f, indent=2)

    log.info(f"✓ ranks.json updated: {len(ranks)} total stocks")


if __name__ == "__main__":
    top_n = 50

    if "--top" in sys.argv:
        idx = sys.argv.index("--top")
        top_n = int(sys.argv[idx + 1])

    log.info("=" * 70)
    log.info("Stock Discovery Engine")
    log.info("=" * 70)

    # Discover candidates
    candidates = discover_candidates(top_n=top_n)

    # Update ranks.json
    update_ranks_json(candidates)

    log.info("\n" + "=" * 70)
    log.info(f"Discovery complete. Run backtest:")
    log.info(f"  python bot/backtester.py --months 60")
    log.info("=" * 70)
