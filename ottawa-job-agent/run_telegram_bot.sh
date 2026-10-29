#!/bin/bash
# Job Pilot Telegram bot — always-on runner (launchd entry point).
cd "$(dirname "$0")"
./telegram_venv/bin/python3 telegram_bot.py >> telegram_bot.log 2>&1
