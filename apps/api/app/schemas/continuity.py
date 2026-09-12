"""Continuity report and settle schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ChapterStatus, ContinuityResult, ContinuitySeverity


class ContinuityIssue(BaseModel):
    fingerprint: str
    severity: ContinuitySeverity
    category: str
    code: str
    message: str
    chapter_refs: list[int] = Field(default_factory=list)
    entity_ids: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)


class StateDiff(BaseModel):
    ledger_proposals: list[dict[str, Any]] = Field(default_factory=list)
    bible_patch_candidates: list[dict[str, Any]] = Field(default_factory=list)
    psyche_card_patches: list[dict[str, Any]] = Field(default_factory=list)
    psych_state_proposals: list[dict[str, Any]] = Field(default_factory=list)


class ContinuityReport(BaseModel):
    report_id: uuid.UUID
    chapter_id: uuid.UUID
    prose_version: int
    result: ContinuityResult
    stats: dict[str, int]
    issues: list[ContinuityIssue]
    state_diff: StateDiff
    created_at: datetime | None = None


class ContinuityCheckRequest(BaseModel):
    prose_version: int | None = Field(default=None, ge=1)


class ContinuityOverrideCreateRequest(BaseModel):
    issue_fingerprint: str
    reason: str = Field(min_length=1)


class ContinuityOverride(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    issue_fingerprint: str
    severity_at_override: ContinuitySeverity
    reason: str
    created_at: datetime


class SettleChapterRequest(BaseModel):
    report_id: uuid.UUID | None = None
    approve_state_diff: bool = True


class SettleChapterResponse(BaseModel):
    chapter_id: uuid.UUID
    status: ChapterStatus
    bible_version_before: int
    bible_version_after: int
    ledger_events_appended: int
    psych_states_appended: int = 0
    settled_at: datetime
