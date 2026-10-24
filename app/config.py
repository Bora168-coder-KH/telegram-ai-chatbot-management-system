"""Application settings, loaded from environment variables or the .env file."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Secrets: never hard-code these. Put them in .env (which is git-ignored).
    bot_token: str = ""
    secret_key: str = "change-me"
    ai_api_key: str = ""

    database_url: str = "sqlite+aiosqlite:///./chatbot.db"
    ai_model: str = ""
    default_language: str = "en"  # "en" or "km"

    # First admin account, created on first start if there is no admin yet.
    admin_email: str = "admin@example.com"
    admin_password: str = ""  # empty: a random password is generated and printed once


settings = Settings()
