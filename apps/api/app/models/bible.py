"""Bible version and staging models."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import BibleSection


class BibleVersion(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "bible_versions"
    __table_args__ = (
        UniqueConstraint("project_id", "version", name="uq_bible_versions_project_version"),
        Index("bible_versions_project_id_version_desc_idx", "project_id", "version"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    settled_from_chapter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chapters.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class BibleEntryStaging(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "bible_entry_staging"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "entry_key", name="uq_bible_entry_staging_project_entry_key"
        ),
        Index("bible_entry_staging_project_section_idx", "project_id", "section", "title"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    entry_key: Mapped[str] = mapped_column(Text, nullable=False)
    section: Mapped[BibleSection] = mapped_column(
        Enum(BibleSection, name="bible_section", native_enum=True), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content_md: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, server_default="{}")
    base_bible_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
