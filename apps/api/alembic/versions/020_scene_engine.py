"""Extend scene_beats with structure fields; create scene_engine_settings."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "020_scene_engine"
down_revision: Union[str, None] = "019_ledger_power_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "scene_beats",
        sa.Column("goal", sa.Text(), server_default="", nullable=False),
    )
    op.add_column(
        "scene_beats",
        sa.Column("conflict", sa.Text(), server_default="", nullable=False),
    )
    op.add_column(
        "scene_beats",
        sa.Column("outcome", sa.Text(), server_default="", nullable=False),
    )
    op.add_column(
        "scene_beats",
        sa.Column("stakes_level", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "scene_beats",
        sa.Column(
            "pressure_tags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
    )
    op.add_column(
        "scene_beats",
        sa.Column(
            "pov_character_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("characters.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "scene_beats",
        sa.Column("scene_type", sa.Text(), server_default="scene", nullable=False),
    )
    op.create_check_constraint(
        "scene_beats_stakes_level_check",
        "scene_beats",
        "stakes_level IS NULL OR (stakes_level >= 0 AND stakes_level <= 5)",
    )
    op.create_index(
        "scene_beats_pov_character_idx",
        "scene_beats",
        ["project_id", "pov_character_id"],
        unique=False,
        postgresql_where=sa.text("pov_character_id IS NOT NULL"),
    )

    op.create_table(
        "scene_engine_settings",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("require_conflict", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "require_outcome_on_complete",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
        sa.Column("min_goal_length", sa.SmallInteger(), server_default="8", nullable=False),
        sa.Column(
            "llm_auditor_enabled",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column("strictness", sa.Text(), server_default="standard", nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id"),
    )


def downgrade() -> None:
    op.drop_table("scene_engine_settings")
    op.drop_index("scene_beats_pov_character_idx", table_name="scene_beats")
    op.drop_constraint("scene_beats_stakes_level_check", "scene_beats", type_="check")
    op.drop_column("scene_beats", "scene_type")
    op.drop_column("scene_beats", "pov_character_id")
    op.drop_column("scene_beats", "pressure_tags")
    op.drop_column("scene_beats", "stakes_level")
    op.drop_column("scene_beats", "outcome")
    op.drop_column("scene_beats", "conflict")
    op.drop_column("scene_beats", "goal")
