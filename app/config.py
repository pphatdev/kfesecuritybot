import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # `compound-beta` is Groq's agentic model with built-in web search — it
    # decides per-request whether to search, giving Gemini-Search-style answers
    # with citations. Override in .env with any Groq model id if desired.
    GROQ_MODEL = os.getenv("GROQ_MODEL", "compound-beta")
    DASHBOARD_ADMINS = os.getenv("DASHBOARD_ADMINS")
    DASHBOARD_ADMIN_IDS = os.getenv("DASHBOARD_ADMIN_IDS")

config = Config()
