# 3-Bot Parallel Trading System

## Overview

Three Minervini bots trading simultaneously on Alpaca paper trading accounts ($100K each), differing only in adaptation strategy:

| Bot | Strategy | Adaptation | Account |
|-----|----------|-----------|---------|
| **A** | Static baseline | None | Production (ALPACA_API_KEY) |
| **B** | Adaptive parameters | Daily tuning (RS, ATR, VIX, risk%) | ALPACA_API_KEY_B |
| **C** | Hybrid Minervini | Position sizing only | ALPACA_API_KEY_C |

## Architecture

### Bots
- **bot_a.py**: Fixed Minervini rules (baseline control)
- **bot_b.py**: Same entry/exit, but parameters adapt daily via AdaptationEngine
- **bot_c.py**: Same Minervini rules as A, only max_risk_pct adapts based on drawdown

### Shared Infrastructure
- **scheduler.py**: Runs bots at 09:00 (production), 09:05 (all 3 variants) weekdays
- **adaptation_engine.py**: Reads recent trades, suggests parameter adjustments (bounded)
- **compare_performance.py**: Dashboard comparing all 3 variants
- **STARTUP_CHECK.sh**: Pre-flight verification
- **DAILY_CHECK.sh**: Morning validation & performance summary

### Alpaca Integration
All three bots submit **MarketOrderRequest** to Alpaca's TradingClient (paper trading).
Fills are real-time, based on live market data from Polygon.
All positions visible on https://app.alpaca.markets dashboard.

## Daily Workflow

### 09:00 AM ET
Production bot runs (unchanged, uses ALPACA_API_KEY):
```bash
python3 bot/minervini_bot.py
```

### 09:05 AM ET
3-bot variants run in sequence:
```bash
python3 bot/bot_a.py    # Static (30s delay)
python3 bot/bot_b.py    # Adaptive (30s delay)
python3 bot/bot_c.py    # Hybrid
python3 bot/compare_performance.py --last-7
```

### 09:30 AM ET (Manual)
Morning check:
```bash
./DAILY_CHECK.sh
```

Shows: open positions, recent exits, 3-bot comparison, P&L summary.

## Parameter Adaptation

### Bot B (Adaptive)
Bounds: RS 60-85, ATR 1.5-3.0, VIX 25-40, max_risk 0.5-2.0

Logic:
- win_rate < 40% → tighten RS (+5)
- profit_factor < 1.0 → widen stop (ATR +0.5)
- win_rate > 65% → relax RS (-5)
- drawdown > 8% → reduce risk (-0.25)

### Bot C (Hybrid)
Only max_risk_pct adapts:
- drawdown > 5% → 0.75%
- win_rate > 60% & drawdown < 3% → 1.5%

All adaptations logged in `bot_adaptations` table.

## Monitoring

### Alpaca Dashboard
Visit https://app.alpaca.markets:
- Each of 3 accounts shows real positions
- P&L visible in real-time
- Order history queryable

### Command-Line Tools

**Live comparison (last 7 days):**
```bash
python3 bot/compare_performance.py --last-7
```

**Live comparison (all-time):**
```bash
python3 bot/compare_performance.py --all-time
```

**Export to CSV:**
```bash
python3 bot/compare_performance.py --csv
```

**Morning summary:**
```bash
./DAILY_CHECK.sh
```

**Watch logs:**
```bash
tail -f bot/scheduler.log
tail -f bot/bot_a.log
tail -f bot/bot_b.log
tail -f bot/bot_c.log
```

## Validation Phase (2-4 weeks)

1. **Week 1**: Observe all 3 bots in action, check Alpaca dashboard
2. **Week 2-3**: Compare performance via `compare_performance.py`
3. **Week 4**: Choose winner based on cumulative P&L
4. **Decision**: Promote best performer to live trading with real money

## After Validation

Once confident, you can:
1. Switch the winner to live trading (change `paper=False`)
2. Retire the other two variants
3. Or promote all three if all show positive returns

## Troubleshooting

**Bots not running?**
```bash
./STARTUP_CHECK.sh
```

**No Alpaca orders appearing?**
```bash
# Check logs
tail -20 bot/bot_b.log | grep -i "order\|error"

# Verify API keys
echo "Bot B key: ${ALPACA_API_KEY_B}"
echo "Bot B secret: ${ALPACA_SECRET_KEY_B}"
```

**Comparison dashboard empty?**
Bots haven't run yet, or no trades closed yet. Run manually:
```bash
cd bot && python3 bot_b.py --dry-run
```

**Scheduler not running?**
```bash
launchctl list | grep scheduler
# If not listed:
launchctl load ~/Library/LaunchAgents/com.minervini.scheduler.plist
```

## Files Reference

```
trading-bot/
├── .env                          # Credentials (DO NOT COMMIT)
├── ranks.json                    # Kavout scores (daily refresh)
├── bots.db                       # Shared trades database (bot_variant column)
├── STARTUP_CHECK.sh              # Pre-flight checklist
├── DAILY_CHECK.sh                # Morning summary
├── 3-BOT-SYSTEM.md              # This file
│
└── bot/
    ├── minervini_bot.py          # Production (unchanged)
    ├── bot_a.py                  # Static baseline
    ├── bot_b.py                  # Adaptive parameters (Alpaca)
    ├── bot_c.py                  # Hybrid sizing (Alpaca)
    ├── scheduler.py              # Daily 09:00/09:05 automation
    ├── adaptation_engine.py       # Parameter tuning logic
    ├── compare_performance.py     # 3-bot dashboard
    ├── virtual_account.py        # Deprecated (VirtualAccount)
    ├── trade_tracker.py          # Trade persistence
    │
    ├── trend_filter.py           # Minervini validation
    ├── position_manager.py       # Size & stops
    ├── indicators.py             # RS, ATR, VIX
    ├── sector_rotation.py        # Sector strength
    ├── intraday_filter.py        # Time-of-day rules
    ├── alerts.py                 # Notifications
    │
    ├── bot_a.log
    ├── bot_b.log
    ├── bot_c.log
    └── scheduler.log
```

## Key Numbers

- **Starting capital per bot**: $100K (paper)
- **Max positions**: 5 simultaneous
- **Max per position**: 20% of equity
- **Base risk**: 1.25% per trade (adaptive for B/C)
- **Minervini target**: +20% per win
- **Stop loss**: 2× ATR (adaptive for B)
- **Run time**: 9:05 AM ET weekdays
- **Validation window**: 2-4 weeks

## Next Steps

1. ✓ **Today**: Verify system with `./STARTUP_CHECK.sh`
2. ✓ **Today**: Check Alpaca dashboard for all 3 accounts
3. **Tomorrow 9:30 AM**: Run `./DAILY_CHECK.sh` and watch first trades
4. **Daily**: Monitor `bot/bot_b.log` and `bot/bot_c.log`
5. **Weekly**: Review `compare_performance.py --last-7` and adaptation decisions
6. **After 4 weeks**: Promote winner to live trading

---

**Status**: ✓ Deployed  
**Last Updated**: 2026-05-18  
**Alpaca Accounts**: 3 paper accounts verified & funded
