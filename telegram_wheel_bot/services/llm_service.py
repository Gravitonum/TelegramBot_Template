import httpx
from telegram_wheel_bot.config import OLLAMA_URL, OLLAMA_MODEL, PROMPTS_DIR


def format_scores(scores: dict[str, int]) -> str:
    return "\n".join([f"{k}: {v}/10" for k, v in scores.items()])


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
