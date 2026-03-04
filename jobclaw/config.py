"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the JobClaw agent."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    jobclaw_env: str = Field(default="development")
    jobclaw_log_level: str = Field(default="INFO")
    jobclaw_headless: bool = Field(default=True)
    jobclaw_max_jobs: int = Field(default=30, ge=1, le=500)
    jobclaw_request_timeout: int = Field(default=30, ge=5, le=300)

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    jobclaw_llm_model: str = Field(default="gpt-4o-mini")

    boss_cookie: str | None = None
    linkedin_cookie: str | None = None

    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    discord_webhook_url: str | None = None

    http_proxy: str | None = None
    https_proxy: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
