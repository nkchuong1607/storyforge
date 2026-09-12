"""Continuity report and override models."""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import ContinuityResult, ContinuitySeverity


class ContinuityReport(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "continuity_reports"
    __table_args__ = (
        Index("continuity_reports_chapter_id_created_desc", "chapter_id", "created_at"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    prose_version: Mapped[int] = mapped_column(Integer, nullable=False)
    result: Mapped[ContinuityResult] = mapped_column(
        Enum(
            ContinuityResult,
            name="continuity_result",
            native_enum=True,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )
    issues_json: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    state_diff_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    stats_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    rule_pack_version: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="deterministic-v1"
    )
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ContinuityOverride(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "continuity_overrides"
    __table_args__ = (
        Index("continuity_overrides_chapter_id_idx", "chapter_id"),
        Index(
            "continuity_overrides_active_fingerprint_idx",
            "chapter_id",
            "issue_fingerprint",
            unique=True,
            postgresql_where=text("revoked_at IS NULL"),
        ),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    issue_fingerprint: Mapped[str] = mapped_column(Text, nullable=False)
    severity_at_override: Mapped[ContinuitySeverity] = mapped_column(
        Enum(
            ContinuitySeverity,
            name="continuity_severity",
            native_enum=True,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("continuity_reports.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SettleIdempotencyKey(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "settle_idempotency_keys"
    __table_args__ = (
        UniqueConstraint("chapter_id", "idempotency_key", name="uq_settle_idempotency_chapter_key"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    idempotency_key: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    response_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
