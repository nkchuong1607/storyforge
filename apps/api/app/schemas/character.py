"""Character request/response schemas."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import CharacterStatus, ExtractorSource, ProvisionalStatus
from app.utils.pagination import PaginatedResponse, PaginationMeta
from app.utils.tier_validation import compute_tier_suggest


class Character(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    display_name: str
    role_one_liner: str | None = None
    tier: int = Field(default=0, ge=0, le=3)
    status: CharacterStatus = CharacterStatus.established
    aliases: list[str] = Field(default_factory=list)
    psyche_card: dict[str, Any] | None = None
    first_seen_chapter_id: uuid.UUID | None = None
    last_seen_chapter_id: uuid.UUID | None = None
    appearance_count: int = Field(default=0, ge=0)
    merged_from_provisional_id: uuid.UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    tier_suggest: bool = False
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, character: Any) -> "Character":
        metadata = dict(getattr(character, "metadata_", {}) or {})
        psyche = character.psyche_card
        if psyche is None:
            psyche = {}
        tier_suggest = compute_tier_suggest(character.appearance_count, metadata)
        return cls(
            id=character.id,
            project_id=character.project_id,
            display_name=character.display_name,
            role_one_liner=character.role_one_liner,
            tier=character.tier,
            status=character.status,
            aliases=list(character.aliases or []),
            psyche_card=psyche,
            first_seen_chapter_id=character.first_seen_chapter_id,
            last_seen_chapter_id=character.last_seen_chapter_id,
            appearance_count=character.appearance_count,
            merged_from_provisional_id=character.merged_from_provisional_id,
            metadata=metadata,
            tier_suggest=tier_suggest,
            created_at=character.created_at,
            updated_at=character.updated_at,
        )


class CharacterCreateRequest(BaseModel):
    display_name: str = Field(min_length=1)
    role_one_liner: str | None = None
    tier: int = Field(default=0, ge=0, le=2)
    aliases: list[str] = Field(default_factory=list)
    status: CharacterStatus = CharacterStatus.established

    @field_validator("tier")
    @classmethod
    def reject_t3_create(cls, value: int) -> int:
        if value > 2:
            raise ValueError("Cannot create character at tier 3")
        return value


class CharacterUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=1)
    role_one_liner: str | None = None
    aliases: list[str] | None = None
    psyche_card: dict[str, Any] | None = None
    status: CharacterStatus | None = None
    metadata: dict[str, Any] | None = None


class CharacterPromoteTierRequest(BaseModel):
    confirm_t3: bool = False


class CharacterListResponse(PaginatedResponse[Character]):
    pagination: PaginationMeta


class CharacterSearchResult(BaseModel):
    character: Character
    match_type: Literal["display_name", "alias", "vector"]
    matched_alias: str | None = None
    score: float = 1.0


class CharacterSearchResponse(BaseModel):
    items: list[CharacterSearchResult]
    search_mode: Literal["keyword", "vector"] = "keyword"


class CharacterProvisional(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    mention_text: str
    mention_fingerprint: str
    chapter_id: uuid.UUID
    chapter_number: int | None = None
    prose_version: int
    snippet: str = ""
    proposed_fields: dict[str, Any] = Field(default_factory=dict)
    status: ProvisionalStatus
    extractor_source: ExtractorSource
    matched_character_id: uuid.UUID | None = None
    merged_character_id: uuid.UUID | None = None
    resolved_at: datetime | None = None
    created_at: datetime


class CharacterProvisionalListResponse(PaginatedResponse[CharacterProvisional]):
    pagination: PaginationMeta
    pending_count: int


class CharacterProvisionalMergeRequest(BaseModel):
    target_character_id: uuid.UUID | None = None
    create_new: bool = False
    display_name: str | None = None
    initial_tier: int = Field(default=0, ge=0, le=2)
    mark_established: bool = True


class CharacterProvisionalMergeResponse(BaseModel):
    provisional: CharacterProvisional
    character: Character
    idempotent: bool


class CharacterProvisionalRejectRequest(BaseModel):
    reason: str | None = None


class ExtractCharactersRequest(BaseModel):
    prose_version: int | None = None
    extractor_mode: Literal["heuristic", "llm"] = "heuristic"
    include_beats: bool = True


class ExtractCharactersResponse(BaseModel):
    created_count: int
    skipped_count: int
    skipped_reasons: dict[str, int] = Field(default_factory=dict)
    provisionals: list[CharacterProvisional]


class CharacterContextPackRequest(BaseModel):
    chapter_id: uuid.UUID
    beat_ids: list[uuid.UUID] | None = None
    name_hints: list[str] = Field(default_factory=list)
    max_stubs: int = Field(default=12, ge=1, le=20)
    include_ledger_tail: bool = True
    ledger_tail_limit: int = Field(default=5, ge=0, le=10)


class CharacterContextPackEntry(BaseModel):
    character: Character
    included_reason: Literal["scene_beat", "pov", "t3_principal", "name_hint", "search_match"]
    ledger_tail: list[dict[str, Any]] = Field(default_factory=list)


class CharacterContextPackResponse(BaseModel):
    entries: list[CharacterContextPackEntry]
    truncated: bool
    search_mode: Literal["keyword", "vector"] = "keyword"
