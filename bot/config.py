"""
Configuration loader for the bot.

Loads settings from .env.bot.secret using pydantic-settings.
This pattern loads secrets from environment files.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram bot token
    bot_token: str = ""

    # LMS API settings
    lms_api_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API settings
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = ""


def load_config() -> BotSettings:
    """Load and return bot configuration."""
    return BotSettings()
