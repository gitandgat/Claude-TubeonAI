#!/bin/bash
# Nutrition Telegram bot — always-on runner (launchd entry point).
cd "$(dirname "$0")"
# exec so launchd supervises python directly; without it launchd kills this wrapper
# and orphans python, leaving two pollers fighting over one Telegram token.
exec ./.venv/bin/python3 bot.py >> bot.log 2>&1
