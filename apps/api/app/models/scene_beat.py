"""Scene beat model."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SceneBeat(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "scene_beats"
    __table_args__ = (
        UniqueConstraint("chapter_id", "beat_key", name="uq_scene_beats_chapter_beat_key"),
        UniqueConstraint("chapter_id", "sort_order", name="uq_scene_beats_chapter_sort_order"),
        Index("scene_beats_chapter_id_sort_idx", "chapter_id", "sort_order"),
        Index("scene_beats_project_id_idx", "project_id"),
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
