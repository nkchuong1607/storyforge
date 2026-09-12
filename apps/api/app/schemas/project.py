"""Project request/response schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import GenreProfile, ProjectLanguage, ProjectStatus, ProjectTemplate
from app.utils.pagination import PaginatedResponse, PaginationMeta


class ProjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    description: str | None = None
    language: ProjectLanguage = ProjectLanguage.vi
    genre_profile: GenreProfile
    template: ProjectTemplate = ProjectTemplate.blank
    status: ProjectStatus
    bible_version_current: int
    progress_percent: int = 0
    updated_at: datetime


class ProjectDetail(ProjectSummary):
    created_by: uuid.UUID
    created_at: datetime
    settings: dict[str, Any] = Field(default_factory=dict)
    chapter_count: int
    bible_entry_count: int


class ProjectCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    language: ProjectLanguage
    genre_profile: GenreProfile
    template: ProjectTemplate
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ProjectUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: ProjectStatus | None = None
    settings: dict[str, Any] | None = None


class ProjectListResponse(PaginatedResponse[ProjectSummary]):
    pagination: PaginationMeta
