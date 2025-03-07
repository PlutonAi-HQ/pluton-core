import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    BASE_URL = os.getenv("BASE_URL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    REDIS_URI = os.getenv("REDIS_URI")
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))
    RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", 5))
    FILE_PREFIX = os.getenv("FILE_PREFIX", "pluton_")
    SEARXNG_HOST = os.getenv("SEARXNG_HOST")
    SERVICE_JUPITER_BASE_URL = os.getenv("SERVICE_JUPITER_BASE_URL")

    @property
    def origins(self):
        return os.getenv("ALLOWED_ORIGINS", "*")

    WALLET_API_URL = os.getenv("WALLET_API_URL")
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


settings = Settings()
