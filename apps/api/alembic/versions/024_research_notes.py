"""Research notes and entity links with FTS."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "024_research_notes"
down_revision: Union[str, None] = "023_ledger_phase8_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "research_notes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body_md", sa.Text(), server_default="", nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("status", sa.Text(), server_default="active", nullable=False),
        sa.Column("promoted_to_staging_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("promoted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "search_vector",
            postgresql.TSVECTOR(),
            sa.Computed(
                "to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(body_md, ''))",
                persisted=True,
            ),
            nullable=True,
        ),
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
        sa.ForeignKeyConstraint(
            ["promoted_to_staging_id"], ["bible_entry_staging.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "research_notes_project_status_idx",
        "research_notes",
        ["project_id", "status", sa.text("updated_at DESC")],
    )
    op.create_index(
        "research_notes_search_idx",
        "research_notes",
        ["search_vector"],
        postgresql_using="gin",
    )
    op.create_index(
        "research_notes_tags_idx",
        "research_notes",
        ["tags"],
        postgresql_using="gin",
        postgresql_ops={"tags": "jsonb_path_ops"},
    )

    op.create_table(
        "research_note_links",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("note_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("link_type", sa.Text(), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("bible_key", sa.Text(), nullable=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["note_id"], ["research_notes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "(link_type = 'character' AND character_id IS NOT NULL "
            "AND bible_key IS NULL AND chapter_id IS NULL) OR "
            "(link_type IN ('place', 'fact') AND bible_key IS NOT NULL "
            "AND character_id IS NULL AND chapter_id IS NULL) OR "
            "(link_type = 'chapter' AND chapter_id IS NOT NULL "
            "AND character_id IS NULL AND bible_key IS NULL)",
            name="research_note_links_target_check",
        ),
    )
    op.create_index("research_note_links_note_idx", "research_note_links", ["note_id"])
    op.create_index(
        "research_note_links_character_idx",
        "research_note_links",
        ["project_id", "character_id"],
        postgresql_where=sa.text("character_id IS NOT NULL"),
    )
    op.execute(
        "CREATE UNIQUE INDEX research_note_links_dedupe_idx ON research_note_links "
        "(note_id, link_type, coalesce(character_id::text, bible_key, chapter_id::text))"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS research_note_links_dedupe_idx")
    op.drop_index("research_note_links_character_idx", table_name="research_note_links")
    op.drop_index("research_note_links_note_idx", table_name="research_note_links")
    op.drop_table("research_note_links")
    op.drop_index("research_notes_tags_idx", table_name="research_notes")
    op.drop_index("research_notes_search_idx", table_name="research_notes")
    op.drop_index("research_notes_project_status_idx", table_name="research_notes")
    op.drop_table("research_notes")
