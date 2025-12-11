from telegram_wheel_bot.database.repository import (
    create_wheel_with_categories,
    update_wheel_analysis,
    get_wheel_scores,
)
from telegram_wheel_bot.services.visualization import draw_wheel, draw_wheel_new
from telegram_wheel_bot.services.llm_service import analyze_wheel


async def create_and_analyze_wheel(
    user_id: int, name: str, scores: dict[str, int]
) -> tuple[int, str | None, str]:
    ordered = [
        ("Семья", scores.get("Семья", 0)),
        ("Друзья", scores.get("Друзья", 0)),
        ("Здоровье", scores.get("Здоровье", 0)),
        ("Хобби", scores.get("Хобби", 0)),
        ("Деньги", scores.get("Деньги", 0)),
        ("Отдых", scores.get("Отдых", 0)),
        ("Личное развитие", scores.get("Личное развитие", 0)),
        ("Работа/бизнес", scores.get("Работа/бизнес", 0)),
    ]
    wheel = create_wheel_with_categories(user_id, name, ordered)
    legacy_img = None
    try:
        legacy_img = draw_wheel(wheel.id, ordered)
    except Exception:
        legacy_img = None
    img = None
    try:
        img = draw_wheel_new(wheel.id, ordered)
    except Exception:
        img = legacy_img
    analysis = await analyze_wheel({k: v for k, v in ordered})
    try:
        update_wheel_analysis(wheel.id, analysis)
    except Exception:
        pass
    return wheel.id, img, analysis


def get_wheel_scores_dict(wheel_id: int) -> dict[str, int]:
    return get_wheel_scores(wheel_id)
