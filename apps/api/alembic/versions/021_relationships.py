"""Relationships registry and append-only relationship events."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "021_relationships"
down_revision: Union[str, None] = "020_scene_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "relationships",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_a_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_b_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relation_type", sa.Text(), nullable=False),
        sa.Column("custom_label", sa.Text(), nullable=True),
        sa.Column("baseline_intensity", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("notes_md", sa.Text(), server_default="", nullable=False),
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
        sa.CheckConstraint("character_a_id < character_b_id"),
        sa.CheckConstraint("baseline_intensity BETWEEN -5 AND 5"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_a_id"], ["characters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_b_id"], ["characters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "character_a_id",
            "character_b_id",
            name="relationships_project_pair_idx",
        ),
    )
    op.create_index(
        "relationships_project_id_idx",
        "relationships",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "relationships_character_a_idx",
        "relationships",
        ["project_id", "character_a_id"],
        unique=False,
    )
    op.create_index(
        "relationships_character_b_idx",
        "relationships",
        ["project_id", "character_b_id"],
        unique=False,
    )

    op.create_table(
        "relationship_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("intensity_delta", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("intensity_after", sa.SmallInteger(), nullable=False),
        sa.Column("relation_type_after", sa.Text(), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_number", sa.Integer(), nullable=False),
        sa.Column("prose_version", sa.Integer(), nullable=False),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["relationship_id"], ["relationships.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "relationship_events_relationship_idx",
        "relationship_events",
        ["relationship_id", "chapter_number", "settled_at"],
        unique=False,
    )
    op.create_index(
        "relationship_events_project_chapter_idx",
        "relationship_events",
        ["project_id", sa.text("chapter_number DESC")],
        unique=False,
    )
    op.create_index(
        "relationship_events_settled_idx",
        "relationship_events",
        ["relationship_id"],
        unique=False,
        postgresql_where=sa.text("settled_at IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("relationship_events_settled_idx", table_name="relationship_events")
    op.drop_index("relationship_events_project_chapter_idx", table_name="relationship_events")
    op.drop_index("relationship_events_relationship_idx", table_name="relationship_events")
    op.drop_table("relationship_events")
    op.drop_index("relationships_character_b_idx", table_name="relationships")
    op.drop_index("relationships_character_a_idx", table_name="relationships")
    op.drop_index("relationships_project_id_idx", table_name="relationships")
    op.drop_table("relationships")
