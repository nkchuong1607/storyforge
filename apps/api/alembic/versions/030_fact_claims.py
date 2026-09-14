"""Fact-check claims and author dispositions."""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "030_fact_claims"
down_revision: str | None = "029_fact_check_runs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fact_claims",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=True),
        sa.Column("span_start", sa.Integer(), nullable=True),
        sa.Column("span_end", sa.Integer(), nullable=True),
        sa.Column("span_excerpt", sa.Text(), nullable=True),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("source_research_note_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("severity", sa.Text(), server_default="pass", nullable=False),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("proposed_correction", sa.Text(), nullable=True),
        sa.Column("author_disposition", sa.Text(), server_default="open", nullable=False),
        sa.Column("disposition_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("disposition_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("promoted_research_note_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "provider_results_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["run_id"], ["fact_check_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_research_note_id"], ["research_notes.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["promoted_research_note_id"], ["research_notes.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("fact_claims_run_idx", "fact_claims", ["run_id"])
    op.create_index(
        "fact_claims_project_disposition_idx",
        "fact_claims",
        ["project_id", "author_disposition"],
        postgresql_where=sa.text("author_disposition = 'open'"),
    )


def downgrade() -> None:
    op.drop_index("fact_claims_project_disposition_idx", table_name="fact_claims")
    op.drop_index("fact_claims_run_idx", table_name="fact_claims")
    op.drop_table("fact_claims")
