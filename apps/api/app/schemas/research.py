"""Research note API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ResearchNoteLinkType, ResearchNoteStatus
from app.utils.pagination import PaginatedResponse


class ResearchNote(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    body_md: str
    source_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    status: ResearchNoteStatus
    promoted_to_staging_id: uuid.UUID | None = None
    promoted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ResearchNoteLink(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    note_id: uuid.UUID
    link_type: ResearchNoteLinkType
    character_id: uuid.UUID | None = None
    bible_key: str | None = None
    chapter_id: uuid.UUID | None = None
    created_at: datetime


class ResearchNoteDetail(ResearchNote):
    links: list[ResearchNoteLink] = Field(default_factory=list)


class ResearchNoteCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    body_md: str = ""
    source_url: str | None = None
    tags: list[str] = Field(default_factory=list)


class ResearchNoteUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    body_md: str | None = None
    source_url: str | None = None
    tags: list[str] | None = None


class ResearchNoteLinkCreateRequest(BaseModel):
    link_type: ResearchNoteLinkType
    character_id: uuid.UUID | None = None
    bible_key: str | None = None
    chapter_id: uuid.UUID | None = None


class ResearchPromoteRequest(BaseModel):
    section: str
    title: str = Field(min_length=1)
    content_md: str | None = None
    staging_entry_id: uuid.UUID | None = None


class ResearchPromoteResponse(BaseModel):
    note_id: uuid.UUID
    staging_entry_id: uuid.UUID
    status: str = "promoted"
    message: str = "Staging entry created — settle separately to commit canon"


class ResearchNoteSearchHit(BaseModel):
    note: ResearchNote
    rank: float
    snippet: str | None = None


class ResearchNoteListResponse(PaginatedResponse[ResearchNote]):
    pass


class ResearchNoteSearchResponse(BaseModel):
    query: str
    items: list[ResearchNoteSearchHit]
    page: int
    page_size: int
    total: int
