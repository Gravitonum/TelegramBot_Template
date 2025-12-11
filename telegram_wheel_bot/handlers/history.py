from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram_wheel_bot.services.history_service import (
    get_history,
    get_latest,
    get_scores,
    get_wheel,
    get_previous_filled,
)
from telegram_wheel_bot.utils import parse_month_label
from telegram_wheel_bot.services.user_service import register_user
from telegram_wheel_bot.services.llm_service import compare_wheels, markdown_to_html
from telegram_wheel_bot.services.visualization import (
    draw_wheel_comparison,
    draw_wheel_new,
)


async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message:
        return
    # Регистрируем/получаем пользователя в базе данных
    db_user = register_user(user.id, user.username, user.first_name)
    wheels = get_history(db_user.id)
    try:
        wheels.sort(key=lambda w: parse_month_label(w.name))
    except Exception:
        pass
    if not wheels:
        await update.message.reply_text("История пуста")
        return
    buttons = [
        [
            InlineKeyboardButton(
                f"{w.name} ({w.created_at.date()})", callback_data=f"hist:{w.id}"
            )
        ]
        for w in wheels
    ]
    await update.message.reply_text(
        "Твоя история колес:", reply_markup=InlineKeyboardMarkup(buttons)
    )


async def open_wheel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    wheel_id = int(q.data.split(":")[1])
    w = get_wheel(wheel_id)
    if not w:
        await q.edit_message_text("Колесо не найдено")
        return
    await q.message.reply_text(w.name)
    # Запоминаем последнее открытое колесо для командного сравнения
    context.user_data["last_open_wheel_id"] = wheel_id

    # Рисуем картинку с новым стилем
    try:
        scores = get_scores(wheel_id)
        ordered = list(scores.items())
        path = draw_wheel_new(wheel_id, ordered)
        await q.message.reply_photo(photo=open(path, "rb"))
    except Exception:
        # Если не удалось, попробуем показать старую картинку, если она есть
        legacy_path = f"wheels/wheel_{wheel_id}.png"
        try:
            await q.message.reply_photo(photo=open(legacy_path, "rb"))
        except Exception:
            pass
    if w.llm_analysis:
        # Конвертируем markdown в HTML для совместимости со старыми сообщениями
        html_analysis = markdown_to_html(w.llm_analysis)
        await q.message.reply_text(html_analysis, parse_mode=ParseMode.HTML)
    prev_filled = get_previous_filled(w.user_id)
    if prev_filled:
        if prev_filled.id == w.id:
            await q.message.reply_text("Не могу сравнить месяц сам с собой")
        else:
            await q.message.reply_text(
                "/compare - Сравнить с последним",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Сравнить с последним",
                                callback_data=f"cmp:{w.id}:{prev_filled.id}",
                            )
                        ]
                    ]
                ),
            )


async def compare_latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    _, a, b = q.data.split(":")
    wid1 = int(a)
    wid2 = int(b)
    w1 = get_wheel(wid1)
    w2 = get_wheel(wid2)
    s1 = get_scores(wid1)
    s2 = get_scores(wid2)
    path = draw_wheel_comparison(
        wid1,
        wid2,
        s1,
        s2,
        w1.name if w1 else "Выбранное",
        w2.name if w2 else "Последнее",
    )
    await q.message.reply_photo(photo=open(path, "rb"))

    # Запрос к LLM для анализа сравнения
    await q.message.reply_text(
        "Формирую результаты сравнения, мне нужно немного времени... "
    )
    date_1 = w1.created_at.date().strftime("%d.%m.%Y") if w1 else ""
    date_2 = w2.created_at.date().strftime("%d.%m.%Y") if w2 else ""
    try:
        analysis = await compare_wheels(s2, s1, date_2, date_1)
        html_analysis = markdown_to_html(analysis)
        await q.message.reply_text(html_analysis, parse_mode=ParseMode.HTML)
    except Exception as e:
        await q.message.reply_text(f"Не удалось получить анализ сравнения: {e}")


def build_callbacks():
    return [
        CallbackQueryHandler(open_wheel, pattern=r"^hist:\d+$"),
        CallbackQueryHandler(compare_latest, pattern=r"^cmp:\d+:\d+$"),
    ]


async def compare_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message:
        return
    db_user = register_user(user.id, user.username, user.first_name)

    # Определяем выбранное колесо: последнее открытое через /history,
    # либо берем два последних колеса пользователя
    current_id = context.user_data.get("last_open_wheel_id")
    prev_filled = get_previous_filled(db_user.id)

    wid1 = None
    wid2 = None
    if current_id and prev_filled and prev_filled.id != current_id:
        wid1 = current_id
        wid2 = prev_filled.id
    elif current_id and prev_filled and prev_filled.id == current_id:
        await update.message.reply_text("Не могу сравнить месяц сам с собой")
        return
    else:
        if not prev_filled:
            await update.message.reply_text("Недостаточно данных для сравнения")
            return
        wheels = get_history(db_user.id)
        # Найти самое последнее колесо, отличное от предыдущего месяца
        alt = next((w for w in wheels if w.id != prev_filled.id), None)
        if not alt:
            await update.message.reply_text("Недостаточно данных для сравнения")
            return
        wid1 = alt.id
        wid2 = prev_filled.id

    w1 = get_wheel(wid1)
    w2 = get_wheel(wid2)
    s1 = get_scores(wid1)
    s2 = get_scores(wid2)
    path = draw_wheel_comparison(
        wid1,
        wid2,
        s1,
        s2,
        w1.name if w1 else "Выбранное",
        w2.name if w2 else "Последнее",
    )
    try:
        await update.message.reply_photo(photo=open(path, "rb"))
    except Exception:
        await update.message.reply_text("Не удалось построить сравнение")
        return

    # Запрос к LLM для анализа сравнения
    await update.message.reply_text(
        "Формирую результаты сравнения, мне нужно немного времени... "
    )
    date_1 = w1.created_at.date().strftime("%d.%m.%Y") if w1 else ""
    date_2 = w2.created_at.date().strftime("%d.%m.%Y") if w2 else ""
    try:
        analysis = await compare_wheels(s2, s1, date_2, date_1)
        html_analysis = markdown_to_html(analysis)
        await update.message.reply_text(html_analysis, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"Не удалось получить анализ сравнения: {e}")
