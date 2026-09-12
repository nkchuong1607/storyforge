"""Append-only ledger events for character/world state."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006_ledger_events"
down_revision: Union[str, None] = "005_scene_beats_prose_versions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ledger_entity_type = postgresql.ENUM(
    "character", "object", "knowledge", "promise", name="ledger_entity_type", create_type=False
)
ledger_event_type = postgresql.ENUM(
    "status_change",
    "location_change",
    "timeline_anchor",
    "bible_promote",
    name="ledger_event_type",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        "CREATE TYPE ledger_entity_type AS ENUM ('character', 'object', 'knowledge', 'promise')"
    )
    op.execute(
        "CREATE TYPE ledger_event_type AS ENUM ("
        "'status_change', 'location_change', 'timeline_anchor', 'bible_promote'"
        ")"
    )

    op.create_table(
        "ledger_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", ledger_entity_type, nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", ledger_event_type, nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_number", sa.Integer(), nullable=False),
        sa.Column("prose_version", sa.Integer(), nullable=False),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("supersedes_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["supersedes_event_id"], ["ledger_events.id"], name="fk_ledger_events_supersedes"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ledger_events_project_entity_idx",
        "ledger_events",
        ["project_id", "entity_type", "entity_id", sa.text("settled_at DESC NULLS LAST")],
        unique=False,
    )
    op.create_index(
        "ledger_events_chapter_id_idx",
        "ledger_events",
        ["chapter_id", sa.text("created_at DESC")],
        unique=False,
    )
    op.create_index(
        "ledger_events_unsettled_idx",
        "ledger_events",
        ["project_id", "chapter_id"],
        unique=False,
        postgresql_where=sa.text("settled_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ledger_events_unsettled_idx", table_name="ledger_events")
    op.drop_index("ledger_events_chapter_id_idx", table_name="ledger_events")
    op.drop_index("ledger_events_project_entity_idx", table_name="ledger_events")
    op.drop_table("ledger_events")
    op.execute("DROP TYPE IF EXISTS ledger_event_type")
    op.execute("DROP TYPE IF EXISTS ledger_entity_type")
