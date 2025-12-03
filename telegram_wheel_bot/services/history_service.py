from telegram_wheel_bot.database.repository import list_user_wheels, get_latest_wheel, get_wheel_scores, get_wheel_by_id
from telegram_wheel_bot.utils import parse_month_label, previous_month_label


def get_history(user_id: int):
    return list_user_wheels(user_id)


def get_latest(user_id: int):
    return get_latest_wheel(user_id)


def get_scores(wheel_id: int):
    return get_wheel_scores(wheel_id)


def get_wheel(wheel_id: int):
    return get_wheel_by_id(wheel_id)


def get_previous_filled(user_id: int):
    """Find the wheel for the previous calendar month relative to today."""
    wheels = list_user_wheels(user_id)
    try:
        target_date = parse_month_label(previous_month_label())
    except Exception:
        target_date = None
    if not target_date:
        return None
    for w in wheels:
        try:
            d = parse_month_label(w.name)
        except Exception:
            continue
        if d == target_date:
            return w
    return None
