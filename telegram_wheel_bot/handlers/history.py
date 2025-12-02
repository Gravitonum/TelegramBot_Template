from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram_wheel_bot.services.history_service import get_history, get_latest, get_scores, get_wheel
from telegram_wheel_bot.services.visualization import draw_wheel_comparison


async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    wheels = get_history(user.id)
    if not wheels:
        await update.message.reply_text("История пуста")
        return
    buttons = [[InlineKeyboardButton(f"{w.name} ({w.created_at.date()})", callback_data=f"hist:{w.id}")] for w in wheels]
    await update.message.reply_text("Твоя история колес:", reply_markup=InlineKeyboardMarkup(buttons))


async def open_wheel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    wheel_id = int(q.data.split(":")[1])
    w = get_wheel(wheel_id)
    if not w:
        await q.edit_message_text("Колесо не найдено")
        return
    path = f"wheels/wheel_{wheel_id}.png"
    try:
        await q.message.reply_photo(photo=open(path, "rb"))
    except Exception:
        pass
    if w.llm_analysis:
        await q.message.reply_text(w.llm_analysis)
    latest = get_latest(w.user_id)
    if latest and latest.id != w.id:
        await q.message.reply_text("/Сравнить_с_последним", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Сравнить с последним", callback_data=f"cmp:{w.id}:{latest.id}")]]))


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
    path = draw_wheel_comparison(wid1, wid2, s1, s2, w1.name if w1 else "Выбранное", w2.name if w2 else "Последнее")
    await q.message.reply_photo(photo=open(path, "rb"))


def build_callbacks():
    return [
        CallbackQueryHandler(open_wheel, pattern=r"^hist:\d+$"),
        CallbackQueryHandler(compare_latest, pattern=r"^cmp:\d+:\d+$"),
    ]
