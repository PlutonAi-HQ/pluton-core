import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    BASE_URL = os.getenv("BASE_URL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    REDIS_URI = os.getenv("REDIS_URI")
    RATE_LIMIT_WINDOW = os.getenv("RATE_LIMIT_WINDOW", 60)
    RATE_LIMIT_MAX_REQUESTS = os.getenv("RATE_LIMIT_MAX_REQUESTS", 5)

    @property
    def origins(self):
        return os.getenv("ALLOWED_ORIGINS", "*")


settings = Settings()
