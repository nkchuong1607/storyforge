"""Power system API schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PowerRankSubStage(BaseModel):
    key: str
    display_name: str
    sort_order: int


class PowerRank(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rank_key: str
    display_name: str
    sort_order: int
    sub_stages: list[PowerRankSubStage] = Field(default_factory=list)
    constraints_md: str = ""


class PowerRankListResponse(BaseModel):
    items: list[PowerRank]


class PowerRankCreateRequest(BaseModel):
    rank_key: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    sort_order: int | None = None
    sub_stages: list[PowerRankSubStage] = Field(default_factory=list)
    constraints_md: str = ""


class PowerRankUpdateRequest(BaseModel):
    rank_key: str | None = None
    display_name: str | None = None
    sort_order: int | None = None
    sub_stages: list[PowerRankSubStage] | None = None
    constraints_md: str | None = None


class PowerRankReorderRequest(BaseModel):
    rank_ids: list[uuid.UUID] = Field(min_length=1)


class PowerTechnique(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    technique_key: str
    display_name: str
    min_rank_id: uuid.UUID
    min_rank_display_name: str | None = None
    sect_requirement: str | None = None
    lineage_requirement: str | None = None
    resource_cost: dict[str, Any] = Field(default_factory=dict)
    notes_md: str = ""


class PowerTechniqueListResponse(BaseModel):
    items: list[PowerTechnique]


class PowerTechniqueCreateRequest(BaseModel):
    technique_key: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    min_rank_id: uuid.UUID
    sect_requirement: str | None = None
    lineage_requirement: str | None = None
    resource_cost: dict[str, Any] = Field(default_factory=dict)
    notes_md: str = ""


class PowerTechniqueUpdateRequest(BaseModel):
    technique_key: str | None = None
    display_name: str | None = None
    min_rank_id: uuid.UUID | None = None
    sect_requirement: str | None = None
    lineage_requirement: str | None = None
    resource_cost: dict[str, Any] | None = None
    notes_md: str | None = None


class PowerSystemSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: uuid.UUID
    enabled: bool
    priority_gap: int
    max_rank_jump_per_chapter: int
    require_breakthrough_event: bool
    updated_at: datetime


class PowerSystemSettingsUpdate(BaseModel):
    enabled: bool | None = None
    priority_gap: int | None = Field(default=None, ge=1, le=10)
    max_rank_jump_per_chapter: int | None = Field(default=None, ge=0, le=5)
    require_breakthrough_event: bool | None = None
