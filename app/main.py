"""
Шаблон Telegram-бота для новичков.
Основная точка входа в приложение.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Импорт настроек после импортов telegram
from app.core.config import settings

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, settings.LOG_LEVEL.upper()),
)
logger = logging.getLogger(__name__)


async def setup_bot_commands(application):
    """Настройка команд бота в меню."""
    commands = [
        ("start", "Начать работу с ботом"),
        ("about", "О боте"),
        # Добавьте новые команды здесь по шаблону: ("command_name", "Описание команды")
    ]
    try:
        await application.bot.set_my_commands(commands)
        logger.info("Команды бота успешно установлены")
    except Exception as e:
        logger.error(f"Ошибка при установке команд бота: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    logger.info(f"Пользователь {update.effective_user.id} запустил команду /start")

    keyboard = [
        [InlineKeyboardButton("О боте", callback_data="about")],
        # Добавьте новые кнопки меню здесь по шаблону: [InlineKeyboardButton("Название кнопки", callback_data="callback_name")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = (
        "Привет! 👋\n"
        "Добро пожаловать в шаблон Telegram-бота!\n\n"
        "Используйте кнопки ниже или команды из меню для навигации."
    )

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /about."""
    logger.info(f"Пользователь {update.effective_user.id} запустил команду /about")

    about_text = (
        "🤖 О боте\n\n"
        "Это шаблон Telegram-бота для новичков.\n"
        "Здесь вы можете добавить описание вашего бота,\n"
        "его возможности и контактную информацию.\n\n"
        "Версия: 1.0.0\n"
        "Разработчик: Ваш Имя"
    )

    await update.message.reply_text(about_text)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на inline-кнопки."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    callback_data = query.data

    logger.info(f"Пользователь {user_id} нажал кнопку: {callback_data}")

    if callback_data == "about":
        await about(query, context)
    # Добавьте обработчики для новых кнопок здесь по шаблону:
    # elif callback_data == "your_callback_name":
    #     await your_function_name(query, context)


async def setup_bot(application):
    """Инициализация бота."""
    await setup_bot_commands(application)
    logger.info("Бот инициализирован")


def main() -> None:
    """Запуск бота."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен в переменных окружения.")
        return

    # Создание приложения
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about))

    # Добавьте новые команды здесь по шаблону:
    # application.add_handler(CommandHandler("your_command", your_function_name))

    # Регистрация обработчика inline-кнопок
    application.add_handler(CallbackQueryHandler(button_handler))

    # Добавление обработчика ошибок
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Логирование ошибок, возникающих в обработчиках."""
        logger.error(msg="Вызван исключение в обработчике", exc_info=context.error)

    application.add_error_handler(error_handler)

    # Инициализация бота
    application.post_init = setup_bot

    # Запуск бота в режиме long polling
    logger.info("Запуск бота...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
