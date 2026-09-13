"""Scene engine settings model."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, SmallInteger, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SceneEngineSettings(Base):
    __tablename__ = "scene_engine_settings"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    require_conflict: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    require_outcome_on_complete: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    min_goal_length: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="8")
    llm_auditor_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    strictness: Mapped[str] = mapped_column(Text, nullable=False, server_default="standard")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
