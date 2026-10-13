import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
    WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v21.0")

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    SYSTEM_PROMPT = os.getenv(
        "SYSTEM_PROMPT",
        "You are a helpful assistant chatting with a user over WhatsApp. "
        "Keep replies concise and conversational.",
    )

    DB_PATH = os.getenv("DB_PATH", "./data/chatbot.db")
    HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "20"))

    PORT = int(os.getenv("PORT", "8000"))


config = Config()
