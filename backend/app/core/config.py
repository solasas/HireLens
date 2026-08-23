from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, sourced entirely from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    app_version: str = "0.1.0"
    project_name: str = "HireLens"
    api_v1_prefix: str = "/api/v1"

    # Comma-separated in the environment (e.g. "http://localhost:5173,http://foo").
    # Kept as a plain str field: pydantic-settings tries to JSON-decode env
    # values for list-typed fields before validators ever run, which breaks
    # on a plain comma-separated string. cors_origins below does the split.
    cors_origins_raw: str = Field(default="", validation_alias="CORS_ORIGINS")

    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str
    db_echo: bool = False

    llm_provider: Literal["openai", "gemini"] = "openai"
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.6-flash"

    embedding_provider: Literal["openai", "gemini"] = "openai"
    gemini_embedding_model: str = "gemini-embedding-2"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        """Async connection string, used by the running application (asyncpg)."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync connection string, used only by Alembic migrations (psycopg)."""
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
