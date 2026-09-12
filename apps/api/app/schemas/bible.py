"""Bible request/response schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BibleSection
from app.utils.pagination import PaginatedResponse, PaginationMeta


class BibleEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    entry_key: str
    section: BibleSection
    title: str
    content_md: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    base_bible_version: int
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_entry(cls, entry: object) -> "BibleEntry":
        data = {
            "id": entry.id,  # type: ignore[attr-defined]
            "project_id": entry.project_id,  # type: ignore[attr-defined]
            "entry_key": entry.entry_key,  # type: ignore[attr-defined]
            "section": entry.section,  # type: ignore[attr-defined]
            "title": entry.title,  # type: ignore[attr-defined]
            "content_md": entry.content_md,  # type: ignore[attr-defined]
            "metadata": entry.metadata_,  # type: ignore[attr-defined]
            "base_bible_version": entry.base_bible_version,  # type: ignore[attr-defined]
            "created_by": entry.created_by,  # type: ignore[attr-defined]
            "created_at": entry.created_at,  # type: ignore[attr-defined]
            "updated_at": entry.updated_at,  # type: ignore[attr-defined]
        }
        return cls.model_validate(data)


class BibleEntryCreateRequest(BaseModel):
    entry_key: str = Field(pattern=r"^[a-z0-9_]+(?:\.[a-z0-9_]+)*$")
    section: BibleSection
    title: str = Field(min_length=1)
    content_md: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class BibleEntryUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    content_md: str | None = None
    metadata: dict[str, Any] | None = None
    section: BibleSection | None = None


class BibleEntryListResponse(PaginatedResponse[BibleEntry]):
    pagination: PaginationMeta


class BibleVersionSummary(BaseModel):
    version: int
    settled_from_chapter_id: uuid.UUID | None = None
    created_at: datetime
    entry_count: int


class BibleVersionDetail(BibleVersionSummary):
    project_id: uuid.UUID
    snapshot_json: dict[str, Any]


class BibleVersionListResponse(PaginatedResponse[BibleVersionSummary]):
    pagination: PaginationMeta
