"""Nutrition Telegram bot — send a food photo, get macros and micronutrients back.

Runs on its own bot token: Telegram allows one long-poller per token and
TELEGRAM_BOT_TOKEN already belongs to the always-on Job Pilot bot.
"""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.error import NetworkError
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters

import nutrition

BASE = Path(__file__).resolve().parent
load_dotenv(BASE.parent / ".env")

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("nutrition-bot")

BOT_TOKEN = os.environ["TELEGRAM_NUTRITION_BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ["TELEGRAM_ALLOWED_USER_ID"])
ANALYSIS_TIMEOUT = 180

HELP = (
    "Send me a photo of your meal and I'll break down the macros and micronutrients "
    "using USDA FoodData Central.\n\n"
    "• Add a caption for context — \"only ate half\", \"that's olive oil\"\n"
    "• Or just type it, which is better for drinks a photo can't measure — "
    "\"1 scoop whey in 300ml milk, 250ml orange juice\"\n"
    "• /today — totals so far today\n\n"
    "Educational estimates from portion sizes I judge by eye, not medical advice."
)


def _authorized(update: Update) -> bool:
    user = update.effective_user
    if user is None or user.id != ALLOWED_USER_ID:
        log.warning("Ignored message from unauthorized user id %s", user.id if user else None)
        return False
    return True


async def _hold_typing(update: Update) -> None:
    # Telegram's typing indicator lapses after ~5s; analysis takes far longer.
    while True:
        await update.message.chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(4)


def _analyze_and_log(photo: Path | None, text: str | None):
    report = nutrition.analyze(photo, text)
    return report, nutrition.log_meal(report)


async def _reply_with_analysis(update: Update, photo: Path | None, text: str | None) -> None:
    typing = asyncio.create_task(_hold_typing(update))
    try:
        report, daily = await asyncio.wait_for(
            asyncio.to_thread(_analyze_and_log, photo, text), timeout=ANALYSIS_TIMEOUT
        )
        reply = nutrition.format_report(report, daily)
    except asyncio.TimeoutError:
        log.error("Analysis timed out")
        reply = "That took too long to analyse — send it again?"
    except Exception:
        log.exception("Failed to analyse meal")
        reply = "Something broke while analysing that — check the bot log."
    finally:
        typing.cancel()

    await update.message.reply_text(reply, parse_mode="Markdown")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update) or not update.message or not update.message.photo:
        return

    photo = await update.message.photo[-1].get_file()  # largest rendition
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        await photo.download_to_drive(tmp_path)
        await _reply_with_analysis(update, tmp_path, update.message.caption)
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        return

    totals, meals = nutrition.daily_totals()
    if not meals:
        await update.message.reply_text("Nothing logged yet today.")
        return

    targets = nutrition.MACRO_TARGETS
    lines = [
        f"*Today* — {meals} meal{'s' if meals != 1 else ''}",
        f"{totals.get('calories', 0):.0f} / {targets['calories']} kcal "
        f"({totals.get('calories', 0) / targets['calories'] * 100:.0f}%)",
        f"Protein {totals.get('protein_g', 0):.0f} / {targets['protein_g']}g · "
        f"Carbs {totals.get('carbs_g', 0):.0f} / {targets['carbs_g']}g · "
        f"Fat {totals.get('fat_g', 0):.0f} / {targets['fat_g']}g · "
        f"Fiber {totals.get('fiber_g', 0):.0f} / {targets['fiber_g']}g",
    ]

    micros = [
        f"• {label} {totals[key]:.0f}{unit} ({totals[key] / target * 100:.0f}% RDA)"
        for key, (target, unit, label) in nutrition.MICRO_TARGETS.items()
        if totals.get(key)
    ]
    if micros:
        lines += ["", "*Micronutrients*"] + micros

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if _authorized(update):
        await update.message.reply_text(HELP)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Typed meals — mainly drinks, where a photo cannot show scoops or volume."""
    if not _authorized(update) or not update.message or not update.message.text:
        return
    await _reply_with_analysis(update, None, update.message.text)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Keep laptop-sleep and wifi-change noise out of the log without hiding real faults."""
    if isinstance(context.error, NetworkError):
        log.warning("Telegram unreachable, polling will retry: %s", context.error)
        return
    log.error("Unhandled error", exc_info=context.error)


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(on_error)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    log.info("Nutrition bot starting (allowlisted user id: %s)", ALLOWED_USER_ID)
    app.run_polling()


if __name__ == "__main__":
    main()
