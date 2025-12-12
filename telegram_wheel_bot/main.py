import asyncio
import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update, BotCommand
from telegram_wheel_bot.config import TELEGRAM_TOKEN, WHEELS_DIR, LOG_LEVEL
from telegram_wheel_bot.database import init_db
from telegram_wheel_bot.handlers.start import start, about
from telegram_wheel_bot.handlers.wheel import build_conversation
from telegram_wheel_bot.handlers.history import history_cmd, build_callbacks, compare_cmd
from telegram_wheel_bot.handlers.clean import build_clean_handlers, clean_cmd

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL.upper()),
)
logger = logging.getLogger(__name__)


def ensure_storage():
    if not os.path.exists(WHEELS_DIR):
        os.makedirs(WHEELS_DIR, exist_ok=True)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок для логирования исключений."""
    logger.error(msg="Exception while handling an update", exc_info=context.error)


async def log_all_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Временный обработчик для логирования всех обновлений."""
    if update.message and update.message.text:
        logger.info(f"Received message: {update.message.text} from user {update.effective_user.id if update.effective_user else 'unknown'}")
    elif update.callback_query:
        logger.info(f"Received callback_query: {update.callback_query.data} from user {update.effective_user.id if update.effective_user else 'unknown'}")


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await start(update, context)


async def history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await history_cmd(update, context)


async def clean_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await clean_cmd(update, context)


async def run():
    init_db()
    ensure_storage()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Добавление обработчика ошибок
    app.add_error_handler(error_handler)
    
    logger.info("Registering command handlers...")
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("Посмотреть_историю", history_handler))
    app.add_handler(CommandHandler("history", history_handler))
    app.add_handler(CommandHandler("compare", compare_cmd))
    
    # Регистрируем обработчики clean ПЕРЕД ConversationHandler
    clean_handlers = build_clean_handlers()
    logger.info(f"Registering {len(clean_handlers)} clean handlers")
    app.add_handler(CommandHandler("clean", clean_handler))
    app.add_handler(CommandHandler("clear", clean_handler))
    for i, h in enumerate(clean_handlers):
        if isinstance(h, CommandHandler):
            continue
        app.add_handler(h)
        logger.info(f"Registered clean handler {i+1}/{len(clean_handlers)}: {type(h).__name__}")
    
    for h in build_callbacks():
        app.add_handler(h)
    
    logger.info("Registering conversation handler...")
    app.add_handler(build_conversation())
    
    await app.bot.delete_my_commands()
    await app.bot.set_my_commands([
        BotCommand("start", "Начать"),
        BotCommand("about", "О боте"),
        BotCommand("history", "История колес"),
        BotCommand("clean", "Удаление колеса или всех колес"),
        BotCommand("build_wheel", "Построить колесо"),
        BotCommand("compare", "Сравнить с последним"),
    ])
    
    # Временный обработчик для отладки - логирует все сообщения
    # app.add_handler(MessageHandler(filters.ALL, log_all_updates), group=-1)
    
    logger.info("Бот запущен и готов к работе")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(run())
