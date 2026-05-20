# Minervini Trend Template Bot — Paper Trading Launch

**Status:** All 11 power-ups implemented ✓  
**Mode:** Ready for paper trading validation  
**Timeline:** 2–4 weeks of testing before live trading  
**Date:** May 17, 2026

---

## What You Have

A fully integrated institutional-grade trading bot with:

1. ✓ **Minervini Trend Template** (4-point validation + 3 confirmatory checks)
2. ✓ **Real RS Rank** (vs SPY, not hardcoded)
3. ✓ **Market Regime Filter** (SPY > MA200 uptrend requirement)
4. ✓ **Volatility Filter** (VIX 10–30 acceptable range)
5. ✓ **Dynamic ATR Stops** (not fixed 7%, but 2×ATR)
6. ✓ **RSI Confirmation** (14-period RSI 50–80 entry zone)
7. ✓ **Intraday Confirmation** (5-min/15-min momentum checks)
8. ✓ **Sector Rotation** (position sizing by sector strength)
9. ✓ **Live Alerts** (email + Slack on entries/exits)
10. ✓ **Performance Dashboard** (HTML realtime portfolio view)
11. ✓ **Daily Email Report** (market close summary)

**Plus:** SQLite trade journaling, launchd automation, Alpaca paper trading integration.

---

## Quick Start (30 seconds)

```bash
cd /Users/toto/Claude\ TubeonAI/trading-bot

# 1. Verify environment
cat .env | grep ALPACA_API_KEY

# 2. Test bot manually (dry-run on paper trading)
python3 bot/minervini_bot.py

# 3. Check results
python3 bot/performance_tracker.py

# 4. Enable daily automation
bash DAILY_CHECK.sh  # Run this daily at 9:30 AM ET
```

---

## The Next 2–4 Weeks (Validation Phase)

### What to Do

1. **Let the bot run automatically** (9:00 AM ET every weekday via launchd)
2. **Check performance daily** (9:30 AM ET)
   ```bash
   /Users/toto/Claude\ TubeonAI/trading-bot/DAILY_CHECK.sh
   ```
3. **Review Friday** (end of week metrics)
   ```bash
   python3 bot/performance_tracker.py --last-7
   ```

### What to Track

| Metric | Target | Current |
|--------|--------|---------|
| **Win Rate** | ≥ 50% | TBD |
| **Profit Factor** | ≥ 1.5 | TBD |
| **Sharpe Ratio** | ≥ 0.8 | TBD |
| **Cumulative P&L** | > +5% | TBD |

**Decision Rules:**
- If ≥ 3/4 metrics pass → **GO LIVE** (with 10% capital)
- If < 2/4 metrics pass → **PAUSE & TUNE** (adjust entry/exit rules)
- If 2/4 pass borderline → **EXTEND TESTING** (another 2 weeks)

---

## Daily Checklist

Save this as a recurring calendar reminder (9:30 AM ET, weekdays):

```
□ Bot ran successfully (check scheduler.log)
□ Check open positions (DAILY_CHECK.sh shows entries)
□ Check recent exits (look for correct P&L calc)
□ Run performance tracker (python3 bot/performance_tracker.py)
□ Review bot.log for errors
□ Log results in tracking spreadsheet
```

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `bot/minervini_bot.py` | Main trading engine (entry/exit logic) |
| `bot/performance_tracker.py` | Daily metrics calculator |
| `DAILY_CHECK.sh` | Quick morning validation script |
| `PAPER_TRADING_SETUP.md` | Full setup & troubleshooting guide |
| `trading_bot.db` | SQLite database (all trades logged) |
| `bot/bot.log` | Detailed bot execution trace |
| `bot/scheduler.log` | Launchd automation log |

---

## Common Commands

```bash
# View today's trades
sqlite3 trading_bot.db "SELECT ticker, entry_date, exit_reason, profit_loss_pct FROM trades WHERE DATE(exit_date) = DATE('now') ORDER BY exit_date DESC;"

# View all open positions
sqlite3 trading_bot.db "SELECT ticker, entry_date, entry_price, qty FROM trades WHERE status='OPEN';"

# Export weekly results to CSV
cd /Users/toto/Claude\ TubeonAI/trading-bot && python3 bot/performance_tracker.py --csv

# Check for errors in bot.log
grep -i error bot/bot.log | tail -20

# Monitor real-time scheduler
tail -f bot/scheduler.log
```

---

## Red Flags (Stop & Investigate)

❌ **Bot never enters trades**
- Likely: Market in downtrend (SPY < MA200) or VIX outside 10-30
- Check: `grep "market uptrend\|volatility" bot/bot.log`

❌ **Win rate < 30%**
- Likely: Bad entries (intraday filter too loose) or exits too tight
- Action: Reduce position size, increase ATR multiplier for stops

❌ **Large single loss (> -10%)**
- Issue: Position sizing too aggressive OR stop loss didn't trigger
- Check: Did Alpaca order execute? Check Alpaca dashboard

❌ **No database updates**
- Issue: Bot crashed or didn't run
- Check: `ls -lh trading_bot.db` (timestamp should be today)

---

## Timeline to Live Trading

**Week 1–2:** Paper trading, validate signals  
**Week 2–4:** Accumulate 20+ trades, track metrics  
**Day 28:** Evaluate against success criteria  

**If validated:**
→ Create live account  
→ Set `PAPER_TRADING=false` in .env  
→ Start with 10% of capital ($5K–$10K)  
→ Run 4+ weeks before scaling  

**If not validated:**
→ Pause live plans  
→ Adjust one variable (entry filter, exit logic, position size)  
→ Test 2 more weeks  

---

## Documentation

- **Full setup guide:** `PAPER_TRADING_SETUP.md`
- **Performance tracker:** `python3 bot/performance_tracker.py --help`
- **Bot logs:** `tail -f bot/bot.log` (real-time)
- **Scheduler logs:** `tail -f bot/scheduler.log` (automation status)

---

## What Happens Automatically

**Every weekday at 9:00 AM ET:**
1. Scheduler wakes bot
2. Bot checks market regime + volatility
3. Bot screens all candidates through Minervini 7-point validation
4. Bot confirms intraday momentum (5-min/15-min bars)
5. Bot places entries where conditions met
6. Bot places ATR-based stops + profit targets
7. Bot monitors open positions for exits
8. Bot logs all trades to database
9. Bot sends alerts (email/Slack if configured)

**You just need to:**
- ✓ Keep bot running (launchd handles it)
- ✓ Check daily performance (DAILY_CHECK.sh)
- ✓ Review weekly metrics (performance_tracker.py)

---

## Next Step: Start Testing

Run this now:

```bash
cd /Users/toto/Claude\ TubeonAI/trading-bot

# Verify everything works
python3 bot/minervini_bot.py

# Check initial performance
python3 bot/performance_tracker.py

# Enable daily automation
launchctl load ~/Library/LaunchAgents/com.minervini.tradingbot.plist
```

Then **check back daily at 9:30 AM ET** using:

```bash
/Users/toto/Claude\ TubeonAI/trading-bot/DAILY_CHECK.sh
```

---

**You're ready. Good luck! 🚀**

Questions? Check `PAPER_TRADING_SETUP.md` for troubleshooting or revisit implementation docs in `IMPLEMENTATION_SUMMARY.md`.
