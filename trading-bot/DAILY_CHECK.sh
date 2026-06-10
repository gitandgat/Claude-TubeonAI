#!/bin/bash
# DAILY_CHECK.sh — Quick morning validation
# Run this at 9:30 AM ET daily to validate bot execution

set -e

BOT_DIR="/Users/toto/Claude TubeonAI/trading-bot"
DB_FILE="$BOT_DIR/trading_bot.db"
BOT_LOG="$BOT_DIR/bot/bot.log"
SCHEDULER_LOG="$BOT_DIR/bot/scheduler.log"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         MINERVINI BOT — DAILY VALIDATION CHECK            ║"
echo "║              $(date '+%Y-%m-%d %H:%M %Z')                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ─────────────────────────────────────────────────────────────────
# 1. Check bot execution (heartbeat written by scheduler after each run)
# ─────────────────────────────────────────────────────────────────
echo "✓ BOT EXECUTION"
HEARTBEAT="$BOT_DIR/bot/last_run.json"
if [ -f "$HEARTBEAT" ]; then
    HB_DATE=$(python3 -c "import json;print(json.load(open('$HEARTBEAT'))['last_run'][:10])" 2>/dev/null || echo "?")
    HB_STATUS=$(python3 -c "import json;print(json.load(open('$HEARTBEAT'))['status'])" 2>/dev/null || echo "?")
    TODAY=$(date '+%Y-%m-%d')
    if [ "$HB_DATE" = "$TODAY" ] && [ "$HB_STATUS" = "ok" ]; then
        echo "  ✓ Bot ran successfully today ($HB_DATE)"
    elif [ "$HB_DATE" = "$TODAY" ]; then
        echo "  ✗ Bot ran today but FAILED — check bot.log"
    else
        echo "  ⚠ Last successful heartbeat: $HB_DATE (status=$HB_STATUS) — bot has NOT run today"
    fi
elif [ -f "$SCHEDULER_LOG" ]; then
    if tail -5 "$SCHEDULER_LOG" | grep -q "Bot run finished successfully"; then
        echo "  ✓ Bot ran successfully (per scheduler.log; no heartbeat yet)"
    else
        echo "  ✗ Bot execution status unclear — check scheduler.log"
    fi
else
    echo "  ⚠ Scheduler not running yet"
fi
echo ""

# ─────────────────────────────────────────────────────────────────
# 2. Check open positions
# ─────────────────────────────────────────────────────────────────
echo "✓ OPEN POSITIONS"
if [ -f "$DB_FILE" ]; then
    OPEN_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM trades WHERE status='OPEN';" 2>/dev/null || echo "0")
    echo "  Open trades: $OPEN_COUNT"

    if [ "$OPEN_COUNT" -gt 0 ]; then
        echo ""
        sqlite3 "$DB_FILE" "SELECT ticker, entry_date, entry_price, qty FROM trades WHERE status='OPEN' ORDER BY entry_date DESC LIMIT 5;" 2>/dev/null | column -t -s '|' -N "TICKER,ENTRY_DATE,PRICE,QTY"
    fi
else
    echo "  Database not found"
fi
echo ""

# ─────────────────────────────────────────────────────────────────
# 3. Check recent exits
# ─────────────────────────────────────────────────────────────────
echo "✓ RECENT EXITS (Last 5)"
if [ -f "$DB_FILE" ]; then
    CLOSED_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM trades WHERE status='CLOSED' AND DATE(exit_date) = DATE('now', '-0 days');" 2>/dev/null || echo "0")
    echo "  Closed today: $CLOSED_COUNT"

    if [ "$CLOSED_COUNT" -gt 0 ]; then
        echo ""
        sqlite3 "$DB_FILE" "SELECT ticker, exit_date, exit_reason, printf('%.2f%%', profit_loss_pct) FROM trades WHERE status='CLOSED' ORDER BY exit_date DESC LIMIT 5;" 2>/dev/null | column -t -s '|' -N "TICKER,EXIT_DATE,REASON,P&L%"
    fi
else
    echo "  Database not found"
fi
echo ""

# (3-bot comparison removed — simplified to single production bot, Jun 2026)

# ─────────────────────────────────────────────────────────────────
# 4. Quick performance summary
# ─────────────────────────────────────────────────────────────────
echo "✓ PERFORMANCE (Last 7 Days)"
if command -v python3 &> /dev/null && [ -f "$BOT_DIR/bot/performance_tracker.py" ]; then
    cd "$BOT_DIR"
    python3 bot/performance_tracker.py --last-7 2>/dev/null || echo "  (Run: python3 bot/performance_tracker.py --last-7)"
else
    echo "  Run: python3 bot/performance_tracker.py --last-7"
fi
echo ""

# ─────────────────────────────────────────────────────────────────
# 5. Log summary
# ─────────────────────────────────────────────────────────────────
echo "✓ LOGS"
echo "  Bot log:       $BOT_LOG"
echo "  Scheduler log: $SCHEDULER_LOG"
echo "  Last bot line: $(tail -1 $BOT_LOG 2>/dev/null || echo '(none)')"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "Use these commands for deeper investigation:"
echo ""
echo "  # View all recent trades"
echo "  sqlite3 $DB_FILE \\\"SELECT ticker, entry_date, exit_date, profit_loss_pct FROM trades ORDER BY exit_date DESC LIMIT 20;\\\""
echo ""
echo "  # Check for errors"
echo "  tail -50 $BOT_LOG | grep -i error"
echo ""
echo "  # Weekly performance export"
echo "  cd $BOT_DIR && python3 bot/performance_tracker.py --csv"
echo ""
echo "════════════════════════════════════════════════════════════"
