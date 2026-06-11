"""Reconcile orphaned Alpaca positions into the trade tracker (one-time)."""
import sys
sys.path.insert(0, "/Users/toto/Claude TubeonAI/trading-bot/bot")
from dotenv import load_dotenv
load_dotenv("/Users/toto/Claude TubeonAI/trading-bot/.env")
import os
from datetime import datetime

from alpaca.trading.client import TradingClient
from trade_tracker import TradeTracker

STOP_PCT, TARGET_PCT = 7.0, 20.0

client = TradingClient(os.getenv("ALPACA_API_KEY") or os.getenv("APCA_API_KEY_ID"),
                       os.getenv("ALPACA_SECRET_KEY") or os.getenv("APCA_API_SECRET_KEY"), paper=True)
tracker = TradeTracker("/Users/toto/Claude TubeonAI/trading-bot/trading_bot.db")

existing = {t["ticker"] for t in tracker.get_open_trades()}
# Positions were opened around May 22, 2026 (per bot logs); exact date only
# matters for the 180-day time exit, so the approximation is harmless.
entry_date = datetime(2026, 5, 22, 9, 30)

for p in client.get_all_positions():
    if p.symbol in existing:
        print(f"  {p.symbol}: already tracked, skipping")
        continue
    entry = float(p.avg_entry_price)
    qty = int(float(p.qty))
    current = float(p.current_price)
    tid = tracker.open_trade(
        ticker=p.symbol, entry_date=entry_date, entry_price=entry, entry_qty=qty,
        stop_loss_level=round(entry * (1 - STOP_PCT / 100), 2),
        take_profit_level=round(entry * (1 + TARGET_PCT / 100), 2),
    )
    # Peak so far: at least entry; use current if higher
    tracker.update_trade_highest_price(tid, max(entry, current))
    pnl = (current - entry) / entry * 100
    print(f"  {p.symbol}: trade {tid} │ {qty} sh @ ${entry:.2f} │ stop ${entry*0.93:.2f} "
          f"target ${entry*1.20:.2f} │ now ${current:.2f} ({pnl:+.2f}%)")

print("\nOpen trades in tracker now:", len(tracker.get_open_trades()))
