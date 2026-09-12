"""Phase 5 psychology schemas — psyche card and psych state."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.character import Character
from app.models.psych_state import PsychState
from app.utils.pagination import PaginationMeta


class PsycheArcFlags(BaseModel):
    allow_moral_break: bool = False
    expected_arc_beats: list[str] = Field(default_factory=list)
    current_arc_beat: str | None = None


class RelationshipLensEntry(BaseModel):
    target_character_id: uuid.UUID
    role_label: str | None = None
    trust_level: int | None = Field(default=None, ge=0, le=5)
    notes: str | None = None


class PsycheCard(BaseModel):
    model_config = ConfigDict(extra="allow")

    drive: str | None = None
    need: str | None = None
    wound: str | None = None
    fear: str | None = None
    value_hierarchy: list[str] = Field(default_factory=list)
    defense: str | None = None
    voice_taboo: list[str] = Field(default_factory=list)
    stress_behavior: str | None = None
    moral_boundaries: list[str] = Field(default_factory=list)
    relationship_lens: list[RelationshipLensEntry] = Field(default_factory=list)
    arc_flags: PsycheArcFlags | None = None


class PsycheCardResponse(BaseModel):
    character_id: uuid.UUID
    project_id: uuid.UUID
    tier: int
    psyche_card: PsycheCard
    updated_at: datetime


class PsycheCardUpdateRequest(BaseModel):
    psyche_card: dict[str, Any]


class BeliefUpdate(BaseModel):
    from_belief: str | None = None
    to_belief: str | None = None
    confidence: str | None = None
    trigger_ref: str | None = None


class RelationshipStance(BaseModel):
    target_character_id: uuid.UUID | None = None
    stance: str | None = None
    trust_delta: int | None = None
    notes: str | None = None


class PsychStateSchema(BaseModel):
    id: uuid.UUID
    character_id: uuid.UUID
    chapter_id: uuid.UUID
    chapter_number: int | None = None
    stress_level: int = Field(ge=0, le=10)
    dominant_emotion: str
    active_goal: str
    belief_updates: list[dict[str, Any]] = Field(default_factory=list)
    relationship_stance: list[dict[str, Any]] = Field(default_factory=list)
    value_pressure: str | None = None
    arc_beat: str | None = None
    trigger_event_refs: list[str] = Field(default_factory=list)
    settled_at: datetime

    @classmethod
    def from_model(cls, row: PsychState, *, chapter_number: int | None = None) -> PsychStateSchema:
        return cls(
            id=row.id,
            character_id=row.character_id,
            chapter_id=row.chapter_id,
            chapter_number=chapter_number,
            stress_level=row.stress_level,
            dominant_emotion=row.dominant_emotion,
            active_goal=row.active_goal,
            belief_updates=list(row.belief_updates or []),
            relationship_stance=list(row.relationship_stance or []),
            value_pressure=row.value_pressure,
            arc_beat=row.arc_beat,
            trigger_event_refs=list(row.trigger_event_refs or []),
            settled_at=row.settled_at,
        )


class PsychStateListResponse(BaseModel):
    items: list[PsychStateSchema]
    pagination: PaginationMeta


class PsychStateProposal(BaseModel):
    character_id: uuid.UUID
    chapter_id: uuid.UUID
    stress_level: int = Field(ge=0, le=10)
    dominant_emotion: str = ""
    active_goal: str = ""
    belief_updates: list[dict[str, Any]] = Field(default_factory=list)
    relationship_stance: list[dict[str, Any]] = Field(default_factory=list)
    value_pressure: str | None = None
    arc_beat: str | None = None
    trigger_event_refs: list[str] = Field(default_factory=list)
    confidence: str | None = None


class PsycheCardPatchProposal(BaseModel):
    character_id: uuid.UUID
    patch: dict[str, Any]
    confidence: str | None = None


class PsychContextPackRequest(BaseModel):
    chapter_id: uuid.UUID
    beat_ids: list[uuid.UUID] = Field(default_factory=list)
    character_ids: list[uuid.UUID] = Field(default_factory=list)
    include_psyche_card: bool = True
    psych_history_limit: int = Field(default=1, ge=0, le=5)


class PsychContextPackEntry(BaseModel):
    character_id: uuid.UUID
    display_name: str
    tier: int
    psyche_summary: dict[str, Any] | None = None
    latest_psych_state: dict[str, Any] | None = None
    included_reason: str


class PsychContextPackResponse(BaseModel):
    entries: list[PsychContextPackEntry]
    truncated: bool = False


def psyche_card_from_character(character: Character) -> PsycheCard:
    raw = character.psyche_card
    if raw is None or raw == {}:
        return PsycheCard()
    return PsycheCard.model_validate(raw)


def psyche_summary_from_card(card: PsycheCard) -> dict[str, Any]:
    return {
        "drive": card.drive,
        "need": card.need,
        "moral_boundaries": list(card.moral_boundaries),
        "value_hierarchy": list(card.value_hierarchy),
    }
