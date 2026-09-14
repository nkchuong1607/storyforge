"""Fact-check provider types."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class ResearchNoteSnapshot:
    id: uuid.UUID
    title: str
    body_md: str
    source_url: str | None
    tags: list[str]
    updated_at: datetime


@dataclass
class ClaimDraft:
    category: str
    text: str
    normalized_text: str | None
    span_start: int | None
    span_end: int | None
    span_excerpt: str | None
    source_type: str
    source_research_note_id: uuid.UUID | None = None


@dataclass
class CitationDraft:
    provider_id: str
    url: str
    title: str
    snippet: str
    retrieved_at: datetime
    snapshot_json: dict = field(default_factory=dict)
    research_note_id: uuid.UUID | None = None


@dataclass
class ProviderResult:
    status: Literal["verified", "contradiction", "inconclusive", "skipped"]
    severity: Literal["pass", "warn", "fail"]
    confidence: float
    summary: str
    proposed_correction: str | None
    citations: list[CitationDraft]
    provider_id: str


@dataclass
class ProviderContext:
    project_id: uuid.UUID
    research_notes: list[ResearchNoteSnapshot]
    http_enabled: bool
    force_refresh: bool
    cache_enabled: bool
