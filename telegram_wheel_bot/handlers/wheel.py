from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CommandHandler,
)
from telegram_wheel_bot.services.wheel_service import create_and_analyze_wheel
from telegram_wheel_bot.services.user_service import register_user
from telegram_wheel_bot.services.llm_service import markdown_to_html
from telegram_wheel_bot.utils import default_wheel_name, last_three_months_labels, previous_month_label, parse_month_label
from telegram_wheel_bot.services.history_service import get_history


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
        buttons.append(
            [
                InlineKeyboardButton(str(i), callback_data=f"rate:{cat_idx}:{i}")
                for i in row
            ]
        )
    return InlineKeyboardMarkup(buttons)


async def build_wheel_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    labels = last_three_months_labels()
    filtered = labels
    user = update.effective_user
    if user:
        db_user = register_user(user.id, user.username, user.first_name)
        wheels = get_history(db_user.id)
        used_dates = set()
        for w in wheels:
            try:
                used_dates.add(parse_month_label(w.name))
            except Exception:
                pass
        tmp = []
        for lbl in labels:
            try:
                d = parse_month_label(lbl)
            except Exception:
                d = None
            if d and d not in used_dates:
                tmp.append(lbl)
        filtered = tmp
    if not filtered:
        await update.message.reply_text("За последние три месяца все колеса уже созданы. Используй /history")
        return ConversationHandler.END
    buttons = [[InlineKeyboardButton(lbl, callback_data=f"choose_month:{lbl}")] for lbl in filtered]
    await update.message.reply_text(
        "Выбери незаполненный месяц (из последних трех), за который ты хочешь построить колесо",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    context.user_data["wheel_scores"] = {}
    return CHOOSING


async def receive_wheel_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = (
        update.message.text.strip()
        if update.message and update.message.text
        else default_wheel_name()
    )
    if not name:
        name = default_wheel_name()
    context.user_data["wheel_name"] = name
    context.user_data["category_index"] = 0
    await update.message.reply_text(
        f"<b>[Семья]</b>\nОцени по шкале от 1 до 10:", 
        reply_markup=rating_keyboard(0),
        parse_mode=ParseMode.HTML
    )
    return RATING_CATEGORY


async def choose_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    label = q.data.split(":", 1)[1]
    context.user_data["wheel_name"] = label
    context.user_data["category_index"] = 0
    try:
        await q.edit_message_text(
            f"<b>[Семья]</b>\nОцени по шкале от 1 до 10:", 
            reply_markup=rating_keyboard(0),
            parse_mode=ParseMode.HTML
        )
    except BadRequest:
        await q.message.reply_text(
            f"<b>[Семья]</b>\nОцени по шкале от 1 до 10:", 
            reply_markup=rating_keyboard(0),
            parse_mode=ParseMode.HTML
        )
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
        try:
            await q.edit_message_text(
                f"<b>[{next_cat}]</b>\nОцени по шкале от 1 до 10:",
                reply_markup=rating_keyboard(next_idx),
                parse_mode=ParseMode.HTML,
            )
        except BadRequest:
            pass
        context.user_data["category_index"] = next_idx
        return RATING_CATEGORY
    user = update.effective_user
    if not user:
        await q.edit_message_text("Ошибка: пользователь не найден")
        return ConversationHandler.END
    # Регистрируем/получаем пользователя в базе данных
    db_user = register_user(user.id, user.username, user.first_name)
    name = context.user_data.get("wheel_name") or previous_month_label()
    scores = context.user_data.get("wheel_scores", {})
    await q.edit_message_text(
        "✓ Колесо создано! Рисую красивую диаграмму, мне нужно немного времени..."
    )
    wheel_id, image_path, analysis = await create_and_analyze_wheel(
        db_user.id, name, scores
    )
    if image_path:
        try:
            await q.message.reply_photo(photo=open(image_path, "rb"))
        except Exception:
            pass
    # Конвертируем markdown в HTML для совместимости со старыми сообщениями
    html_analysis = markdown_to_html(analysis)
    await q.message.reply_text(html_analysis, parse_mode=ParseMode.HTML)
    await q.message.reply_text("/history")
    context.user_data.clear()
    return ConversationHandler.END


def build_conversation():
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(r"^/Построить_колесо$"), build_wheel_entry),
            CommandHandler("build_wheel", build_wheel_entry),
        ],
        states={
            CHOOSING: [
                CallbackQueryHandler(choose_month, pattern=r"^choose_month:.+")
            ],
            RATING_CATEGORY: [
                CallbackQueryHandler(rate_category, pattern=r"^rate:\d+:\d+$")
            ],
        },
        fallbacks=[],
    )
