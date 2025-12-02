from telegram_wheel_bot.database.repository import list_user_wheels, get_latest_wheel, get_wheel_scores, get_wheel_by_id


def get_history(user_id: int):
    return list_user_wheels(user_id)


def get_latest(user_id: int):
    return get_latest_wheel(user_id)


def get_scores(wheel_id: int):
    return get_wheel_scores(wheel_id)


def get_wheel(wheel_id: int):
    return get_wheel_by_id(wheel_id)
