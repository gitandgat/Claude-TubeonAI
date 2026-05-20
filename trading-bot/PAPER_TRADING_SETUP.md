# Paper Trading Validation Setup

**Goal:** Run the bot for 2–4 weeks on paper trading to validate performance before live trading.

---

## Step 1: Verify Environment

```bash
cd /Users/toto/Claude\ TubeonAI/trading-bot

# Check .env file has these keys:
cat .env | grep -E "ALPACA_API_KEY|ALPACA_SECRET_KEY|PAPER_TRADING|POLYGON_API_KEY"
```

**Required values:**
- `ALPACA_API_KEY` ✓
- `ALPACA_SECRET_KEY` ✓
- `PAPER_TRADING=true` (forces paper account)
- `POLYGON_API_KEY` ✓
- `ALERT_SENDER_EMAIL` (optional for alerts)
- `ALERT_SENDER_PASSWORD` (optional for alerts)
- `SLACK_WEBHOOK_URL` (optional for Slack alerts)

If any are missing, add them to `.env` now.

---

## Step 2: Verify Python Dependencies

```bash
python3 --version  # Ensure 3.8+

pip install -r requirements.txt --upgrade
```

**Key packages:**
- alpaca-py (Alpaca broker API)
- python-polygon (Polygon.io market data)
- pytz (timezone)
- requests (HTTP)
- python-dotenv (env vars)

---

## Step 3: Dry-Run the Bot Once

```bash
cd /Users/toto/Claude\ TubeonAI/trading-bot

# Run bot manually to test
python3 bot/minervini_bot.py
```

**Expected output:**
- Loads ranks.json with 50+ candidates
- Checks market regime (SPY > MA200)
- Checks volatility (VIX 10-30)
- Screens candidates through Minervini 7-point checks
- Intraday filter checks (5-min/15-min bars)
- Logs entries/exits to trading_bot.db
- Generates bot.log with detailed decision trace

**If errors occur:**
- Check bot.log for stacktraces
- Verify API keys in .env
- Run `python3 -c "import alpaca; print('Alpaca OK')"` to test imports

---

## Step 4: Set Up Daily Automation (launchd)

Create launchd plist to run bot every weekday at 9:00 AM ET:

```bash
# Create plist file
cat > ~/Library/LaunchAgents/com.minervini.tradingbot.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.minervini.tradingbot</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/toto/Claude TubeonAI/trading-bot/bot/scheduler.py</string>
    </array>
    
    <key>StartInterval</key>
    <integer>1800</integer>
    
    <key>StandardOutPath</key>
    <string>/Users/toto/Claude TubeonAI/trading-bot/bot/scheduler.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/toto/Claude TubeonAI/trading-bot/bot/scheduler.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>TZ</key>
        <string>America/New_York</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load it
launchctl load ~/Library/LaunchAgents/com.minervini.tradingbot.plist

# Verify it's running
launchctl list | grep minervini
```

**To stop the bot:**
```bash
launchctl unload ~/Library/LaunchAgents/com.minervini.tradingbot.plist
```

**To view logs:**
```bash
tail -f /Users/toto/Claude\ TubeonAI/trading-bot/bot/scheduler.log
tail -f /Users/toto/Claude\ TubeonAI/trading-bot/bot/bot.log
```

---

## Step 5: Daily Validation Checklist (Weeks 1–4)

Every morning after 9:30 AM ET, check:

### ✓ Bot Execution
- [ ] Bot ran (scheduler.log shows "Bot run finished successfully")
- [ ] No errors (bot.log shows entry/exit logic, not exceptions)
- [ ] Database updated (trading_bot.db file timestamp = today)

### ✓ Entry Signals
- [ ] Log recent entries:
  ```bash
  sqlite3 /Users/toto/Claude\ TubeonAI/trading-bot/trading_bot.db \
    "SELECT ticker, entry_date, entry_price, qty FROM trades WHERE status='OPEN' ORDER BY entry_date DESC LIMIT 5;"
  ```
- [ ] Expected entries per day: 0–3 (bot is highly selective)
- [ ] Entry prices align with chart (check via Alpaca dashboard)

### ✓ Exit Signals
- [ ] Log recent exits:
  ```bash
  sqlite3 /Users/toto/Claude\ TubeonAI/trading-bot/trading_bot.db \
    "SELECT ticker, exit_date, exit_reason, profit_loss_pct FROM trades WHERE status='CLOSED' ORDER BY exit_date DESC LIMIT 5;"
  ```
- [ ] Exits triggered by STOP_LOSS, TAKE_PROFIT, or TIME_EXIT
- [ ] P&L % matches calculation

### ✓ Daily Performance
- [ ] Check daily summary:
  ```bash
  python3 bot/performance_tracker.py
  ```
- [ ] Track these metrics daily:
  - Total trades
  - Win rate %
  - Profit factor
  - Sharpe ratio

### ✓ Account Health
- [ ] Cash position (should increase with profits, decrease with losses)
  ```bash
  python3 -c "from alpaca.trading.client import TradingClient; c = TradingClient('...', '...', paper=True); a = c.get_account(); print(f'Equity: \${a.equity:,.0f} | Cash: \${a.cash:,.0f}')"
  ```
- [ ] No liquidated positions (all exits voluntary via bot logic)
- [ ] Buying power > 0 (never overleveraged)

---

## Step 6: Weekly Summary (Every Friday)

Run full performance report:

```bash
# Last 7 days
python3 bot/performance_tracker.py --last-7

# Export to CSV for analysis
python3 bot/performance_tracker.py --csv
```

**Track in a simple spreadsheet:**
| Week | Total Trades | Win Rate | Profit Factor | Sharpe | Cumulative P&L |
|------|-------------|----------|---------------|--------|----------------|
| W1   | 2           | 50%      | 1.2           | 0.3    | +1.5%          |
| W2   | 5           | 60%      | 1.8           | 0.7    | +3.2%          |
| W3   | 3           | 67%      | 2.1           | 0.9    | +4.8%          |
| W4   | 4           | 75%      | 2.5           | 1.2    | +6.5%          |

---

## Step 7: Success Criteria (After 2–4 Weeks)

✓ **VALIDATION PASSED** if ANY of these hold:
- [ ] Win rate ≥ 50%
- [ ] Profit factor ≥ 1.5
- [ ] Sharpe ratio ≥ 0.8
- [ ] Cumulative P&L > +5%

❌ **VALIDATION FAILED** if ALL of these hold:
- Win rate < 40%
- Profit factor < 1.0
- Sharpe ratio < 0.3
- Cumulative P&L < -5%

**If failed:** Stop, analyze why (market regime? Bad entries? Overlapping stops?), tune one variable, retest.

**If passed:** Proceed to live trading with 10% of capital first.

---

## Step 8: Switch to Live Trading (Optional)

Once validated on paper:

```bash
# Edit .env
PAPER_TRADING=false

# Test with micro position size first
# Only trade $5K account size, not full capital
```

**CRITICAL:** 
- Never trade your entire capital immediately
- Start with 10% of total capital
- Scale up only after 4 weeks of profitable live trading
- Always keep stop losses active
- Monitor drawdowns daily

---

## Logs & Debugging

### View all recent trades
```bash
sqlite3 trading_bot.db "SELECT ticker, entry_date, exit_date, exit_reason, profit_loss_pct FROM trades ORDER BY exit_date DESC LIMIT 20;"
```

### Check specific stock
```bash
sqlite3 trading_bot.db "SELECT * FROM trades WHERE ticker='AAPL' ORDER BY entry_date DESC;"
```

### Check intraday filter decisions
```bash
grep "intraday" bot.log | tail -20
```

### Check market regime checks
```bash
grep "market uptrend\|volatility" bot.log | tail -20
```

---

## Common Issues

**Q: Bot not running at 9:00 AM?**
- Check launchctl: `launchctl list | grep minervini`
- Check Mac was awake at 9:00 AM
- Check timezone: `date +%Z` should show EDT (May–Oct) or EST (Nov–Apr)
- Check logs: `tail -100 scheduler.log`

**Q: No trades ever?**
- Market may be in downtrend (SPY < MA200) — check `grep "market uptrend" bot.log`
- Volatility may be outside 10-30 range — check VIX
- Watchlist candidates may not pass 7-point check — run `python bot/discover_candidates.py`

**Q: Trades losing money?**
- Check if exits are happening at correct prices (slippage on market orders?)
- Check if stop losses are actually -7% from entry
- Check intraday filter (5-min/15-min bars may be filtering out good entries)

---

## Next: Go Live (After Validation)

Once you have 2+ weeks of paper trading performance ≥ 50% win rate:

1. Create a separate live account (keep paper as backup)
2. Set `PAPER_TRADING=false` in .env
3. Start with $5K–$10K capital
4. Run bot for 4+ weeks before scaling
5. Only increase capital after consistent profitability

**Good luck! 🚀**
