"""Append-only PsychState snapshot per character per chapter."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, SmallInteger, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class PsychState(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "psych_states"
    __table_args__ = (
        CheckConstraint(
            "stress_level >= 0 AND stress_level <= 10",
            name="ck_psych_states_stress_level",
        ),
        Index(
            "psych_states_character_chapter_settled_idx",
            "character_id",
            "chapter_id",
            unique=True,
            postgresql_where="settled_at IS NOT NULL",
        ),
        Index(
            "psych_states_project_character_chapter_idx",
            "project_id",
            "character_id",
            "chapter_id",
        ),
        Index("psych_states_character_timeline_idx", "character_id", "settled_at"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    stress_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dominant_emotion: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    active_goal: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    belief_updates: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    relationship_stance: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    value_pressure: Mapped[str | None] = mapped_column(Text, nullable=True)
    arc_beat: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger_event_refs: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    settled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
