"""Application configuration for KrishiMitra-AI."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "KrishiMitra-AI"
    app_version: str = "0.1.0"
    environment: str = Field(default="development")
    debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"
    api_version: str = "v1"

    # Database
    database_url: str = (
        "postgresql+asyncpg://krishimitra:krishimitra@localhost:5432/krishimitra"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Security
    secret_key: str = Field(
        default="change-me-in-production",
        min_length=16,
    )

    # WhatsApp
    whatsapp_verify_token: str = ""
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_app_secret: str = ""

    # External services
    weather_api_base_url: str = "https://api.open-meteo.com"

    # AI
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Storage
    storage_backend: str = "local"
    storage_bucket: str = "krishimitra"

    # Observability
    log_level: str = "INFO"
    service_name: str = "krishimitra"

    @property
    def is_production(self) -> bool:
        """Return whether the application runs in production mode."""
        return self.environment.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide validated settings instance."""
    return Settings()