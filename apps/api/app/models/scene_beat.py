"""Scene beat model."""

import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SceneBeat(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "scene_beats"
    __table_args__ = (
        UniqueConstraint("chapter_id", "beat_key", name="uq_scene_beats_chapter_beat_key"),
        UniqueConstraint("chapter_id", "sort_order", name="uq_scene_beats_chapter_sort_order"),
        CheckConstraint(
            "stakes_level IS NULL OR (stakes_level >= 0 AND stakes_level <= 5)",
            name="scene_beats_stakes_level_check",
        ),
        Index("scene_beats_chapter_id_sort_idx", "chapter_id", "sort_order"),
        Index("scene_beats_project_id_idx", "project_id"),
        Index(
            "scene_beats_pov_character_idx",
            "project_id",
            "pov_character_id",
            postgresql_where="pov_character_id IS NOT NULL",
        ),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    beat_key: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    goal: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    conflict: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    outcome: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    stakes_level: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    pressure_tags: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    pov_character_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="SET NULL"), nullable=True
    )
    scene_type: Mapped[str] = mapped_column(Text, nullable=False, server_default="scene")
