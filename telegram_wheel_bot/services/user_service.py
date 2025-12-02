from telegram_wheel_bot.database.repository import get_or_create_user


def register_user(telegram_id: int, username: str | None, first_name: str | None):
    return get_or_create_user(telegram_id, username, first_name)
