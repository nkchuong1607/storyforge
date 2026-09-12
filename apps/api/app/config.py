"""Application configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    database_url: str = "postgresql+asyncpg://storyforge:storyforge@localhost:5432/storyforge"
    app_title: str = "StoryForge API"
    app_version: str = "0.2.0-phase1"
    llm_provider: str = Field(default="fake", validation_alias="STORYFORGE_LLM_PROVIDER")
    litellm_model: str | None = Field(default=None, validation_alias="LITELLM_MODEL")
    litellm_api_base: str | None = Field(default=None, validation_alias="LITELLM_API_BASE")
    llm_timeout_sec: int = Field(default=60, validation_alias="STORYFORGE_LLM_TIMEOUT_SEC")
    llm_max_output_tokens: int = Field(
        default=4096, validation_alias="STORYFORGE_LLM_MAX_OUTPUT_TOKENS"
    )
    prompt_edit_rate_limit_per_hour: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
