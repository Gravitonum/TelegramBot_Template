import asyncio
import os
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram_wheel_bot.config import TELEGRAM_TOKEN, WHEELS_DIR
from telegram_wheel_bot.database import init_db
from telegram_wheel_bot.handlers.start import start, about
from telegram_wheel_bot.handlers.wheel import build_conversation
from telegram_wheel_bot.handlers.history import history_cmd, build_callbacks
from telegram_wheel_bot.handlers.admin import clear_cmd


def ensure_storage():
    if not os.path.exists(WHEELS_DIR):
        os.makedirs(WHEELS_DIR, exist_ok=True)


async def run():
    init_db()
    ensure_storage()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("Посмотреть_историю", history_cmd))
    for h in build_callbacks():
        app.add_handler(h)
    app.add_handler(CommandHandler("Clear", clear_cmd))
    app.add_handler(build_conversation())
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(run())
