"""Configuration loaded from environment variables and .env files."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env.bot.secret file lives in the project root, one level above bot/
_project_root = Path(__file__).resolve().parent.parent
_env_secret = _project_root / ".env.bot.secret"


class Settings(BaseSettings):
    """Application settings loaded from environment / .env files."""

    model_config = SettingsConfigDict(
        env_file=(str(_env_secret), ".env.bot"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = ""
    lms_api_base_url: str = ""
    lms_api_key: str = ""
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = "coder-model"


settings = Settings()
