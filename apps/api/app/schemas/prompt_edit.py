"""Prompt edit API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PromptEditTurn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    turn_index: int
    instruction: str
    proposed_content: str | None = None
    model: str
    provider: str
    latency_ms: int | None = None
    token_usage: dict = Field(default_factory=dict)
    error_code: str | None = None
    created_at: datetime


class PromptEditInstructRequest(BaseModel):
    instruction: str = Field(min_length=1, max_length=4000)
    base_prose_version: int | None = Field(default=None, ge=1)
    beat_key: str | None = None


class PromptEditInstructResponse(BaseModel):
    session_id: uuid.UUID
    turn: PromptEditTurn
    base_prose_version: int


class PromptEditRegenerateRequest(BaseModel):
    session_id: uuid.UUID
    turn_id: uuid.UUID


class PromptEditApplyRequest(BaseModel):
    session_id: uuid.UUID
    turn_id: uuid.UUID


class PromptEditApplyChapterSummary(BaseModel):
    current_prose_version: int
    word_count: int


class PromptEditApplyResponse(BaseModel):
    prose_version: "ProseVersionApplySummary"
    chapter: PromptEditApplyChapterSummary


class ProseVersionApplySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version: int
    source: str
    word_count: int
    created_at: datetime
    prompt_edit_turn_id: uuid.UUID | None = None


class PromptEditSessionSummary(BaseModel):
    id: uuid.UUID
    status: str
    base_prose_version: int
    turns: list[PromptEditTurn]
    created_at: datetime


class PromptEditSessionListResponse(BaseModel):
    items: list[PromptEditSessionSummary]
