"""Application configuration."""

from functools import lru_cache

from pydantic import Field, field_validator
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
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    export_artifact_dir: str = Field(
        default="/tmp/storyforge-exports", validation_alias="STORYFORGE_EXPORT_ARTIFACT_DIR"
    )
    export_sync: bool = Field(default=False, validation_alias="STORYFORGE_EXPORT_SYNC")
    export_queue_name: str = "storyforge:export_jobs"

    @field_validator("export_sync", mode="before")
    @classmethod
    def parse_export_sync(cls, value: object) -> bool:
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)


@lru_cache
def get_settings() -> Settings:
    return Settings()
