"""Scene beat schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SceneBeat(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    chapter_id: uuid.UUID
    beat_key: str
    summary: str
    sort_order: int
    completed: bool
    created_at: datetime
    updated_at: datetime


class SceneBeatCreateRequest(BaseModel):
    beat_key: str
    summary: str
    sort_order: int = Field(ge=0)
    completed: bool = False


class SceneBeatUpdateRequest(BaseModel):
    beat_key: str | None = None
    summary: str | None = None
    sort_order: int | None = None
    completed: bool | None = None


class SceneBeatListResponse(BaseModel):
    items: list[SceneBeat]
