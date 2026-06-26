from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SignalCraft"
    environment: str = "local"
    database_url: str = "sqlite:///./signalcraft.db"
    redis_url: str = "redis://localhost:6379/0"

    llm_provider: str = "openai"
    llm_model: str = "gpt-4.1-mini"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    phone_provider: str = "console"
    approval_phone_number: str | None = None
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_from_number: str | None = None

    youtube_api_key: str | None = None
    enable_live_collection: bool = False
    enable_browser_scraping: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
