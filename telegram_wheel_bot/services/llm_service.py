import httpx
import re
from telegram_wheel_bot.config import OLLAMA_URL, OLLAMA_MODEL, PROMPTS_DIR


def format_scores(scores: dict[str, int]) -> str:
    return "\n".join([f"{k}: {v}/10" for k, v in scores.items()])


def clean_text(text: str) -> str:
    """Очищает текст от markdown code blocks и лишних символов."""
    # Удаляем markdown code blocks в начале (```html, ```markdown, ``` и т.д.)
    text = re.sub(r'^```\w*\s*\n?', '', text, flags=re.MULTILINE)
    # Удаляем закрывающие ``` в конце
    text = re.sub(r'\n?```\s*$', '', text, flags=re.MULTILINE)
    # Удаляем если остались в начале/конце после strip
    text = text.strip()
    # Дополнительная проверка и очистка
    while text.startswith('```'):
        # Удаляем открывающий блок с любым языком
        text = re.sub(r'^```\w*\s*\n?', '', text)
        text = text.strip()
    while text.endswith('```'):
        # Удаляем закрывающий блок
        text = re.sub(r'\n?```\s*$', '', text)
        text = text.strip()
    return text.strip()


def markdown_to_html(text: str) -> str:
    """Конвертирует markdown в HTML для Telegram."""
    # Сначала очищаем от code blocks
    text = clean_text(text)
    # Заменяем заголовки ## на жирный текст
    text = re.sub(r'^##\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
    # Заменяем **текст** на <b>текст</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Заменяем маркеры списка - на •
    text = re.sub(r'^-\s+', '• ', text, flags=re.MULTILINE)
    return text


async def analyze_wheel_with_ollama(scores: dict[str, int]) -> str:
    formatted_scores = format_scores(scores)
    try:
        with open(f"{PROMPTS_DIR}/wheel_analysis.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
        prompt = prompt_template.format(wheel_scores_formatted=formatted_scores)
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
        if response.status_code != 200:
            return f"Ошибка анализа: HTTP {response.status_code}: {response.text}"
        try:
            data = response.json()
        except Exception:
            return response.text
        return data.get("response", "Ошибка анализа")
    except Exception as e:
        return f"Ошибка анализа: {type(e).__name__}: {e}"


async def compare_wheels_with_ollama(scores_1: dict[str, int], scores_2: dict[str, int], date_1: str, date_2: str) -> str:
    f1 = format_scores(scores_1)
    f2 = format_scores(scores_2)
    try:
        with open(f"{PROMPTS_DIR}/comparison.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
        prompt = prompt_template.format(
            date_1=date_1, date_2=date_2, wheel_scores_1_formatted=f1, wheel_scores_2_formatted=f2
        )
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "top_p": 0.9},
                },
            )
        if response.status_code != 200:
            return f"Ошибка анализа: HTTP {response.status_code}: {response.text}"
        try:
            data = response.json()
        except Exception:
            return response.text
        return data.get("response", "Ошибка анализа")
    except Exception as e:
        return f"Ошибка анализа: {type(e).__name__}: {e}"
