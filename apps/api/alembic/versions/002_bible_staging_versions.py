"""Bible versions and staging tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_bible_staging_versions"
down_revision: Union[str, None] = "001_core_enums_and_projects"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

bible_section = postgresql.ENUM(
    "world_rules",
    "locations",
    "factions",
    "glossary",
    "timeline",
    "characters",
    "objects",
    name="bible_section",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        "CREATE TYPE bible_section AS ENUM ("
        "'world_rules', 'locations', 'factions', 'glossary', "
        "'timeline', 'characters', 'objects'"
        ")"
    )

    op.create_table(
        "bible_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("settled_from_chapter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "version", name="uq_bible_versions_project_version"),
    )
    op.create_index(
        "bible_versions_project_id_version_desc_idx",
        "bible_versions",
        ["project_id", "version"],
        unique=False,
    )

    op.create_table(
        "bible_entry_staging",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entry_key", sa.Text(), nullable=False),
        sa.Column("section", bible_section, nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("content_md", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("base_bible_version", sa.Integer(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "entry_key", name="uq_bible_entry_staging_project_entry_key"),
    )
    op.create_index(
        "bible_entry_staging_project_section_idx",
        "bible_entry_staging",
        ["project_id", "section", "title"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("bible_entry_staging_project_section_idx", table_name="bible_entry_staging")
    op.drop_table("bible_entry_staging")
    op.drop_index("bible_versions_project_id_version_desc_idx", table_name="bible_versions")
    op.drop_table("bible_versions")
    op.execute("DROP TYPE IF EXISTS bible_section")
