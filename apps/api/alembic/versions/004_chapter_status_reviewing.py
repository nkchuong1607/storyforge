"""Rename continuity_pending to reviewing; add chapter settle columns."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_chapter_status_reviewing"
down_revision: Union[str, None] = "003_chapters_characters"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE chapter_status RENAME VALUE 'continuity_pending' TO 'reviewing'")
    op.add_column("chapters", sa.Column("current_prose_version", sa.Integer(), nullable=True))
    op.add_column(
        "chapters",
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "chapters",
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "chapters_project_status_idx",
        "chapters",
        ["project_id", "status", "number"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("chapters_project_status_idx", table_name="chapters")
    op.drop_column("chapters", "locked_at")
    op.drop_column("chapters", "settled_at")
    op.drop_column("chapters", "current_prose_version")
    op.execute("ALTER TYPE chapter_status RENAME VALUE 'reviewing' TO 'continuity_pending'")
