"""Character cast model."""

import uuid

from sqlalchemy import ForeignKey, Index, SmallInteger, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Character(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "characters"
    __table_args__ = (
        UniqueConstraint("project_id", "display_name", name="uq_characters_project_display_name"),
        Index("characters_project_id_tier_idx", "project_id", "tier", "display_name"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    role_one_liner: Mapped[str | None] = mapped_column(Text, nullable=True)
    tier: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    psyche_card: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
