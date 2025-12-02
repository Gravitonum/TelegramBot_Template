from telegram import Update
from telegram.ext import ContextTypes
from telegram_wheel_bot.config import ADMIN_IDS
from telegram_wheel_bot.database.repository import SessionLocal
from telegram_wheel_bot.database.models import User, Wheel, WheelCategory


async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ У тебя нет прав на эту команду")
        return
    with SessionLocal() as session:
        u = session.query(User).filter(User.telegram_id == user.id).first()
        if u:
            session.query(WheelCategory).filter(WheelCategory.wheel_id.in_(session.query(Wheel.id).filter(Wheel.user_id == u.id))).delete(synchronize_session=False)
            session.query(Wheel).filter(Wheel.user_id == u.id).delete(synchronize_session=False)
            session.delete(u)
            session.commit()
    await update.message.reply_text("✓ Все данные удалены")
