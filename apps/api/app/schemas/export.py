"""Export job API schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ExportChapterScope, ExportJobStatus, ExportJobType
from app.utils.pagination import PaginatedResponse


class ExportJobOptions(BaseModel):
    chapter_scope: ExportChapterScope = ExportChapterScope.settled_only
    chapter_ids: list[uuid.UUID] | None = None
    include_author_notes: bool = False
    include_bible: bool = True
    bible_version: int | None = None
    strip_secrets: bool = True
    git_md_push_stub: bool = False


class ExportJob(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    job_type: ExportJobType
    status: ExportJobStatus
    options: ExportJobOptions
    artifact_filename: str | None = None
    artifact_size_bytes: int | None = None
    download_url: str | None = None
    error_message: str | None = None
    result_json: dict[str, Any] | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime


class ExportJobCreateRequest(BaseModel):
    job_type: ExportJobType
    options: ExportJobOptions = Field(default_factory=ExportJobOptions)


class ExportJobListResponse(PaginatedResponse[ExportJob]):
    pass
