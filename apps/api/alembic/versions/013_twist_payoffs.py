"""Twist payoffs table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "013_twist_payoffs"
down_revision: Union[str, None] = "012_twist_plants"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "twist_payoffs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("twist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "required_plant_ids",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            server_default=sa.text("'{}'::uuid[]"),
            nullable=False,
        ),
        sa.Column("min_plants", sa.Integer(), server_default="1", nullable=False),
        sa.Column("revealed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.CheckConstraint("min_plants >= 0", name="ck_twist_payoffs_min_plants"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["twist_id"], ["twist_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("twist_id", name="uq_twist_payoffs_twist_id"),
    )
    op.create_index(
        "twist_payoffs_target_chapter_idx",
        "twist_payoffs",
        ["target_chapter_id", "twist_id"],
        unique=False,
    )
    op.create_index(
        "twist_payoffs_project_id_idx",
        "twist_payoffs",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("twist_payoffs_project_id_idx", table_name="twist_payoffs")
    op.drop_index("twist_payoffs_target_chapter_idx", table_name="twist_payoffs")
    op.drop_table("twist_payoffs")
