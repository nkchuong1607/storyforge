"""Append-only ledger event model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import LedgerEntityType, LedgerEventType


class LedgerEvent(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "ledger_events"
    __table_args__ = (
        Index(
            "ledger_events_project_entity_idx",
            "project_id",
            "entity_type",
            "entity_id",
            "settled_at",
        ),
        Index("ledger_events_chapter_id_idx", "chapter_id", "created_at"),
        Index(
            "ledger_events_unsettled_idx",
            "project_id",
            "chapter_id",
            postgresql_where=text("settled_at IS NULL"),
        ),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    entity_type: Mapped[LedgerEntityType] = mapped_column(
        Enum(LedgerEntityType, name="ledger_entity_type", native_enum=True), nullable=False
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    event_type: Mapped[LedgerEventType] = mapped_column(
        Enum(LedgerEventType, name="ledger_event_type", native_enum=True), nullable=False
    )
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="RESTRICT"), nullable=False
    )
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    prose_version: Mapped[int] = mapped_column(Integer, nullable=False)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supersedes_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ledger_events.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
