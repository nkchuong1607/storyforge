"""TwistPlan API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.enums import (
    ContextAudience,
    GenreStrictness,
    PlantSalience,
    TwistPlanKind,
    TwistPlanStatus,
)
from app.models.twist import TwistPayoff as TwistPayoffModel
from app.models.twist import TwistPlan as TwistPlanModel
from app.models.twist import TwistPlant as TwistPlantModel
from app.utils.pagination import PaginatedResponse


class TwistPayoffSummary(BaseModel):
    id: uuid.UUID
    target_chapter_id: uuid.UUID
    target_chapter_number: int
    min_plants: int = Field(ge=0)
    required_plant_ids: list[uuid.UUID] = Field(default_factory=list)


class TwistPlan(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    secret_truth: str | None = None
    status: TwistPlanStatus
    kind: TwistPlanKind
    misdirection: str | None = None
    constraints_json: dict[str, Any] = Field(default_factory=dict)
    genre_strictness: GenreStrictness | None = None
    plant_count: int = Field(ge=0, default=0)
    payoff: TwistPayoffSummary | None = None
    created_at: datetime
    updated_at: datetime


class TwistPlanCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    secret_truth: str = Field(min_length=1)
    kind: TwistPlanKind = TwistPlanKind.twist
    misdirection: str | None = None
    constraints_json: dict[str, Any] = Field(default_factory=dict)
    genre_strictness: GenreStrictness | None = None


class TwistPlanUpdateRequest(BaseModel):
    title: str | None = None
    secret_truth: str | None = None
    misdirection: str | None = None
    constraints_json: dict[str, Any] | None = None
    genre_strictness: GenreStrictness | None = None
    status: TwistPlanStatus | None = None


class TwistPlanListResponse(PaginatedResponse[TwistPlan]):
    pass


class TwistTransitionRequest(BaseModel):
    status: TwistPlanStatus


class TwistPlant(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    twist_id: uuid.UUID
    chapter_id: uuid.UUID
    chapter_number: int
    beat_id: uuid.UUID | None = None
    salience: PlantSalience
    snippet: str
    prose_span_start: int | None = None
    prose_span_end: int | None = None
    sort_order: int
    created_at: datetime
    updated_at: datetime


class TwistPlantCreateRequest(BaseModel):
    chapter_id: uuid.UUID
    beat_id: uuid.UUID | None = None
    salience: PlantSalience = PlantSalience.soft
    snippet: str = ""
    prose_span_start: int | None = None
    prose_span_end: int | None = None
    sort_order: int = 0


class TwistPlantUpdateRequest(BaseModel):
    chapter_id: uuid.UUID | None = None
    beat_id: uuid.UUID | None = None
    salience: PlantSalience | None = None
    snippet: str | None = None
    prose_span_start: int | None = None
    prose_span_end: int | None = None
    sort_order: int | None = None
    twist_id: uuid.UUID | None = None


class TwistPlantListResponse(BaseModel):
    items: list[TwistPlant]


class TwistPayoff(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    twist_id: uuid.UUID
    target_chapter_id: uuid.UUID
    target_chapter_number: int
    required_plant_ids: list[uuid.UUID] = Field(default_factory=list)
    min_plants: int = Field(ge=0)
    revealed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TwistPayoffCreateRequest(BaseModel):
    target_chapter_id: uuid.UUID
    required_plant_ids: list[uuid.UUID] = Field(default_factory=list)
    min_plants: int = Field(default=1, ge=0)


class TwistPayoffUpdateRequest(BaseModel):
    target_chapter_id: uuid.UUID | None = None
    required_plant_ids: list[uuid.UUID] | None = None
    min_plants: int | None = Field(default=None, ge=0)


class TwistFairnessState(BaseModel):
    state: Literal["ok", "warn", "fail"]
    issue_codes: list[str] = Field(default_factory=list)


class TwistBoardCard(BaseModel):
    card_type: Literal["twist", "plant", "payoff"]
    twist_id: uuid.UUID | None = None
    plant_id: uuid.UUID | None = None
    payoff_id: uuid.UUID | None = None
    title: str | None = None
    twist_title: str | None = None
    status: TwistPlanStatus | None = None
    kind: TwistPlanKind | None = None
    secret_truth_preview: str | None = None
    chapter_number: int | None = None
    target_chapter_number: int | None = None
    salience: PlantSalience | None = None
    snippet: str | None = None
    min_plants: int | None = None
    plant_count: int | None = None
    required_plant_ids: list[uuid.UUID] | None = None
    fairness: TwistFairnessState | None = None


class TwistBoardColumn(BaseModel):
    id: Literal["secrets", "plants", "payoffs", "revealed"]
    label: str
    cards: list[TwistBoardCard]


class TwistBoardResponse(BaseModel):
    columns: list[TwistBoardColumn]


class TwistContextPackRequest(BaseModel):
    chapter_id: uuid.UUID
    chapter_number: int = Field(ge=1)
    max_plants: int = Field(default=20, ge=1, le=50)
    audience: ContextAudience = ContextAudience.writer


class TwistContextPlantEntry(BaseModel):
    plant_id: uuid.UUID
    twist_id: uuid.UUID
    twist_title: str
    chapter_number: int
    salience: PlantSalience
    snippet: str


class TwistContextPackResponse(BaseModel):
    twist_relevant: list[TwistContextPlantEntry]
    meta: dict[str, Any]


def strip_writer_secrets(constraints_json: dict[str, Any]) -> dict[str, Any]:
    """Remove author-only fields from constraints for writer audience."""
    stripped = dict(constraints_json)
    stripped.pop("constrained_facts", None)
    return stripped


def twist_plan_from_model(
    twist: TwistPlanModel,
    *,
    plant_count: int,
    payoff: TwistPayoffModel | None = None,
    target_chapter_number: int | None = None,
    audience: ContextAudience = ContextAudience.author,
) -> TwistPlan:
    payoff_summary = None
    if payoff is not None and target_chapter_number is not None:
        payoff_summary = TwistPayoffSummary(
            id=payoff.id,
            target_chapter_id=payoff.target_chapter_id,
            target_chapter_number=target_chapter_number,
            min_plants=payoff.min_plants,
            required_plant_ids=list(payoff.required_plant_ids or []),
        )
    constraints = dict(twist.constraints_json or {})
    secret_truth = twist.secret_truth
    misdirection = twist.misdirection
    if audience == ContextAudience.writer:
        secret_truth = None
        misdirection = None
        constraints = strip_writer_secrets(constraints)
    genre = twist.genre_strictness
    genre_enum = GenreStrictness(genre) if genre in ("strict", "relaxed") else None
    return TwistPlan(
        id=twist.id,
        project_id=twist.project_id,
        title=twist.title,
        secret_truth=secret_truth,
        status=twist.status,
        kind=twist.kind,
        misdirection=misdirection,
        constraints_json=constraints,
        genre_strictness=genre_enum,
        plant_count=plant_count,
        payoff=payoff_summary,
        created_at=twist.created_at,
        updated_at=twist.updated_at,
    )


def twist_plant_from_model(plant: TwistPlantModel, chapter_number: int) -> TwistPlant:
    return TwistPlant(
        id=plant.id,
        project_id=plant.project_id,
        twist_id=plant.twist_id,
        chapter_id=plant.chapter_id,
        chapter_number=chapter_number,
        beat_id=plant.beat_id,
        salience=plant.salience,
        snippet=plant.snippet,
        prose_span_start=plant.prose_span_start,
        prose_span_end=plant.prose_span_end,
        sort_order=plant.sort_order,
        created_at=plant.created_at,
        updated_at=plant.updated_at,
    )


def twist_payoff_from_model(payoff: TwistPayoffModel, target_chapter_number: int) -> TwistPayoff:
    return TwistPayoff(
        id=payoff.id,
        project_id=payoff.project_id,
        twist_id=payoff.twist_id,
        target_chapter_id=payoff.target_chapter_id,
        target_chapter_number=target_chapter_number,
        required_plant_ids=list(payoff.required_plant_ids or []),
        min_plants=payoff.min_plants,
        revealed_at=payoff.revealed_at,
        created_at=payoff.created_at,
        updated_at=payoff.updated_at,
    )
