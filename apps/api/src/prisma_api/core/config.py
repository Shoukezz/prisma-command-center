from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "PRISMA API"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    _default_db_path = Path(__file__).parent.parent.parent.parent / "data" / "prisma.db"
    database_url: str = f"sqlite:///{_default_db_path}"
    secret_key: str = Field(default="dev-secret-change-in-production")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )
    auto_tick: bool = True
    tick_interval_seconds: float = Field(default=15.0, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
