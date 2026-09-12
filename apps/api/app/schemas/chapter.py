"""Chapter request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ChapterStatus
from app.utils.pagination import PaginatedResponse, PaginationMeta


class Chapter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    number: int = Field(ge=1)
    title: str
    status: ChapterStatus
    word_count: int
    bible_version_at_draft: int | None = None
    current_prose_version: int | None = None
    settled_at: datetime | None = None
    locked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ChapterCreateRequest(BaseModel):
    number: int = Field(ge=1)
    title: str = Field(min_length=1)
    status: ChapterStatus = ChapterStatus.planned


class ChapterUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    status: ChapterStatus | None = None


class ChapterListResponse(PaginatedResponse[Chapter]):
    pagination: PaginationMeta
