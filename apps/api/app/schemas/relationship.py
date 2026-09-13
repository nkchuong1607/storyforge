"""Relationship schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RelationType


class Relationship(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    character_a_id: uuid.UUID
    character_b_id: uuid.UUID
    character_a_name: str | None = None
    character_b_name: str | None = None
    relation_type: RelationType
    custom_label: str | None = None
    baseline_intensity: int = Field(ge=-5, le=5)
    current_intensity: int = Field(ge=-5, le=5)
    notes_md: str = ""
    event_count: int = 0
    created_at: datetime
    updated_at: datetime


class RelationshipCreateRequest(BaseModel):
    character_a_id: uuid.UUID
    character_b_id: uuid.UUID
    relation_type: RelationType
    custom_label: str | None = None
    baseline_intensity: int = Field(default=0, ge=-5, le=5)
    notes_md: str = ""


class RelationshipUpdateRequest(BaseModel):
    relation_type: RelationType | None = None
    custom_label: str | None = None
    baseline_intensity: int | None = Field(default=None, ge=-5, le=5)
    notes_md: str | None = None


class RelationshipListResponse(BaseModel):
    items: list[Relationship]
    page: int
    page_size: int
    total: int


class RelationshipEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    relationship_id: uuid.UUID
    event_type: str
    intensity_delta: int
    intensity_after: int
    relation_type_after: str | None = None
    chapter_id: uuid.UUID | None = None
    chapter_number: int
    prose_version: int | None = None
    settled_at: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class RelationshipEventListResponse(BaseModel):
    items: list[RelationshipEvent]


class RelationshipGraphNode(BaseModel):
    id: uuid.UUID
    display_name: str
    tier: int
    degree: int


class RelationshipGraphEdge(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    target_id: uuid.UUID
    relation_type: RelationType
    intensity: int
    event_count: int
    last_event: dict[str, Any] | None = None


class RelationshipGraphMeta(BaseModel):
    filtered_character_ids: list[uuid.UUID] = Field(default_factory=list)
    act_number: int | None = None
    generated_at: datetime


class RelationshipGraphResponse(BaseModel):
    nodes: list[RelationshipGraphNode]
    edges: list[RelationshipGraphEdge]
    meta: RelationshipGraphMeta


class RelationshipContextPackRequest(BaseModel):
    chapter_id: uuid.UUID
    character_ids: list[uuid.UUID] = Field(default_factory=list)


class RelationshipContextPackEdge(BaseModel):
    relation_type: str
    intensity: int
    recent_events: list[dict[str, Any]] = Field(default_factory=list)


class RelationshipContextPackResponse(BaseModel):
    edges: list[RelationshipContextPackEdge]
