"""Act structure settings model."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, SmallInteger, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ActStructureSettings(Base):
    __tablename__ = "act_structure_settings"
    __table_args__ = (CheckConstraint("act_count BETWEEN 1 AND 7"),)

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    act_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="3")
    chapters_per_act: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    flat_middle_window_chapters: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="3"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
