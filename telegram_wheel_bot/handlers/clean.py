from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from telegram_wheel_bot.services.history_service import get_history
from telegram_wheel_bot.database.repository import delete_wheels_by_ids, delete_all_user_wheels, log_user_action
from telegram_wheel_bot.services.user_service import register_user
from telegram_wheel_bot.config import WHEELS_DIR
import os
import logging

logger = logging.getLogger(__name__)


async def clean_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("clean_cmd: Handler called!")
    try:
        user = update.effective_user
        if not user:
            logger.error("clean_cmd: effective_user is None")
            return
        
        if not update.message:
            logger.error("clean_cmd: update.message is None")
            return
        
        logger.info(f"clean_cmd: Processing command from user {user.id}")
        
        # Регистрируем/получаем пользователя в базе данных
        db_user = register_user(user.id, user.username, user.first_name)
        logger.info(f"clean_cmd: User {user.id} (db_id: {db_user.id}) called /clean")
        
        # Получаем колеса пользователя по database user_id
        wheels = get_history(db_user.id)
        
        if not wheels:
            await update.message.reply_text("У вас нет колес для удаления")
            logger.info(f"clean_cmd: User {user.id} has no wheels")
            return
        
        buttons = []
        for w in wheels:
            buttons.append([InlineKeyboardButton(f"{w.name} ({w.created_at.date()})", callback_data=f"clean_sel:{w.id}")])
        buttons.append([InlineKeyboardButton("все колеса", callback_data="clean_sel:all")])
        
        await update.message.reply_text("Выберите колесо для удаления", reply_markup=InlineKeyboardMarkup(buttons))
        logger.info(f"clean_cmd: User {user.id} shown {len(wheels)} wheels for deletion")
    except Exception as e:
        logger.error(f"clean_cmd error: {e}", exc_info=True)
        if update.message:
            await update.message.reply_text("Произошла ошибка при выполнении команды. Попробуйте позже.")


async def select_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query
        if not q:
            logger.error("select_target: callback_query is None")
            return
        
        await q.answer()
        target = q.data.split(":")[1]
        
        logger.info(f"select_target: User selected target {target}")
        
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Да", callback_data=f"clean_conf:{target}:yes"),
                InlineKeyboardButton("Нет", callback_data=f"clean_conf:{target}:no"),
            ]
        ])
        await q.edit_message_text("Вы точно желаете удалить данные? Их невозможно будет восстановить!", reply_markup=kb)
    except Exception as e:
        logger.error(f"select_target error: {e}", exc_info=True)
        if update.callback_query:
            await update.callback_query.answer("Произошла ошибка", show_alert=True)


def _remove_wheel_images(wheel_ids: list[int]) -> None:
    for wid in wheel_ids:
        for name in [f"wheel_{wid}.png", f"wheel_new_{wid}.png"]:
            path = os.path.join(WHEELS_DIR, name)
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query
        if not q:
            logger.error("confirm_delete: callback_query is None")
            return
        
        await q.answer()
        _, target, decision = q.data.split(":")
        
        user = update.effective_user
        if not user:
            logger.error("confirm_delete: effective_user is None")
            await q.edit_message_text("Ошибка: пользователь не найден")
            return
        
        # Регистрируем/получаем пользователя в базе данных
        db_user = register_user(user.id, user.username, user.first_name)
        logger.info(f"confirm_delete: User {user.id} (db_id: {db_user.id}) decision={decision}, target={target}")
        
        if decision == "no":
            await q.edit_message_text("Отменено")
            logger.info(f"confirm_delete: User {user.id} cancelled deletion")
            return
        
        if target == "all":
            wheels = get_history(db_user.id)
            ids = [w.id for w in wheels]
            _remove_wheel_images(ids)
            count = delete_all_user_wheels(db_user.id)
            log_user_action(db_user.id, "delete_all_wheels", f"count={count}")
            await q.edit_message_text("✓ Все колеса удалены")
            logger.info(f"confirm_delete: User {user.id} deleted all {count} wheels")
            return
        
        try:
            wid = int(target)
        except ValueError:
            logger.error(f"confirm_delete: Invalid wheel_id format: {target}")
            await q.edit_message_text("Ошибка выбора")
            return
        
        _remove_wheel_images([wid])
        deleted = delete_wheels_by_ids(db_user.id, [wid])
        if deleted:
            log_user_action(db_user.id, "delete_wheel", wheel_id=wid)
            await q.edit_message_text("✓ Колесо удалено")
            logger.info(f"confirm_delete: User {user.id} deleted wheel {wid}")
        else:
            await q.edit_message_text("Колесо не найдено")
            logger.warning(f"confirm_delete: User {user.id} tried to delete non-existent wheel {wid}")
    except Exception as e:
        logger.error(f"confirm_delete error: {e}", exc_info=True)
        if update.callback_query:
            await update.callback_query.answer("Произошла ошибка при удалении", show_alert=True)


def build_clean_handlers():
    return [
        CallbackQueryHandler(select_target, pattern=r"^clean_sel:(\d+|all)$"),
        CallbackQueryHandler(confirm_delete, pattern=r"^clean_conf:(\d+|all):(yes|no)$"),
        CommandHandler("clean", clean_cmd),
        CommandHandler("clear", clean_cmd),
    ]
