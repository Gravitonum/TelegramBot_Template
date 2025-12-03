from datetime import datetime, timedelta, date


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


MONTHS_RU = [
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


def _year_short(y: int) -> str:
    return str(y % 100)


def previous_month_label() -> str:
    m, y = get_previous_month_year()
    return f"{m} {_year_short(y)}"


def last_three_months_labels(today: datetime | None = None) -> list[str]:
    t = today or datetime.utcnow()
    first = t.replace(day=1)
    labels: list[str] = []
    dt = first - timedelta(days=1)
    for _ in range(3):
        m_name = MONTHS_RU[dt.month - 1]
        labels.append(f"{m_name} {_year_short(dt.year)}")
        dt = (dt.replace(day=1) - timedelta(days=1))
    return labels


def parse_month_label(label: str) -> date:
    s = label.strip().lower()
    parts = s.split()
    if not parts:
        raise ValueError("empty label")
    if parts[0] == "за" and len(parts) >= 3:
        month_name = parts[1]
        year_part = parts[2]
    elif len(parts) >= 2:
        month_name = parts[0]
        year_part = parts[1]
    else:
        raise ValueError("invalid label format")
    try:
        m_idx = MONTHS_RU.index(month_name) + 1
    except ValueError:
        raise ValueError("unknown month name")
    if not year_part.isdigit():
        raise ValueError("year is not numeric")
    y = int(year_part)
    if len(year_part) == 2:
        y = 2000 + y
    return date(y, m_idx, 1)
