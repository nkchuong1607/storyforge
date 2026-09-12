"""Twist plants table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "012_twist_plants"
down_revision: Union[str, None] = "011_twist_plans"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE plant_salience AS ENUM ('soft', 'hard')")

    plant_salience = postgresql.ENUM("soft", "hard", name="plant_salience", create_type=False)

    op.create_table(
        "twist_plants",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("twist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("beat_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "salience",
            plant_salience,
            server_default="soft",
            nullable=False,
        ),
        sa.Column("snippet", sa.Text(), server_default="", nullable=False),
        sa.Column("prose_span_start", sa.Integer(), nullable=True),
        sa.Column("prose_span_end", sa.Integer(), nullable=True),
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
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["twist_id"], ["twist_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["beat_id"], ["scene_beats.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "twist_plants_twist_id_idx",
        "twist_plants",
        ["twist_id", sa.text("sort_order ASC")],
        unique=False,
    )
    op.create_index(
        "twist_plants_chapter_id_idx",
        "twist_plants",
        ["chapter_id", "twist_id"],
        unique=False,
    )
    op.create_index(
        "twist_plants_project_id_idx",
        "twist_plants",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("twist_plants_project_id_idx", table_name="twist_plants")
    op.drop_index("twist_plants_chapter_id_idx", table_name="twist_plants")
    op.drop_index("twist_plants_twist_id_idx", table_name="twist_plants")
    op.drop_table("twist_plants")
    op.execute("DROP TYPE IF EXISTS plant_salience")
