"""CraftPack API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ContextAudience


class CraftPackSummary(BaseModel):
    id: str
    display_name: str
    genre_tags: list[str]
    schema_version: int


class CraftPackListResponse(BaseModel):
    items: list[CraftPackSummary]


class CraftPackDetail(BaseModel):
    id: str
    pack: dict[str, Any]


class ProjectCraftPackBinding(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    craft_pack_id: str
    active: bool
    bound_at: datetime
    display_name: str


class ProjectCraftPackResponse(BaseModel):
    project_id: uuid.UUID
    active_pack_id: str | None = None
    bindings: list[ProjectCraftPackBinding]


class CraftContextPackRequest(BaseModel):
    chapter_id: uuid.UUID
    chapter_number: int = Field(ge=1)
    audience: ContextAudience = ContextAudience.writer


class CraftBeatEntry(BaseModel):
    key: str
    act: int
    required: bool


class CraftChecklistOpenItem(BaseModel):
    id: str
    code: str
    description: str | None = None


class CraftClueEntry(BaseModel):
    twist_id: uuid.UUID
    twist_title: str
    chapter_number: int
    snippet: str
    plant_id: uuid.UUID


class CraftMisdirectionEntry(BaseModel):
    twist_id: uuid.UUID
    twist_title: str
    misdirection: str


class CraftContextPackResponse(BaseModel):
    craft_pack_id: str
    craft_beats: list[CraftBeatEntry]
    craft_checklist_open: list[CraftChecklistOpenItem]
    active_clues: list[CraftClueEntry]
    active_misdirections: list[CraftMisdirectionEntry]
    meta: dict[str, Any]
