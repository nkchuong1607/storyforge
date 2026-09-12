"""Scene beats and append-only prose versions."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005_scene_beats_prose_versions"
down_revision: Union[str, None] = "004_chapter_status_reviewing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

prose_source = postgresql.ENUM("human", "ai_writer", "ai_editor", name="prose_source", create_type=False)


def upgrade() -> None:
    op.execute("CREATE TYPE prose_source AS ENUM ('human', 'ai_writer', 'ai_editor')")

    op.create_table(
        "scene_beats",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("beat_key", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), server_default="", nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("completed", sa.Boolean(), server_default="false", nullable=False),
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
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chapter_id", "beat_key", name="uq_scene_beats_chapter_beat_key"),
        sa.UniqueConstraint("chapter_id", "sort_order", name="uq_scene_beats_chapter_sort_order"),
    )
    op.create_index(
        "scene_beats_chapter_id_sort_idx",
        "scene_beats",
        ["chapter_id", "sort_order"],
        unique=False,
    )
    op.create_index("scene_beats_project_id_idx", "scene_beats", ["project_id"], unique=False)

    op.create_table(
        "prose_versions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column(
            "source",
            prose_source,
            server_default="human",
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
        sa.UniqueConstraint("chapter_id", "version", name="uq_prose_versions_chapter_version"),
    )
    op.create_index(
        "prose_versions_chapter_id_version_desc_idx",
        "prose_versions",
        ["chapter_id", sa.text("version DESC")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("prose_versions_chapter_id_version_desc_idx", table_name="prose_versions")
    op.drop_table("prose_versions")
    op.drop_index("scene_beats_project_id_idx", table_name="scene_beats")
    op.drop_index("scene_beats_chapter_id_sort_idx", table_name="scene_beats")
    op.drop_table("scene_beats")
    op.execute("DROP TYPE IF EXISTS prose_source")
