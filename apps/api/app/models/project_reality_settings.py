"""Project reality / fact-check settings model."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProjectRealitySettings(Base):
    __tablename__ = "project_reality_settings"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    reality_anchors: Mapped[str] = mapped_column(Text, nullable=False, server_default="soft")
    enabled_categories: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    fact_check_blocks_settle: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    auto_run_on_save: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    include_research_notes: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
