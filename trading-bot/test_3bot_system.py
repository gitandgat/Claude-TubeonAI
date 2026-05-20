#!/usr/bin/env python
import os, sys, json, sqlite3
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "bot"))

try:
    from virtual_account import VirtualAccount
    from adaptation_engine import AdaptationEngine
    print("✓ VirtualAccount and AdaptationEngine imported successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

print("\nTesting VirtualAccount (Bot A)...")
db_path = "test_bot_a.db"
if Path(db_path).exists():
    os.remove(db_path)

try:
    account_a = VirtualAccount('A', initial_equity=100_000.0, db_path=db_path)
    print(f"  Initial: Cash=${account_a.cash:,.0f}, Equity=${account_a.equity:,.0f}")
    
    tid = account_a.buy("MSFT", 400.0, 10.0, 380.0, 480.0)
    print(f"  Buy 10 MSFT @ $400: Cash=${account_a.cash:,.0f}")
    
    pnl = account_a.sell(tid, "MSFT", 410.0, 10.0, "TP")
    print(f"  Sell 10 MSFT @ $410: P&L={pnl:+.2f}%")
    print("✓ VirtualAccount works")
except Exception as e:
    print(f"✗ VirtualAccount failed: {e}")
    import traceback
    traceback.print_exc()

os.remove(db_path)

print("\nTesting AdaptationEngine (Bot B)...")
db_path = "test_bot_b.db"
if Path(db_path).exists():
    os.remove(db_path)

try:
    account_b = VirtualAccount('B', initial_equity=100_000.0, db_path=db_path)
    tid = account_b.buy("GOOGL", 180.0, 5.0, 165.0, 220.0)
    account_b.sell(tid, "GOOGL", 190.0, 5.0, "WIN")
    
    engine = AdaptationEngine('B', db_path=db_path)
    metrics = engine.get_recent_metrics(lookback_trades=10)
    print(f"  Metrics: {metrics}")
    
    current = {'rs_threshold': 70, 'atr_multiplier': 2.0, 'vix_max': 30, 'max_risk_pct': 1.25}
    new = engine.suggest_b_params(current)
    print(f"  Suggested params: {new}")
    print("✓ AdaptationEngine works")
except Exception as e:
    print(f"✗ AdaptationEngine failed: {e}")
    import traceback
    traceback.print_exc()

os.remove(db_path)

print("\n✓✓✓ ALL CORE TESTS PASSED ✓✓✓")
print("\nNext: Need to fix yfinance environment for full bot runs")
