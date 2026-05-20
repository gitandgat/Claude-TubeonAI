#!/bin/bash
# STARTUP_CHECK.sh — Verify 3-bot system is ready to trade
# Run this before first deployment or after making changes

set -e

BOT_DIR="/Users/toto/Claude TubeonAI/trading-bot"
cd "$BOT_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          3-BOT ALPACA INTEGRATION — STARTUP CHECK         ║"
echo "║              $(date '+%Y-%m-%d %H:%M %Z')                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ─────────────────────────────────────────────────────────────────
# 1. Check environment variables
# ─────────────────────────────────────────────────────────────────
echo "✓ CREDENTIALS CHECK"
python3 << 'EOF'
import os
from dotenv import load_dotenv
import sys

load_dotenv(".env")

checks = {
    "MASSIVE_API_KEY": os.getenv("MASSIVE_API_KEY"),
    "ALPACA_API_KEY (Production)": os.getenv("ALPACA_API_KEY"),
    "ALPACA_API_KEY_B (Bot B)": os.getenv("ALPACA_API_KEY_B"),
    "ALPACA_API_KEY_C (Bot C)": os.getenv("ALPACA_API_KEY_C"),
}

missing = [k for k, v in checks.items() if not v]
if missing:
    print(f"  ✗ Missing: {', '.join(missing)}")
    sys.exit(1)

for key in checks:
    print(f"  ✓ {key}")
EOF
echo ""

# ─────────────────────────────────────────────────────────────────
# 2. Test Alpaca connections
# ─────────────────────────────────────────────────────────────────
echo "✓ ALPACA CONNECTIONS"
python3 << 'EOF'
import sys
sys.path.insert(0, 'bot')
from dotenv import load_dotenv
import os
from alpaca.trading.client import TradingClient

load_dotenv(".env")

bots = [
    ("Bot B (Adaptive)", "ALPACA_API_KEY_B", "ALPACA_SECRET_KEY_B"),
    ("Bot C (Hybrid)", "ALPACA_API_KEY_C", "ALPACA_SECRET_KEY_C"),
]

for name, key_env, secret_env in bots:
    key = os.getenv(key_env)
    secret = os.getenv(secret_env)
    try:
        client = TradingClient(api_key=key, secret_key=secret, paper=True)
        account = client.get_account()
        print(f"  ✓ {name}: ${float(account.equity):,.2f}")
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        sys.exit(1)
EOF
echo ""

# ─────────────────────────────────────────────────────────────────
# 3. Check required files
# ─────────────────────────────────────────────────────────────────
echo "✓ FILES PRESENT"
files=(
    "bot/bot_a.py"
    "bot/bot_b.py"
    "bot/bot_c.py"
    "bot/scheduler.py"
    "bot/compare_performance.py"
    "bot/adaptation_engine.py"
    "ranks.json"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file NOT FOUND"
        exit 1
    fi
done
echo ""

# ─────────────────────────────────────────────────────────────────
# 4. Verify Python imports
# ─────────────────────────────────────────────────────────────────
echo "✓ PYTHON IMPORTS"
python3 << 'EOF'
import sys
import os
sys.path.insert(0, 'bot')
os.chdir('bot')

modules = [
    "bot_b",
    "bot_c",
    "compare_performance",
    "adaptation_engine",
]

for module in modules:
    try:
        __import__(module)
        print(f"  ✓ {module}")
    except ImportError as e:
        print(f"  ✗ {module}: {e}")
        sys.exit(1)
EOF
echo ""

# ─────────────────────────────────────────────────────────────────
# 5. Check scheduler
# ─────────────────────────────────────────────────────────────────
echo "✓ SCHEDULER CONFIGURATION"
if grep -q "09:00.*trigger_bot" bot/scheduler.py && \
   grep -q "09:05.*trigger_all_variants" bot/scheduler.py; then
    echo "  ✓ Production bot scheduled at 09:00 ET"
    echo "  ✓ 3-bot variants scheduled at 09:05 ET"
else
    echo "  ✗ Scheduler not configured correctly"
    exit 1
fi
echo ""

echo "════════════════════════════════════════════════════════════"
echo "✓ SYSTEM READY FOR DEPLOYMENT"
echo ""
echo "Next steps:"
echo "  1. Verify all 3 Alpaca accounts in https://app.alpaca.markets"
echo "  2. Ensure launchd is running: launchctl list | grep scheduler"
echo "  3. Monitor: tail -f bot/scheduler.log"
echo "  4. View daily summary: ./DAILY_CHECK.sh"
echo "  5. Compare performance: python3 bot/compare_performance.py --last-7"
echo "════════════════════════════════════════════════════════════"
