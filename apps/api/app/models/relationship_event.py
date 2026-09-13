"""Relationship event ledger model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, SmallInteger, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class RelationshipEvent(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "relationship_events"
    __table_args__ = (
        Index(
            "relationship_events_relationship_idx",
            "relationship_id",
            "chapter_number",
            "settled_at",
        ),
        Index("relationship_events_project_chapter_idx", "project_id", "chapter_number"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    relationship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("relationships.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    intensity_delta: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    intensity_after: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    relation_type_after: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="RESTRICT"), nullable=False
    )
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    prose_version: Mapped[int] = mapped_column(Integer, nullable=False)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
