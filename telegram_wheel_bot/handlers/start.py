from telegram import Update
from telegram.ext import ContextTypes
from telegram_wheel_bot.services.user_service import register_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    register_user(u.id, u.username, u.first_name)
    text = (
        f"Привет, {u.first_name}! 👋\n"
        "Это бот для отслеживания качества твоей жизни.\n"
        "Выбери действие из меню ↓\n\n"
        "/start\n/about\n/Построить_колесо\n/Посмотреть_историю"
    )
    await update.message.reply_text(text)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📊 Wheel of Life Bot\n\n"
        "Этот бот помогает тебе оценить различные аспекты жизни и улучшить их.\n\n"
        "Категории:\n"
        "1. Семья\n2. Друзья\n3. Здоровье\n4. Хобби\n5. Деньги\n6. Отдых\n7. Личное развитие\n8. Работа/бизнес\n\n"
        "Оценивай каждую категорию от 1 до 10, и получай AI-анализ!"
    )
    await update.message.reply_text(text)
