from datetime import datetime, timedelta


def get_previous_month_year() -> tuple[str, int]:
    today = datetime.utcnow()
    first = today.replace(day=1)
    prev_last = first - timedelta(days=1)
    months = [
        "январь",
        "февраль",
        "март",
        "апрель",
        "май",
        "июнь",
        "июль",
        "август",
        "сентябрь",
        "октябрь",
        "ноябрь",
        "декабрь",
    ]
    return months[prev_last.month - 1], prev_last.year


def default_wheel_name() -> str:
    m, y = get_previous_month_year()
    return f"за {m} {y}"
