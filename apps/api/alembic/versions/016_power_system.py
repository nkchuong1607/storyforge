"""Power system staging tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "016_power_system"
down_revision: Union[str, None] = "015_psych_states"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "power_system_settings",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("priority_gap", sa.SmallInteger(), server_default="2", nullable=False),
        sa.Column(
            "max_rank_jump_per_chapter", sa.SmallInteger(), server_default="1", nullable=False
        ),
        sa.Column(
            "require_breakthrough_event", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id"),
    )

    op.create_table(
        "power_ranks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rank_key", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "sub_stages",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("constraints_md", sa.Text(), server_default="", nullable=False),
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
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "power_ranks_project_key_idx", "power_ranks", ["project_id", "rank_key"], unique=True
    )
    op.create_index(
        "power_ranks_project_sort_idx", "power_ranks", ["project_id", "sort_order"], unique=True
    )
    op.create_index("power_ranks_project_id_idx", "power_ranks", ["project_id"], unique=False)

    op.create_table(
        "power_techniques",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("technique_key", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("min_rank_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sect_requirement", sa.Text(), nullable=True),
        sa.Column("lineage_requirement", sa.Text(), nullable=True),
        sa.Column(
            "resource_cost",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("notes_md", sa.Text(), server_default="", nullable=False),
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
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["min_rank_id"], ["power_ranks.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "power_techniques_project_key_idx",
        "power_techniques",
        ["project_id", "technique_key"],
        unique=True,
    )
    op.create_index(
        "power_techniques_project_min_rank_idx",
        "power_techniques",
        ["project_id", "min_rank_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("power_techniques_project_min_rank_idx", table_name="power_techniques")
    op.drop_index("power_techniques_project_key_idx", table_name="power_techniques")
    op.drop_table("power_techniques")
    op.drop_index("power_ranks_project_id_idx", table_name="power_ranks")
    op.drop_index("power_ranks_project_sort_idx", table_name="power_ranks")
    op.drop_index("power_ranks_project_key_idx", table_name="power_ranks")
    op.drop_table("power_ranks")
    op.drop_table("power_system_settings")
