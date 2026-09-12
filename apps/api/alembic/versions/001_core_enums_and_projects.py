"""Core enums, projects, and project_members."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_core_enums_and_projects"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

project_status = postgresql.ENUM("active", "archived", name="project_status", create_type=False)
project_member_role = postgresql.ENUM(
    "owner", "editor", "viewer", name="project_member_role", create_type=False
)
project_language = postgresql.ENUM("vi", "en", "mixed", name="project_language", create_type=False)
genre_profile = postgresql.ENUM(
    "xianxia", "mystery", "literary", "romance", "custom", name="genre_profile", create_type=False
)
project_template = postgresql.ENUM(
    "blank", "xianxia_starter", "mystery_starter", name="project_template", create_type=False
)


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.execute("CREATE TYPE project_status AS ENUM ('active', 'archived')")
    op.execute("CREATE TYPE project_member_role AS ENUM ('owner', 'editor', 'viewer')")
    op.execute("CREATE TYPE project_language AS ENUM ('vi', 'en', 'mixed')")
    op.execute(
        "CREATE TYPE genre_profile AS ENUM ('xianxia', 'mystery', 'literary', 'romance', 'custom')"
    )
    op.execute(
        "CREATE TYPE project_template AS ENUM ('blank', 'xianxia_starter', 'mystery_starter')"
    )

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "language",
            project_language,
            server_default="vi",
            nullable=False,
        ),
        sa.Column(
            "genre_profile",
            genre_profile,
            server_default="custom",
            nullable=False,
        ),
        sa.Column(
            "template",
            project_template,
            server_default="blank",
            nullable=False,
        ),
        sa.Column(
            "status",
            project_status,
            server_default="active",
            nullable=False,
        ),
        sa.Column("bible_version_current", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "projects_created_by_status_idx",
        "projects",
        ["created_by", "status", "updated_at"],
        unique=False,
    )

    op.create_table(
        "project_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role",
            project_member_role,
            server_default="owner",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_members_project_user"),
    )
    op.create_index("project_members_user_id_idx", "project_members", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("project_members_user_id_idx", table_name="project_members")
    op.drop_table("project_members")
    op.drop_index("projects_created_by_status_idx", table_name="projects")
    op.drop_table("projects")

    op.execute("DROP TYPE IF EXISTS project_template")
    op.execute("DROP TYPE IF EXISTS genre_profile")
    op.execute("DROP TYPE IF EXISTS project_language")
    op.execute("DROP TYPE IF EXISTS project_member_role")
    op.execute("DROP TYPE IF EXISTS project_status")
