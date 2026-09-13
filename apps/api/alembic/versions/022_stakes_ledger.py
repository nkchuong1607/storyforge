"""Act structure settings and stakes ledger entries."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "022_stakes_ledger"
down_revision: Union[str, None] = "021_relationships"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "act_structure_settings",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("act_count", sa.SmallInteger(), server_default="3", nullable=False),
        sa.Column(
            "chapters_per_act",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "flat_middle_window_chapters",
            sa.SmallInteger(),
            server_default="3",
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("act_count BETWEEN 1 AND 7"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id"),
    )

    op.create_table(
        "stakes_ledger_entries",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("act_number", sa.SmallInteger(), nullable=False),
        sa.Column("checkpoint_key", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description_md", sa.Text(), server_default="", nullable=False),
        sa.Column("target_level", sa.SmallInteger(), nullable=False),
        sa.Column("status", sa.Text(), server_default="planned", nullable=False),
        sa.Column("plant_chapter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolve_chapter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("linked_twist_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
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
        sa.CheckConstraint("act_number >= 1"),
        sa.CheckConstraint("target_level BETWEEN 0 AND 5"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plant_chapter_id"], ["chapters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resolve_chapter_id"], ["chapters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["linked_twist_id"], ["twist_plans.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "act_number",
            "checkpoint_key",
            name="stakes_ledger_project_act_key_idx",
        ),
    )
    op.create_index(
        "stakes_ledger_project_act_sort_idx",
        "stakes_ledger_entries",
        ["project_id", "act_number", "sort_order"],
        unique=False,
    )
    op.create_index(
        "stakes_ledger_status_idx",
        "stakes_ledger_entries",
        ["project_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("stakes_ledger_status_idx", table_name="stakes_ledger_entries")
    op.drop_index("stakes_ledger_project_act_sort_idx", table_name="stakes_ledger_entries")
    op.drop_table("stakes_ledger_entries")
    op.drop_table("act_structure_settings")
