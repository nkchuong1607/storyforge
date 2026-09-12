"""Continuity reports, overrides, and settle idempotency."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007_continuity_settle"
down_revision: Union[str, None] = "006_ledger_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

continuity_result = postgresql.ENUM("pass", "warn", "fail", name="continuity_result", create_type=False)
continuity_severity = postgresql.ENUM(
    "pass", "warn", "fail", name="continuity_severity", create_type=False
)
continuity_category = postgresql.ENUM(
    "character",
    "timeline",
    "location",
    "world_rule",
    "bible_staging",
    name="continuity_category",
    create_type=False,
)


def upgrade() -> None:
    op.execute("CREATE TYPE continuity_result AS ENUM ('pass', 'warn', 'fail')")
    op.execute("CREATE TYPE continuity_severity AS ENUM ('pass', 'warn', 'fail')")
    op.execute(
        "CREATE TYPE continuity_category AS ENUM ("
        "'character', 'timeline', 'location', 'world_rule', 'bible_staging'"
        ")"
    )

    op.create_table(
        "continuity_reports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prose_version", sa.Integer(), nullable=False),
        sa.Column("result", continuity_result, nullable=False),
        sa.Column(
            "issues_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "state_diff_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "stats_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "rule_pack_version",
            sa.Text(),
            server_default="deterministic-v1",
            nullable=False,
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "continuity_reports_chapter_id_created_desc",
        "continuity_reports",
        ["chapter_id", sa.text("created_at DESC")],
        unique=False,
    )

    op.create_table(
        "continuity_overrides",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_fingerprint", sa.Text(), nullable=False),
        sa.Column("severity_at_override", continuity_severity, nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["report_id"], ["continuity_reports.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "continuity_overrides_chapter_id_idx",
        "continuity_overrides",
        ["chapter_id"],
        unique=False,
    )
    op.create_index(
        "continuity_overrides_active_fingerprint_idx",
        "continuity_overrides",
        ["chapter_id", "issue_fingerprint"],
        unique=True,
        postgresql_where=sa.text("revoked_at IS NULL"),
    )

    op.create_table(
        "settle_idempotency_keys",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "response_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "chapter_id",
            "idempotency_key",
            name="uq_settle_idempotency_chapter_key",
        ),
    )


def downgrade() -> None:
    op.drop_table("settle_idempotency_keys")
    op.drop_index("continuity_overrides_active_fingerprint_idx", table_name="continuity_overrides")
    op.drop_index("continuity_overrides_chapter_id_idx", table_name="continuity_overrides")
    op.drop_table("continuity_overrides")
    op.drop_index("continuity_reports_chapter_id_created_desc", table_name="continuity_reports")
    op.drop_table("continuity_reports")
    op.execute("DROP TYPE IF EXISTS continuity_category")
    op.execute("DROP TYPE IF EXISTS continuity_severity")
    op.execute("DROP TYPE IF EXISTS continuity_result")
