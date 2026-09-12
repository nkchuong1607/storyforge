"""Twist plans table and Phase 4 enums."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "011_twist_plans"
down_revision: Union[str, None] = "010_character_search_v1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE twist_plan_status AS ENUM ("
        "'seeded', 'planted', 'armed', 'paid_off', 'abandoned'"
        ")"
    )
    op.execute("CREATE TYPE twist_plan_kind AS ENUM ('twist', 'promise')")

    op.execute("ALTER TYPE continuity_category ADD VALUE IF NOT EXISTS 'foreshadow'")

    twist_plan_status = postgresql.ENUM(
        "seeded",
        "planted",
        "armed",
        "paid_off",
        "abandoned",
        name="twist_plan_status",
        create_type=False,
    )
    twist_plan_kind = postgresql.ENUM(
        "twist", "promise", name="twist_plan_kind", create_type=False
    )

    op.create_table(
        "twist_plans",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("secret_truth", sa.Text(), nullable=False),
        sa.Column(
            "status",
            twist_plan_status,
            server_default="seeded",
            nullable=False,
        ),
        sa.Column(
            "kind",
            twist_plan_kind,
            server_default="twist",
            nullable=False,
        ),
        sa.Column("misdirection", sa.Text(), nullable=True),
        sa.Column(
            "constraints_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("genre_strictness", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
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
        "twist_plans_project_status_idx",
        "twist_plans",
        ["project_id", "status", sa.text("updated_at DESC")],
        unique=False,
    )
    op.create_index(
        "twist_plans_project_kind_idx",
        "twist_plans",
        ["project_id", "kind", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("twist_plans_project_kind_idx", table_name="twist_plans")
    op.drop_index("twist_plans_project_status_idx", table_name="twist_plans")
    op.drop_table("twist_plans")
    op.execute("DROP TYPE IF EXISTS twist_plan_kind")
    op.execute("DROP TYPE IF EXISTS twist_plan_status")
