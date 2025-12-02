from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, CommandHandler
from telegram_wheel_bot.services.wheel_service import create_and_analyze_wheel
from telegram_wheel_bot.utils import default_wheel_name


CHOOSING = 0
NAMING_WHEEL = 1
RATING_CATEGORY = 2


CATEGORIES = [
    "Семья",
    "Друзья",
    "Здоровье",
    "Хобби",
    "Деньги",
    "Отдых",
    "Личное развитие",
    "Работа/бизнес",
]


def rating_keyboard(cat_idx: int):
    buttons = []
    for row in [range(1, 6), range(6, 11)]:
        buttons.append([InlineKeyboardButton(str(i), callback_data=f"rate:{cat_idx}:{i}") for i in row])
    return InlineKeyboardMarkup(buttons)


async def build_wheel_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Назови свое колесо жизни (например: 'за декабрь 2024'). По умолчанию: предыдущий месяц год")
    context.user_data["wheel_scores"] = {}
    return NAMING_WHEEL


async def receive_wheel_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip() if update.message and update.message.text else default_wheel_name()
    if not name:
        name = default_wheel_name()
    context.user_data["wheel_name"] = name
    context.user_data["category_index"] = 0
    await update.message.reply_text(f"[Семья]\nОцени по шкале от 1 до 10:", reply_markup=rating_keyboard(0))
    return RATING_CATEGORY


async def rate_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    parts = data.split(":")
    idx = int(parts[1])
    val = int(parts[2])
    cat = CATEGORIES[idx]
    context.user_data.setdefault("wheel_scores", {})[cat] = val
    next_idx = idx + 1
    if next_idx < len(CATEGORIES):
        next_cat = CATEGORIES[next_idx]
        await q.edit_message_text(f"[{next_cat}]\nОцени по шкале от 1 до 10:", reply_markup=rating_keyboard(next_idx))
        context.user_data["category_index"] = next_idx
        return RATING_CATEGORY
    user = update.effective_user
    name = context.user_data.get("wheel_name") or default_wheel_name()
    scores = context.user_data.get("wheel_scores", {})
    await q.edit_message_text("✓ Колесо создано! Рисую красивую диаграмму...")
    wheel_id, image_path, analysis = await create_and_analyze_wheel(user.id, name, scores)
    await q.message.reply_photo(photo=open(image_path, "rb"))
    await q.message.reply_text(analysis)
    await q.message.reply_text("/Посмотреть_историю")
    context.user_data.clear()
    return ConversationHandler.END


def build_conversation():
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(r"^/Построить_колесо$"), build_wheel_entry),
            CommandHandler("build_wheel", build_wheel_entry),
        ],
        states={
            NAMING_WHEEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_wheel_name)],
            RATING_CATEGORY: [CallbackQueryHandler(rate_category, pattern=r"^rate:\d+:\d+$")],
        },
        fallbacks=[],
    )
