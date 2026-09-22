"""CraftPack catalog and project binding models."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CraftPack(Base):
    __tablename__ = "craft_packs"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    pack_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    installed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )


class ProjectCraftPack(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "project_craft_packs"
    __table_args__ = (
        UniqueConstraint("project_id", "craft_pack_id", name="project_craft_packs_project_pack_uq"),
        Index("project_craft_packs_project_active_idx", "project_id", "active"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    craft_pack_id: Mapped[str] = mapped_column(
        Text, ForeignKey("craft_packs.id", ondelete="CASCADE"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    bound_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
