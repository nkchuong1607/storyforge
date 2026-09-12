"""Project and membership models."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    GenreProfile,
    ProjectLanguage,
    ProjectMemberRole,
    ProjectStatus,
    ProjectTemplate,
)


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "projects"
    __table_args__ = (
        Index("projects_created_by_status_idx", "created_by", "status", "updated_at"),
    )

    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[ProjectLanguage] = mapped_column(
        Enum(ProjectLanguage, name="project_language", native_enum=True),
        nullable=False,
        server_default=ProjectLanguage.vi.value,
    )
    genre_profile: Mapped[GenreProfile] = mapped_column(
        Enum(GenreProfile, name="genre_profile", native_enum=True),
        nullable=False,
        server_default=GenreProfile.custom.value,
    )
    template: Mapped[ProjectTemplate] = mapped_column(
        Enum(ProjectTemplate, name="project_template", native_enum=True),
        nullable=False,
        server_default=ProjectTemplate.blank.value,
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status", native_enum=True),
        nullable=False,
        server_default=ProjectStatus.active.value,
    )
    bible_version_current: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    genre_rule_pack_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    members: Mapped[list["ProjectMember"]] = relationship(back_populates="project")


class ProjectMember(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_members_project_user"),
        Index("project_members_user_id_idx", "user_id"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    role: Mapped[ProjectMemberRole] = mapped_column(
        Enum(ProjectMemberRole, name="project_member_role", native_enum=True),
        nullable=False,
        server_default=ProjectMemberRole.owner.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    project: Mapped[Project] = relationship(back_populates="members")
