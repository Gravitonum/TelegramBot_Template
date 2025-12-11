import httpx
import re
import json
from telegram_wheel_bot.config import (
    OLLAMA_URL,
    OLLAMA_MODEL,
    PROMPTS_DIR,
    OPENAI_BASE_URL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    LLM_DEFAULT_PROVIDER,
)


def format_scores(scores: dict[str, int]) -> str:
    return "\n".join([f"{k}: {v}/10" for k, v in scores.items()])


def clean_text(text: str) -> str:
    """Очищает текст от markdown code blocks и лишних символов."""
    # Удаляем markdown code blocks в начале (```html, ```markdown, ``` и т.д.)
    text = re.sub(r"^```\w*\s*\n?", "", text, flags=re.MULTILINE)
    # Удаляем закрывающие ``` в конце
    text = re.sub(r"\n?```\s*$", "", text, flags=re.MULTILINE)
    # Удаляем если остались в начале/конце после strip
    text = text.strip()
    # Дополнительная проверка и очистка
    while text.startswith("```"):
        # Удаляем открывающий блок с любым языком
        text = re.sub(r"^```\w*\s*\n?", "", text)
        text = text.strip()
    while text.endswith("```"):
        # Удаляем закрывающий блок
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()
    return text.strip()


def markdown_to_html(text: str) -> str:
    """Конвертирует markdown в HTML для Telegram."""
    # Сначала очищаем от code blocks
    text = clean_text(text)
    # Заменяем заголовки ## на жирный текст
    text = re.sub(r"^##\s+(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    # Заменяем **текст** на <b>текст</b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Заменяем маркеры списка - на •
    text = re.sub(r"^-\s+", "• ", text, flags=re.MULTILINE)
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


async def compare_wheels_with_ollama(
    scores_1: dict[str, int], scores_2: dict[str, int], date_1: str, date_2: str
) -> str:
    f1 = format_scores(scores_1)
    f2 = format_scores(scores_2)
    try:
        with open(f"{PROMPTS_DIR}/comparison.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
        prompt = prompt_template.format(
            date_1=date_1,
            date_2=date_2,
            wheel_scores_1_formatted=f1,
            wheel_scores_2_formatted=f2,
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


async def analyze_wheel_with_openai(scores: dict[str, int], model: str | None = None) -> str:
    formatted_scores = format_scores(scores)
    try:
        with open(f"{PROMPTS_DIR}/wheel_analysis.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
        prompt = prompt_template.format(wheel_scores_formatted=formatted_scores)

        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            response = await client.post(
                f"{OPENAI_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": model or OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
            )

        if response.status_code != 200:
            return f"Ошибка анализа: HTTP {response.status_code}: {response.text}"

        try:
            data = response.json()
            return (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "Ошибка анализа")
            )
        except Exception:
            return response.text
    except Exception as e:
        return f"Ошибка анализа: {type(e).__name__}: {e}"


async def compare_wheels_with_openai(
    scores_1: dict[str, int], scores_2: dict[str, int], date_1: str, date_2: str
) -> str:
    f1 = format_scores(scores_1)
    f2 = format_scores(scores_2)
    try:
        with open(f"{PROMPTS_DIR}/comparison.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
        prompt = prompt_template.format(
            date_1=date_1,
            date_2=date_2,
            wheel_scores_1_formatted=f1,
            wheel_scores_2_formatted=f2,
        )

        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            response = await client.post(
                f"{OPENAI_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
            )

        if response.status_code != 200:
            return f"Ошибка анализа: HTTP {response.status_code}: {response.text}"

        try:
            data = response.json()
            return (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "Ошибка анализа")
            )
        except Exception:
            return response.text
    except Exception as e:
        return f"Ошибка анализа: {type(e).__name__}: {e}"


# Provider selection functions
async def analyze_wheel(scores: dict[str, int]) -> str:
    if LLM_DEFAULT_PROVIDER == "openai":
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                models_resp = await client.get(
                    f"{OPENAI_BASE_URL}/models",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                )
            openai_accessible = models_resp.status_code == 200
        except Exception:
            openai_accessible = False

        if openai_accessible:
            r = await analyze_wheel_with_openai(scores)
            if r.startswith("Ошибка анализа:"):
                try:
                    data = models_resp.json()
                except Exception:
                    data = {}
                names = []
                if isinstance(data, dict):
                    if isinstance(data.get("data"), list):
                        for m in data["data"]:
                            n = m.get("id") or m.get("name")
                            if isinstance(n, str):
                                names.append(n)
                    elif isinstance(data.get("models"), list):
                        for m in data["models"]:
                            n = m.get("id") or m.get("name")
                            if isinstance(n, str):
                                names.append(n)
                free_model = next((n for n in names if n.endswith(":free")), None)
                if free_model:
                    return await analyze_wheel_with_openai(scores, free_model)
                return r
            return r
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                ollama_resp = await client.get(f"{OLLAMA_URL}/api/tags")
            ollama_accessible = ollama_resp.status_code == 200
        except Exception:
            ollama_accessible = False
        if ollama_accessible:
            return await analyze_wheel_with_ollama(scores)
        return "Ошибка анализа: LLM сервис недоступен"
    else:
        return await analyze_wheel_with_ollama(scores)


async def compare_wheels(
    scores_1: dict[str, int], scores_2: dict[str, int], date_1: str, date_2: str
) -> str:
    if LLM_DEFAULT_PROVIDER == "openai":
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                models_resp = await client.get(
                    f"{OPENAI_BASE_URL}/models",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                )
            openai_accessible = models_resp.status_code == 200
        except Exception:
            openai_accessible = False

        if openai_accessible:
            r = await compare_wheels_with_openai(scores_1, scores_2, date_1, date_2)
            if r.startswith("Ошибка анализа:"):
                try:
                    data = models_resp.json()
                except Exception:
                    data = {}
                names = []
                if isinstance(data, dict):
                    if isinstance(data.get("data"), list):
                        for m in data["data"]:
                            n = m.get("id") or m.get("name")
                            if isinstance(n, str):
                                names.append(n)
                    elif isinstance(data.get("models"), list):
                        for m in data["models"]:
                            n = m.get("id") or m.get("name")
                            if isinstance(n, str):
                                names.append(n)
                free_model = next((n for n in names if n.endswith(":free")), None)
                if free_model:
                    try:
                        formatted_f1 = format_scores(scores_1)
                        formatted_f2 = format_scores(scores_2)
                        with open(f"{PROMPTS_DIR}/comparison.txt", "r", encoding="utf-8") as f:
                            prompt_template = f.read()
                        prompt = prompt_template.format(
                            date_1=date_1,
                            date_2=date_2,
                            wheel_scores_1_formatted=formatted_f1,
                            wheel_scores_2_formatted=formatted_f2,
                        )
                        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
                            resp2 = await client.post(
                                f"{OPENAI_BASE_URL}/chat/completions",
                                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                                json={
                                    "model": free_model,
                                    "messages": [{"role": "user", "content": prompt}],
                                    "temperature": 0.7,
                                },
                            )
                        if resp2.status_code == 200:
                            try:
                                j = resp2.json()
                                return (
                                    j.get("choices", [{}])[0]
                                    .get("message", {})
                                    .get("content", "Ошибка анализа")
                                )
                            except Exception:
                                return resp2.text
                        return f"Ошибка анализа: HTTP {resp2.status_code}: {resp2.text}"
                    except Exception as e:
                        return f"Ошибка анализа: {type(e).__name__}: {e}"
                return r
            return r
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                ollama_resp = await client.get(f"{OLLAMA_URL}/api/tags")
            ollama_accessible = ollama_resp.status_code == 200
        except Exception:
            ollama_accessible = False
        if ollama_accessible:
            return await compare_wheels_with_ollama(scores_1, scores_2, date_1, date_2)
        return "Ошибка анализа: LLM сервис недоступен"
    else:
        return await compare_wheels_with_ollama(scores_1, scores_2, date_1, date_2)
