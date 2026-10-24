"""Application settings, loaded from environment variables or the .env file."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Secrets: never hard-code these. Put them in .env (which is git-ignored).
    bot_token: str = ""
    bot_mode: str = "polling"  # "polling" (python -m app.bot.main) or "webhook" (the dashboard receives updates)
    webhook_url: str = ""  # public HTTPS base URL, e.g. https://bot.example.com
    webhook_secret: str = ""
    secret_key: str = "change-me"
    ai_api_key: str = ""

    database_url: str = "sqlite+aiosqlite:///./chatbot.db"
    ai_model: str = ""
    ai_base_url: str = "https://openrouter.ai/api/v1"  # any OpenAI-compatible chat API
    ai_timeout: float = 20.0  # seconds
    default_language: str = "en"  # "en" or "km"

    timezone: str = "Asia/Phnom_Penh"  # dashboard times; the database stores UTC
    session_timeout_minutes: int = 30
    secure_cookies: bool = False  # set true when the dashboard is served over HTTPS  # Auto Logout after this much inactivity

    # First admin account, created on first start if there is no admin yet.
    admin_email: str = "admin@example.com"
    admin_password: str = ""  # empty: a random password is generated and printed once


settings = Settings()
