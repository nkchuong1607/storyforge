"""Application configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://storyforge:storyforge@localhost:5432/storyforge"
    app_title: str = "StoryForge API"
    app_version: str = "0.2.0-phase1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
