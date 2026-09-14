"""Project reality / fact-check settings."""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "028_project_reality_settings"
down_revision: str | None = "027_bible_staging_series_meta"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "project_reality_settings",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reality_anchors", sa.Text(), server_default="soft", nullable=False),
        sa.Column(
            "enabled_categories",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("fact_check_blocks_settle", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("auto_run_on_save", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("include_research_notes", sa.Boolean(), server_default="true", nullable=False),
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
    op.drop_table("project_reality_settings")
