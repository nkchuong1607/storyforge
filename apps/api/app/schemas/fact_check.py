"""Fact-check API schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    FactCheckRunStatus,
    FactClaimCategory,
    FactClaimDisposition,
    FactClaimSeverity,
    FactClaimSourceType,
)
from app.utils.pagination import PaginatedResponse, PaginationMeta


class FactClaimSpan(BaseModel):
    start: int
    end: int
    excerpt: str | None = None


class FactCitation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    provider_id: str
    url: str
    title: str
    snippet: str
    retrieved_at: datetime
    research_note_id: uuid.UUID | None = None


class FactClaim(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    project_id: uuid.UUID
    category: FactClaimCategory
    text: str
    normalized_text: str | None = None
    span: FactClaimSpan | None = None
    source_type: FactClaimSourceType
    source_research_note_id: uuid.UUID | None = None
    severity: FactClaimSeverity
    confidence: Decimal | None = None
    summary: str | None = None
    proposed_correction: str | None = None
    author_disposition: FactClaimDisposition
    disposition_at: datetime | None = None
    promoted_research_note_id: uuid.UUID | None = None
    citations: list[FactCitation] = Field(default_factory=list)
    created_at: datetime


class FactCheckRunSummary(BaseModel):
    total_claims: int = 0
    pass_: int = Field(default=0, alias="pass")
    warn: int = 0
    fail: int = 0
    skipped: int = 0

    model_config = ConfigDict(populate_by_name=True)


class FactCheckRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    chapter_id: uuid.UUID
    prose_version_id: uuid.UUID
    requested_by_user_id: uuid.UUID
    status: FactCheckRunStatus
    skipped_reason: str | None = None
    error_message: str | None = None
    summary: FactCheckRunSummary | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime


class FactCheckRunDetail(FactCheckRun):
    claims: list[FactClaim] = Field(default_factory=list)


class FactCheckRunListResponse(PaginatedResponse[FactCheckRun]):
    pagination: PaginationMeta


class FactCheckRunCreateRequest(BaseModel):
    prose_version_id: uuid.UUID | None = None
    force_refresh: bool = False
    categories: list[FactClaimCategory] | None = None


class FactClaimDispositionRequest(BaseModel):
    disposition: FactClaimDisposition
    note: str | None = None


class FactClaimAcceptFixRequest(BaseModel):
    handoff_target: str = "prompt_edit"
    correction_override: str | None = None


class FactClaimAcceptFixResponse(BaseModel):
    claim_id: uuid.UUID
    handoff_target: str
    handoff_payload: dict


class FactClaimPromoteEvidenceRequest(BaseModel):
    citation_id: uuid.UUID | None = None
    note_title: str | None = None
    tags: list[str] = Field(default_factory=list)


class FactClaimPromoteEvidenceResponse(BaseModel):
    claim_id: uuid.UUID
    research_note_id: uuid.UUID
    research_note: dict
