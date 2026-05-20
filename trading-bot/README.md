# Trading Bot

A lightweight algorithmic trading bot combining **Kavout Stock Rank** signals with **20-day SMA** crossover and optional **Smart Signal** integration. Market data via **Massive.com (Polygon.io)**, automated Kavout scraping via **Playwright**, trade execution via **Alpaca** (paper mode by default).

---

## Quick Commands

```bash
# Scrape Kavout watchlist (Overview + Technical tabs)
python bot/scrape_kavout.py

# Scrape with Smart Signal included
python bot/scrape_kavout.py --signal

# Scrape only Smart Signal (quick daily update)
python bot/scrape_kavout.py --signal-only

# Run the trading bot
python bot/bot.py

# Backtest the Kavout + SMA20 strategy
python bot/backtest_kavout.py                    # 12 months
python bot/backtest_kavout.py --months 24        # 24 months
python bot/backtest_kavout.py --ticker AAPL      # Single stock
python bot/backtest_kavout.py --print-signals    # Debug: show all signals

# Check scheduler status
launchctl list | grep tradingbot
tail -f scheduler.log

# View latest trades
tail -f bot.log
```

---

## Project Structure

```
trading-bot/
├── bot/
│   ├── bot.py              # Core signal engine and trade executor
│   ├── backtest_kavout.py  # Backtest the Kavout + SMA20 strategy
│   ├── backtester.py       # Backtest the Minervini Trend Template strategy
│   ├── scrape_kavout.py    # Scrape Kavout watchlist via Playwright
│   ├── scheduler.py        # Automated execution scheduler
│   ├── trade_tracker.py    # SQLite-based trade journal
│   └── position_manager.py # Position sizing helpers
├── dashboard/
│   └── index.html          # Local browser dashboard (no server needed)
├── requirements.txt
├── .env.example            # Copy to .env and fill in your keys
└── README.md
```

---

## Prerequisites

- Python 3.11+
- An [Alpaca Markets](https://app.alpaca.markets) account (free, paper trading available)
- A [Polygon.io](https://polygon.io) account (free tier is sufficient)
- A [Kavout](https://kavout.com) subscription for daily K Scores

---

## Setup

### 1. Clone / download the project

```bash
cd trading-bot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Open .env and fill in your API keys
```

---

## Getting API Keys

### Alpaca

1. Sign up at [alpaca.markets](https://alpaca.markets) (free)
2. Go to **Settings → API Keys**
3. Click **Generate New Key** under **Paper Trading**
4. Copy `API Key ID` → `ALPACA_API_KEY` and `Secret Key` → `ALPACA_SECRET_KEY`
5. Leave `PAPER_TRADING=true` until you are ready for live trading

### Massive.com / Polygon.io

1. Sign up at [polygon.io](https://polygon.io) (free tier available)
2. Go to **Dashboard → API Keys**
3. Copy your key → `MASSIVE_API_KEY`
4. Free tier provides end-of-day data at 5 requests/min — enough for this bot's watchlist of 5 tickers

### Kavout Account

1. Sign up at [kavout.com](https://kavout.com) (free or paid tier)
2. Add your desired stocks to your **Watchlist**
3. Access the watchlist at `https://kavout.com/watchlist`
   - The bot will scrape **Stock Rank** (High/Medium/Low) + **Outlook** (Outperform/Neutral/Underperform)
   - Optionally scrape **Smart Signal** (composite BUY/HOLD/SELL) with `--signal` flag

---

## Automated Kavout Scraping

Instead of manually updating scores, the bot scrapes Kavout automatically via Playwright:

### First-time setup

```bash
python bot/scrape_kavout.py
```

- Browser opens → log into Kavout **once**
- Session is saved in `.browser_data/`
- After first login, all future runs are headless and automatic

### Daily scrape (Overview + Technical tabs)

```bash
python bot/scrape_kavout.py
```

Scrapes:
- **Overview tab**: Stock Rank, Outlook
- **Technical tab**: Price, MA20, RSI, ADX (for tech signal calculation)
- Updates `ranks.json` automatically

### Include Smart Signal

```bash
python bot/scrape_kavout.py --signal
```

Scrapes Overview + Technical + **Smart Signal** tab, merging all three into `ranks.json`.

### Smart Signal only

```bash
python bot/scrape_kavout.py --signal-only
```

Scrapes only the Smart Signal tab (quick update if ranks/outlook don't change).

### Debug mode

```bash
python bot/scrape_kavout.py --debug
```

Dumps raw DOM rows to stdout for troubleshooting ticker extraction.

---

## Scheduled Daily Scraping

The scheduler includes a 2-minute network wait to handle post-wake connectivity delays. If you want to scrape with Smart Signal every morning before the 9 AM bot run, set up a second launchd job or cron entry.

---

## Backtesting the Strategy

**backtest_kavout.py** replays historical daily data through the same Kavout + SMA20 signal logic used by bot.py, tracking entry/exit points, trades, and P&L.

### Basic backtest (12 months)

```bash
python bot/backtest_kavout.py
```

This:
1. Loads your current `ranks.json` (watchlist + Kavout scores)
2. Fetches daily OHLCV from Polygon.io for the past 12 months
3. Simulates the signal logic day-by-day: entry on BUY signal, exit on SELL signal (or after 180 days)
4. Writes results to `backtest_kavout.db` and `backtest_kavout.log`

### Custom period (24 months)

```bash
python bot/backtest_kavout.py --months 24
```

### Single stock

```bash
python bot/backtest_kavout.py --ticker AAPL
```

Backtests only AAPL (must be in `ranks.json`).

### Debug mode (print all signals)

```bash
python bot/backtest_kavout.py --print-signals
```

Prints every signal decision (BUY/HOLD/SELL) for each ticker each day — useful to verify signal logic.

### Reading backtest results

Backtest results are saved in SQLite:

```python
from bot.trade_tracker import TradeTracker

tracker = TradeTracker("backtest_kavout.db")
print(tracker.get_pnl_summary(days=365))
tracker.print_summary(days=365)
```

---

## Signal Logic

Three-factor confluence signal: **Kavout Stock Rank + Outlook + Technical**

### Entry Signal (BUY)

All of the following must be true:
- **Rank** = `High`
- **Outlook** = `Outperform`
- **Tech** = `BUY` (price > MA20 AND RSI < 80 AND ADX > 20)
- **Close** > **SMA20** (live Polygon.io data check)

### Exit Signal (SELL)

Any one of the following:
- **Rank** = `Low`
- **Outlook** = `Underperform`
- **Tech** = `SELL` (price < MA20 OR RSI < 35)
- **Close** < **SMA20** (live Polygon.io data check)

### Hold

All other cases — no action, re-evaluated at next run.

---

## Optional: Smart Signal Integration

When scraped with `--signal`, the Smart Signal (BUY/HOLD/SELL) is stored in `ranks.json` for reference, but does **not** override the three-factor logic. You can use it for manual decision-making or extend the bot logic to weight it.

---

## Trade Execution

- **BUY** → enters a new position (up to `MAX_POSITION_SIZE = $1,000`)
- **SELL** → exits the full position if currently holding
- **HOLD** → no action taken

Share quantity is calculated automatically: `shares = floor(MAX_POSITION_SIZE / last_close)`.

---

## Running the Bot

### Manual workflow

```bash
# 1. Scrape latest Kavout data (Overview + Technical)
python bot/scrape_kavout.py

# 2. Review the signal preview printed to stdout
# 3. Run the bot when ready
python bot/bot.py
```

Output goes to the console **and** `bot.log`.

### Automated daily schedule (9:00 AM ET, weekdays)

The **scheduler** runs automatically via launchd (macOS):

1. Wakes the Mac at 8:45 AM ET (via `pmset`)
2. Waits for network connectivity (up to 2 min)
3. Runs `bot.py` at 9:00 AM ET
4. Puts the Mac to sleep after completion

The scheduler is already installed and running. You'll receive a notification at 7:46 PM Bangkok time (the evening before) to run `scrape_kavout.py` manually if desired.

To check scheduler status:

```bash
launchctl list | grep tradingbot
tail -f scheduler.log
```

### Dashboard

Open `dashboard/index.html` directly in any browser — no server required.

To connect it to live data, add a thin backend (e.g. FastAPI) that exposes `/api/account` and `/api/watchlist`, then replace the `MOCK_DATA` object in the HTML with `fetch()` calls.

---

## Safety Checklist Before Going Live

Complete **every** item before switching to real money:

- [ ] Run in paper mode for at least **3 months** and review all trades in `bot.log`
- [ ] Verify the P&L makes sense — check Alpaca paper account statements
- [ ] Confirm Polygon.io data matches what you see on other platforms (e.g. Yahoo Finance)
- [ ] Test `scrape_kavout.py` for **5+ runs** and verify `ranks.json` updates correctly
- [ ] Confirm Kavout login session persists across runs (check `.browser_data/` directory)
- [ ] Switch `PAPER_TRADING=false` in `.env` and update keys to **live** Alpaca keys (not paper keys)
- [ ] Start with a **smaller** `MAX_POSITION_SIZE` (e.g. `$250`) for the first live week
- [ ] Know Polygon.io's free-tier rate limits (5 calls/min, 2 calls/ticker) — bot waits 13s between tickers to stay under limit
- [ ] Understand that `TimeInForce.DAY` orders expire at 4 PM ET if unfilled
- [ ] Never run during pre-market / after-hours without changing `TimeInForce` to `GTC` or `OPG`
- [ ] Add a stop-loss strategy (see roadmap below) before risking significant capital
- [ ] Keep `bot.log` rotation in mind — it grows indefinitely; use `logrotate` or add a `RotatingFileHandler`
- [ ] Monitor the scheduler: check `scheduler.log` weekly for network issues or crashes
- [ ] Backup `.browser_data/` occasionally — losing the Kavout login session means one manual re-login

---

## Future Roadmap

| Feature | Status | Notes |
|---------|--------|-------|
| **Automated Kavout scraping** | ✅ Done | `scrape_kavout.py` with Playwright, browser session persistence |
| **Smart Signal integration** | ✅ Done | Optional `--signal` flag to scrape composite BUY/HOLD/SELL |
| **Network wait on wake** | ✅ Done | Scheduler waits 2 min for internet after Mac wakes |
| **Backtesting module** | ✅ Done | `backtest_kavout.py` replays Kavout + SMA20 strategy on historical data |
| Stop-loss / take-profit | ⏳ Pending | Add bracket orders using `LimitOrderRequest` + `StopLossRequest` |
| Holiday skip | ⏳ Pending | Load NYSE calendar from `trading_calendars` or `pandas_market_calendars` |
| Portfolio rebalancing | ⏳ Pending | Cap total exposure; avoid over-concentration in one sector |
| Email / SMS alerts | ⏳ Pending | Twilio or SendGrid on every `ORDER PLACED` or `ORDER FAILED` |
| Live dashboard backend | ⏳ Pending | FastAPI endpoint serving `/api/dashboard` JSON to the HTML dashboard |
| WebSocket price streaming | ⏳ Pending | Use Alpaca's Data Stream for real-time last-price updates |
| Multi-strategy support | ⏳ Pending | Plug in RSI, MACD, or ML models alongside Stock Rank |
| Smart Signal weighting | ⏳ Pending | Use Smart Signal to adjust position size or confidence level |
| Kavout API polling | ⏳ Pending | If Kavout releases an API, auto-pull Stock Rank without scraping |
