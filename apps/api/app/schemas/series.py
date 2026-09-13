"""Series API schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.utils.pagination import PaginatedResponse


class SeriesSummary(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    book_count: int
    hub_project_id: uuid.UUID | None = None
    created_at: datetime


class SeriesProjectLink(BaseModel):
    series_id: uuid.UUID
    project_id: uuid.UUID
    book_order: int
    project_title: str | None = None
    attached_at: datetime


class SeriesDetail(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    hub_project_id: uuid.UUID | None = None
    slice_version_current: int
    projects: list[SeriesProjectLink] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class SeriesListResponse(PaginatedResponse[SeriesSummary]):
    pass


class SeriesCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    create_hub_project: bool = True
    hub_project_title: str | None = None


class SeriesUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    slug: str | None = Field(default=None, min_length=1)


class SeriesAttachProjectRequest(BaseModel):
    project_id: uuid.UUID
    book_order: int = Field(default=1, ge=1)


class SeriesBibleSlice(BaseModel):
    series_id: uuid.UUID
    version: int
    slice_json: dict[str, Any]
    inherited_sections: list[str]
    settled_at: datetime


class ProjectInheritedSliceResponse(BaseModel):
    project_id: uuid.UUID
    series_id: uuid.UUID
    series_title: str | None = None
    slice_version: int
    last_seen_slice_version: int | None = None
    inherited_sections: list[str]
    slice_json: dict[str, Any]
    read_only: bool = True
    drift_warning: bool = False


class SeriesOverrideCreateRequest(BaseModel):
    overrides_series_key: str = Field(min_length=1)
    section: str
    title: str = Field(min_length=1)
    content_md: str
    override_reason: str | None = None


class SeriesOverrideStagingEntry(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    section: str
    title: str
    content_md: str
    metadata: dict[str, Any] = Field(default_factory=dict)
