from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./sinapi-dev.db"
    api_key_pepper: str = "dev-pepper"
    caixa_search_url: str = "https://www.caixa.gov.br/_api/search/query"
    caixa_download_timeout_seconds: int = 120
    sync_storage_dir: str = "./.sync-storage"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
