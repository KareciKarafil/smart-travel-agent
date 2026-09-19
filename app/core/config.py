from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart Travel Agent API"
    app_version: str = "0.1.0"
    debug: bool = False

    openai_api_key: str | None = None
    openai_model: str | None = None
    open_meteo_geocoding_url: str = (
    "https://geocoding-api.open-meteo.com/v1/search"
)
    external_api_timeout_seconds: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()