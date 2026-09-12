"""Chapter metadata model."""

import uuid

from sqlalchemy import Enum, ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ChapterStatus


class Chapter(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chapters"
    __table_args__ = (
        UniqueConstraint("project_id", "number", name="uq_chapters_project_number"),
        Index("chapters_project_id_number_idx", "project_id", "number"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ChapterStatus] = mapped_column(
        Enum(ChapterStatus, name="chapter_status", native_enum=True),
        nullable=False,
        server_default=ChapterStatus.planned.value,
    )
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    bible_version_at_draft: Mapped[int | None] = mapped_column(Integer, nullable=True)
