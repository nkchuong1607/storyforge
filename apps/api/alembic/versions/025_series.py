"""Series, bible slices, and project membership."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "025_series"
down_revision: Union[str, None] = "024_research_notes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "series",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("hub_project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["hub_project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_user_id", "slug", name="series_owner_slug_idx"),
    )

    op.create_table(
        "series_bible_slices",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("series_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("slice_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "inherited_sections",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default='["world","glossary","style","power_system"]',
            nullable=False,
        ),
        sa.Column(
            "settled_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("settled_from_hub_bible_version", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["series_id"], ["series.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("series_id", "version", name="series_bible_slices_version_idx"),
    )
    op.create_index(
        "series_bible_slices_series_version_desc",
        "series_bible_slices",
        ["series_id", sa.text("version DESC")],
    )

    op.create_table(
        "series_projects",
        sa.Column("series_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("book_order", sa.SmallInteger(), server_default="1", nullable=False),
        sa.Column(
            "inheritance_config_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "attached_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["series_id"], ["series.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("series_id", "project_id"),
        sa.UniqueConstraint("project_id", name="series_projects_one_series_per_project"),
    )

    op.add_column(
        "projects",
        sa.Column("series_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("last_seen_series_slice_version", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "projects_series_id_fkey",
        "projects",
        "series",
        ["series_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("projects_series_id_fkey", "projects", type_="foreignkey")
    op.drop_column("projects", "last_seen_series_slice_version")
    op.drop_column("projects", "series_id")
    op.drop_table("series_projects")
    op.drop_index(
        "series_bible_slices_series_version_desc", table_name="series_bible_slices"
    )
    op.drop_table("series_bible_slices")
    op.drop_table("series")
