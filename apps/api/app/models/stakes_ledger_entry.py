"""Stakes ledger entry model."""

import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class StakesLedgerEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "stakes_ledger_entries"
    __table_args__ = (
        CheckConstraint("act_number >= 1"),
        CheckConstraint("target_level BETWEEN 0 AND 5"),
        UniqueConstraint(
            "project_id",
            "act_number",
            "checkpoint_key",
            name="stakes_ledger_project_act_key_idx",
        ),
        Index("stakes_ledger_project_act_sort_idx", "project_id", "act_number", "sort_order"),
        Index("stakes_ledger_status_idx", "project_id", "status"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    act_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    checkpoint_key: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description_md: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    target_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="planned")
    plant_chapter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True
    )
    resolve_chapter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True
    )
    linked_twist_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("twist_plans.id", ondelete="SET NULL"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
