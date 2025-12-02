from telegram_wheel_bot.database.repository import create_wheel_with_categories, update_wheel_analysis, get_wheel_scores
from telegram_wheel_bot.services.visualization import draw_wheel
from telegram_wheel_bot.services.llm_service import analyze_wheel_with_ollama


async def create_and_analyze_wheel(user_id: int, name: str, scores: dict[str, int]) -> tuple[int, str, str]:
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
    image_path = draw_wheel(wheel.id, ordered)
    analysis = await analyze_wheel_with_ollama({k: v for k, v in ordered})
    update_wheel_analysis(wheel.id, analysis)
    return wheel.id, image_path, analysis


def get_wheel_scores_dict(wheel_id: int) -> dict[str, int]:
    return get_wheel_scores(wheel_id)
