"""Configuración central de la aplicación cargada desde variables de entorno."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parámetros de configuración de la plataforma.

    Los valores se leen de variables de entorno o del archivo `.env`.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./ecommerce.db"
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300
    payment_default_scenario: str = "approved"


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración cacheada (singleton por proceso)."""
    return Settings()
