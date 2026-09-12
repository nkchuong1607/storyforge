"""Character cast model."""

import uuid

from sqlalchemy import (
    CheckConstraint,
    Enum,
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
from app.models.enums import CharacterStatus


class Character(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "characters"
    __table_args__ = (
        UniqueConstraint("project_id", "display_name", name="uq_characters_project_display_name"),
        CheckConstraint("tier >= 0 AND tier <= 3", name="ck_characters_tier_range"),
        Index("characters_project_tier_name_idx", "project_id", "tier", "display_name"),
        Index("characters_project_status_idx", "project_id", "status", "updated_at"),
        Index("characters_last_seen_idx", "project_id", "last_seen_chapter_id"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    role_one_liner: Mapped[str | None] = mapped_column(Text, nullable=True)
    tier: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    aliases: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    psyche_card: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[CharacterStatus] = mapped_column(
        Enum(CharacterStatus, name="character_status", native_enum=True),
        nullable=False,
        server_default=CharacterStatus.established.value,
    )
    first_seen_chapter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True
    )
    last_seen_chapter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True
    )
    appearance_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    merged_from_provisional_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, server_default="{}")
