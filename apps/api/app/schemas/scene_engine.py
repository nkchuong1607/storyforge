"""Scene engine and extended beat schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ContinuityResult, SceneType
from app.schemas.continuity import ContinuityIssue

SceneStrictness = Literal["relaxed", "standard", "strict"]


class PressureTag(BaseModel):
    tag: str
    source: str | None = None
    weight: int = Field(default=1, ge=0)


class SceneBeat(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    chapter_id: uuid.UUID
    beat_key: str
    summary: str
    sort_order: int
    completed: bool
    goal: str = ""
    conflict: str = ""
    outcome: str = ""
    stakes_level: int | None = None
    pressure_tags: list[PressureTag] = Field(default_factory=list)
    pov_character_id: uuid.UUID | None = None
    scene_type: SceneType = SceneType.scene
    created_at: datetime
    updated_at: datetime

    @field_validator("goal", "conflict", "outcome", mode="before")
    @classmethod
    def _blank_strings(cls, value: str | None) -> str:
        return value or ""

    @field_validator("pressure_tags", mode="before")
    @classmethod
    def _pressure_tags(cls, value: list | None) -> list:
        return value or []

    @field_validator("scene_type", mode="before")
    @classmethod
    def _scene_type(cls, value: SceneType | str | None) -> SceneType:
        if value is None:
            return SceneType.scene
        return value if isinstance(value, SceneType) else SceneType(value)


class SceneBeatCreateRequest(BaseModel):
    beat_key: str
    summary: str
    sort_order: int = Field(ge=0)
    completed: bool = False
    goal: str = ""
    conflict: str = ""
    outcome: str = ""
    stakes_level: int | None = Field(default=None, ge=0, le=5)
    pressure_tags: list[PressureTag] = Field(default_factory=list)
    pov_character_id: uuid.UUID | None = None
    scene_type: SceneType = SceneType.scene


class SceneBeatUpdateRequest(BaseModel):
    beat_key: str | None = None
    summary: str | None = None
    sort_order: int | None = None
    completed: bool | None = None
    goal: str | None = None
    conflict: str | None = None
    outcome: str | None = None
    stakes_level: int | None = Field(default=None, ge=0, le=5)
    pressure_tags: list[PressureTag] | None = None
    pov_character_id: uuid.UUID | None = None
    scene_type: SceneType | None = None


class SceneBeatListResponse(BaseModel):
    items: list[SceneBeat]


class SceneEngineSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: uuid.UUID
    enabled: bool
    require_conflict: bool
    require_outcome_on_complete: bool
    min_goal_length: int
    llm_auditor_enabled: bool
    strictness: SceneStrictness
    updated_at: datetime


class SceneEngineSettingsUpdateRequest(BaseModel):
    enabled: bool | None = None
    require_conflict: bool | None = None
    require_outcome_on_complete: bool | None = None
    min_goal_length: int | None = Field(default=None, ge=1)
    llm_auditor_enabled: bool | None = None
    strictness: SceneStrictness | None = None


class SceneLintResponse(BaseModel):
    chapter_id: uuid.UUID
    result: ContinuityResult
    issues: list[ContinuityIssue]
    stats: dict[str, int]


class SceneContextPackRequest(BaseModel):
    chapter_id: uuid.UUID
    beat_ids: list[uuid.UUID] = Field(default_factory=list)
    include_empty: bool = False


class SceneContextPackBeat(BaseModel):
    beat_key: str
    goal: str
    conflict: str
    outcome: str
    stakes_level: int | None = None
    pressure_tags: list[PressureTag] = Field(default_factory=list)


class SceneContextPackResponse(BaseModel):
    beats: list[SceneContextPackBeat]
