import asyncio
import httpx
from telegram_wheel_bot.services.llm_service import analyze_wheel_with_ollama, format_scores
from telegram_wheel_bot.config import OLLAMA_URL, OLLAMA_MODEL, PROMPTS_DIR


async def run():
    scores = {
        "Семья": 3,
        "Друзья": 3,
        "Здоровье": 3,
        "Хобби": 3,
        "Деньги": 6,
        "Отдых": 5,
        "Личное развитие": 8,
        "Работа/бизнес": 8,
    }
    result = await analyze_wheel_with_ollama(scores)
    if result == "Ошибка анализа":
        formatted_scores = format_scores(scores)
        with open(f"{PROMPTS_DIR}/wheel_analysis.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
        prompt = prompt_template.format(wheel_scores_formatted=formatted_scores)
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
                response = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
                )
            if response.status_code != 200:
                print(f"HTTP {response.status_code}: {response.text}")
                return
            try:
                data = response.json()
            except Exception:
                print(response.text)
                return
            print(data.get("response", "Ошибка анализа"))
            return
        except Exception as e:
            print(f"Ошибка анализа: {type(e).__name__}: {e}")
            return
    print(result)


if __name__ == "__main__":
    asyncio.run(run())

