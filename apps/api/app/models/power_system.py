"""Power system staging models."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, SmallInteger, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class PowerSystemSettings(Base):
    __tablename__ = "power_system_settings"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    priority_gap: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="2")
    max_rank_jump_per_chapter: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="1"
    )
    require_breakthrough_event: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PowerRank(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "power_ranks"
    __table_args__ = (
        Index("power_ranks_project_key_idx", "project_id", "rank_key", unique=True),
        Index("power_ranks_project_sort_idx", "project_id", "sort_order", unique=True),
        Index("power_ranks_project_id_idx", "project_id"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    rank_key: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    sub_stages: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    constraints_md: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PowerTechnique(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "power_techniques"
    __table_args__ = (
        Index("power_techniques_project_key_idx", "project_id", "technique_key", unique=True),
        Index("power_techniques_project_min_rank_idx", "project_id", "min_rank_id"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    technique_key: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    min_rank_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("power_ranks.id", ondelete="RESTRICT"), nullable=False
    )
    sect_requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    lineage_requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource_cost: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    notes_md: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
