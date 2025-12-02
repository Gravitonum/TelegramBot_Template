import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///wheel_of_life.db")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://192.168.0.165:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "hhao/qwen2.5-coder-tools:32b")
WHEELS_DIR = os.getenv("WHEELS_DIR", "./wheels")
PROMPTS_DIR = os.getenv("PROMPTS_DIR", os.path.join(BASE_DIR, "prompts"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
