import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    BASE_URL = os.getenv("BASE_URL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    @property
    def origins(self):
        return os.getenv("ALLOWED_ORIGINS", "*")


settings = Settings()
