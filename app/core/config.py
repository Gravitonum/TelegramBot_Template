"""
Конфигурация приложения.
Загружает переменные окружения из файла .env
"""

import os
from pathlib import Path

# Путь к корневой директории проекта
BASE_DIR = Path(__file__).parent.parent.parent

# Загрузка переменных окружения из .env файла
def load_env_file():
    """Загружает переменные окружения из файла .env в корне проекта."""
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

# Загружаем переменные окружения
load_env_file()

class Settings:
    """Настройки приложения."""

    # Токен Telegram-бота
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # Уровень логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Экземпляр настроек
settings = Settings()