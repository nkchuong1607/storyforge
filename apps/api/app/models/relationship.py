"""Relationship registry model."""

import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Relationship(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "relationships"
    __table_args__ = (
        CheckConstraint("character_a_id < character_b_id"),
        CheckConstraint("baseline_intensity BETWEEN -5 AND 5"),
        UniqueConstraint(
            "project_id", "character_a_id", "character_b_id", name="relationships_project_pair_idx"
        ),
        Index("relationships_project_id_idx", "project_id"),
        Index("relationships_character_a_idx", "project_id", "character_a_id"),
        Index("relationships_character_b_idx", "project_id", "character_b_id"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    character_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    character_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(Text, nullable=False)
    custom_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    baseline_intensity: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="0"
    )
    notes_md: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
