"""Extend characters for Phase 3 progressive cast."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "008_characters_progressive"
down_revision: Union[str, None] = "007_continuity_settle"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

character_status = postgresql.ENUM(
    "established",
    "provisional",
    "archived",
    name="character_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        "CREATE TYPE character_status AS ENUM ('established', 'provisional', 'archived')"
    )

    op.add_column(
        "characters",
        sa.Column(
            "aliases",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "characters",
        sa.Column(
            "status",
            character_status,
            server_default="established",
            nullable=False,
        ),
    )
    op.add_column(
        "characters",
        sa.Column(
            "first_seen_chapter_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "characters",
        sa.Column(
            "last_seen_chapter_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "characters",
        sa.Column(
            "appearance_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "characters",
        sa.Column(
            "merged_from_provisional_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "characters",
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )

    op.create_foreign_key(
        "fk_characters_first_seen_chapter_id",
        "characters",
        "chapters",
        ["first_seen_chapter_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_characters_last_seen_chapter_id",
        "characters",
        "chapters",
        ["last_seen_chapter_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.execute(
        "UPDATE characters SET psyche_card = NULL "
        "WHERE psyche_card = '{}'::jsonb OR psyche_card IS NULL"
    )
    op.alter_column("characters", "psyche_card", nullable=True)

    op.create_check_constraint(
        "ck_characters_tier_range",
        "characters",
        "tier >= 0 AND tier <= 3",
    )

    op.drop_index("characters_project_id_tier_idx", table_name="characters")
    op.create_index(
        "characters_project_tier_name_idx",
        "characters",
        ["project_id", sa.text("tier DESC"), "display_name"],
        unique=False,
    )
    op.create_index(
        "characters_project_status_idx",
        "characters",
        ["project_id", "status", sa.text("updated_at DESC")],
        unique=False,
    )
    op.create_index(
        "characters_last_seen_idx",
        "characters",
        ["project_id", "last_seen_chapter_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("characters_last_seen_idx", table_name="characters")
    op.drop_index("characters_project_status_idx", table_name="characters")
    op.drop_index("characters_project_tier_name_idx", table_name="characters")
    op.drop_constraint("ck_characters_tier_range", "characters", type_="check")
    op.drop_constraint("fk_characters_last_seen_chapter_id", "characters", type_="foreignkey")
    op.drop_constraint("fk_characters_first_seen_chapter_id", "characters", type_="foreignkey")

    op.alter_column(
        "characters",
        "psyche_card",
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )
    op.execute("UPDATE characters SET psyche_card = '{}'::jsonb WHERE psyche_card IS NULL")

    op.drop_column("characters", "metadata")
    op.drop_column("characters", "merged_from_provisional_id")
    op.drop_column("characters", "appearance_count")
    op.drop_column("characters", "last_seen_chapter_id")
    op.drop_column("characters", "first_seen_chapter_id")
    op.drop_column("characters", "status")
    op.drop_column("characters", "aliases")

    op.create_index(
        "characters_project_id_tier_idx",
        "characters",
        ["project_id", "tier", "display_name"],
        unique=False,
    )

    op.execute("DROP TYPE IF EXISTS character_status")
