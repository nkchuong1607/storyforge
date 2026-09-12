"""Prose version schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ProseSource
from app.utils.pagination import PaginatedResponse, PaginationMeta


class ProseVersionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version: int
    word_count: int
    source: ProseSource
    created_by: uuid.UUID
    created_at: datetime


class ProseVersionDetail(ProseVersionSummary):
    content: str


class ProseVersionCreateRequest(BaseModel):
    content: str = Field(min_length=1)


class ProseVersionListResponse(PaginatedResponse[ProseVersionSummary]):
    pagination: PaginationMeta


class ProseVersionCompareResponse(BaseModel):
    from_version: int
    to_version: int
    word_count_delta: int
    created_at_from: datetime
    created_at_to: datetime
