import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DASHBOARD_ADMINS = os.getenv("DASHBOARD_ADMINS")
    DASHBOARD_ADMIN_IDS = os.getenv("DASHBOARD_ADMIN_IDS")

config = Config()
