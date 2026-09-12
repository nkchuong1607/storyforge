"""Character provisional inbox model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import ExtractorSource, ProvisionalStatus


class CharacterProvisional(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "character_provisional"
    __table_args__ = (
        Index(
            "character_provisional_project_status_idx",
            "project_id",
            "status",
            "created_at",
        ),
        Index("character_provisional_chapter_idx", "chapter_id", "status"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    mention_text: Mapped[str] = mapped_column(Text, nullable=False)
    mention_fingerprint: Mapped[str] = mapped_column(Text, nullable=False)
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    prose_version: Mapped[int] = mapped_column(Integer, nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    proposed_fields: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    status: Mapped[ProvisionalStatus] = mapped_column(
        Enum(ProvisionalStatus, name="provisional_status", native_enum=True),
        nullable=False,
        server_default=ProvisionalStatus.pending.value,
    )
    extractor_source: Mapped[ExtractorSource] = mapped_column(
        Enum(ExtractorSource, name="extractor_source", native_enum=True),
        nullable=False,
        server_default=ExtractorSource.heuristic.value,
    )
    matched_character_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="SET NULL"), nullable=True
    )
    merged_character_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="SET NULL"), nullable=True
    )
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
