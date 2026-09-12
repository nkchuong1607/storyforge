"""PsychState append-only ledger table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "015_psych_states"
down_revision: Union[str, None] = "014_psyche_card_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "psych_states",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stress_level", sa.SmallInteger(), nullable=False),
        sa.Column("dominant_emotion", sa.Text(), server_default="", nullable=False),
        sa.Column("active_goal", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "belief_updates",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "relationship_stance",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("value_pressure", sa.Text(), nullable=True),
        sa.Column("arc_beat", sa.Text(), nullable=True),
        sa.Column(
            "trigger_event_refs",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "stress_level >= 0 AND stress_level <= 10",
            name="ck_psych_states_stress_level",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "psych_states_character_chapter_settled_idx",
        "psych_states",
        ["character_id", "chapter_id"],
        unique=True,
        postgresql_where=sa.text("settled_at IS NOT NULL"),
    )
    op.create_index(
        "psych_states_project_character_chapter_idx",
        "psych_states",
        ["project_id", "character_id", sa.text("chapter_id DESC")],
        unique=False,
    )
    op.create_index(
        "psych_states_character_timeline_idx",
        "psych_states",
        ["character_id", sa.text("settled_at DESC")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("psych_states_character_timeline_idx", table_name="psych_states")
    op.drop_index("psych_states_project_character_chapter_idx", table_name="psych_states")
    op.drop_index("psych_states_character_chapter_settled_idx", table_name="psych_states")
    op.drop_table("psych_states")
