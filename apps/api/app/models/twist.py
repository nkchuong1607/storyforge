"""TwistPlan ledger models — plans, plants, payoffs."""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import PlantSalience, TwistPlanKind, TwistPlanStatus


class TwistPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "twist_plans"
    __table_args__ = (
        Index("twist_plans_project_status_idx", "project_id", "status", "updated_at"),
        Index("twist_plans_project_kind_idx", "project_id", "kind", "status"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    secret_truth: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TwistPlanStatus] = mapped_column(
        Enum(TwistPlanStatus, name="twist_plan_status", native_enum=True),
        nullable=False,
        server_default=TwistPlanStatus.seeded.value,
    )
    kind: Mapped[TwistPlanKind] = mapped_column(
        Enum(TwistPlanKind, name="twist_plan_kind", native_enum=True),
        nullable=False,
        server_default=TwistPlanKind.twist.value,
    )
    misdirection: Mapped[str | None] = mapped_column(Text, nullable=True)
    constraints_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    genre_strictness: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)


class TwistPlant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "twist_plants"
    __table_args__ = (
        Index("twist_plants_twist_id_idx", "twist_id", "sort_order"),
        Index("twist_plants_chapter_id_idx", "chapter_id", "twist_id"),
        Index("twist_plants_project_id_idx", "project_id"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    twist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("twist_plans.id", ondelete="CASCADE"), nullable=False
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    beat_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scene_beats.id", ondelete="SET NULL"), nullable=True
    )
    salience: Mapped[PlantSalience] = mapped_column(
        Enum(PlantSalience, name="plant_salience", native_enum=True),
        nullable=False,
        server_default=PlantSalience.soft.value,
    )
    snippet: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    prose_span_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prose_span_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")


class TwistPayoff(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "twist_payoffs"
    __table_args__ = (
        UniqueConstraint("twist_id", name="uq_twist_payoffs_twist_id"),
        CheckConstraint("min_plants >= 0", name="ck_twist_payoffs_min_plants"),
        Index("twist_payoffs_target_chapter_idx", "target_chapter_id", "twist_id"),
        Index("twist_payoffs_project_id_idx", "project_id"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    twist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("twist_plans.id", ondelete="CASCADE"), nullable=False
    )
    target_chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    required_plant_ids: Mapped[list] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=False, server_default="{}"
    )
    min_plants: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    revealed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
