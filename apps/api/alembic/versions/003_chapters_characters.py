"""Chapters, characters, and bible_versions chapter FK."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_chapters_characters"
down_revision: Union[str, None] = "002_bible_staging_versions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

chapter_status = postgresql.ENUM(
    "planned",
    "drafting",
    "continuity_pending",
    "settled",
    "locked",
    name="chapter_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        "CREATE TYPE chapter_status AS ENUM ("
        "'planned', 'drafting', 'continuity_pending', 'settled', 'locked'"
        ")"
    )

    op.create_table(
        "chapters",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column(
            "status",
            chapter_status,
            server_default="planned",
            nullable=False,
        ),
        sa.Column("word_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("bible_version_at_draft", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "number", name="uq_chapters_project_number"),
    )
    op.create_index("chapters_project_id_number_idx", "chapters", ["project_id", "number"], unique=False)

    op.create_foreign_key(
        "fk_bible_versions_settled_from_chapter_id",
        "bible_versions",
        "chapters",
        ["settled_from_chapter_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "characters",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("role_one_liner", sa.Text(), nullable=True),
        sa.Column("tier", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column(
            "psyche_card",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "display_name", name="uq_characters_project_display_name"),
    )
    op.create_index(
        "characters_project_id_tier_idx",
        "characters",
        ["project_id", "tier", "display_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("characters_project_id_tier_idx", table_name="characters")
    op.drop_table("characters")
    op.drop_constraint("fk_bible_versions_settled_from_chapter_id", "bible_versions", type_="foreignkey")
    op.drop_index("chapters_project_id_number_idx", table_name="chapters")
    op.drop_table("chapters")
    op.execute("DROP TYPE IF EXISTS chapter_status")
