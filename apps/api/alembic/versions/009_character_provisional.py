"""Character provisional inbox table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "009_character_provisional"
down_revision: Union[str, None] = "008_characters_progressive"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

provisional_status = postgresql.ENUM(
    "pending",
    "merged",
    "rejected",
    name="provisional_status",
    create_type=False,
)
extractor_source = postgresql.ENUM(
    "heuristic",
    "manual",
    "llm",
    name="extractor_source",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        "CREATE TYPE provisional_status AS ENUM ('pending', 'merged', 'rejected')"
    )
    op.execute(
        "CREATE TYPE extractor_source AS ENUM ('heuristic', 'manual', 'llm')"
    )

    op.create_table(
        "character_provisional",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mention_text", sa.Text(), nullable=False),
        sa.Column("mention_fingerprint", sa.Text(), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prose_version", sa.Integer(), nullable=False),
        sa.Column("snippet", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "proposed_fields",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "status",
            provisional_status,
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "extractor_source",
            extractor_source,
            server_default="heuristic",
            nullable=False,
        ),
        sa.Column("matched_character_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merged_character_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["matched_character_id"], ["characters.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["merged_character_id"], ["characters.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "character_provisional_project_status_idx",
        "character_provisional",
        ["project_id", "status", sa.text("created_at DESC")],
        unique=False,
    )
    op.create_index(
        "character_provisional_chapter_idx",
        "character_provisional",
        ["chapter_id", "status"],
        unique=False,
    )
    op.execute(
        "CREATE UNIQUE INDEX character_provisional_pending_fingerprint_idx "
        "ON character_provisional (project_id, mention_fingerprint) "
        "WHERE status = 'pending'"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS character_provisional_pending_fingerprint_idx")
    op.drop_index("character_provisional_chapter_idx", table_name="character_provisional")
    op.drop_index(
        "character_provisional_project_status_idx", table_name="character_provisional"
    )
    op.drop_table("character_provisional")
    op.execute("DROP TYPE IF EXISTS extractor_source")
    op.execute("DROP TYPE IF EXISTS provisional_status")
