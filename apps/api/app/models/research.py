"""Research notes and entity links."""

import uuid
from datetime import datetime

from sqlalchemy import Computed, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ResearchNote(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "research_notes"
    __table_args__ = (
        Index("research_notes_project_status_idx", "project_id", "status", "updated_at"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body_md: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="active")
    promoted_to_staging_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bible_entry_staging.id", ondelete="SET NULL"),
        nullable=True,
    )
    promoted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(body_md, ''))",
            persisted=True,
        ),
        nullable=True,
    )


class ResearchNoteLink(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "research_note_links"
    __table_args__ = (Index("research_note_links_note_idx", "note_id"),)

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_notes.id", ondelete="CASCADE"), nullable=False
    )
    link_type: Mapped[str] = mapped_column(Text, nullable=False)
    character_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=True
    )
    bible_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
