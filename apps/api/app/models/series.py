"""Series and shared bible slice models."""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Series(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "series"
    __table_args__ = (UniqueConstraint("owner_user_id", "slug", name="series_owner_slug_idx"),)

    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False)
    hub_project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )


class SeriesBibleSlice(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "series_bible_slices"
    __table_args__ = (
        UniqueConstraint("series_id", "version", name="series_bible_slices_version_idx"),
        Index("series_bible_slices_series_version_desc", "series_id", "version"),
    )

    series_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("series.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    slice_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    inherited_sections: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default='["world","glossary","style","power_system"]'
    )
    settled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    settled_from_hub_bible_version: Mapped[int | None] = mapped_column(Integer, nullable=True)


class SeriesProject(Base):
    __tablename__ = "series_projects"
    __table_args__ = (
        UniqueConstraint("project_id", name="series_projects_one_series_per_project"),
    )

    series_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("series.id", ondelete="CASCADE"), primary_key=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    book_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="1")
    inheritance_config_json: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    attached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
