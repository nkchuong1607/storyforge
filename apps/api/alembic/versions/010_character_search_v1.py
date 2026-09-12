"""Character search indexes — ILIKE + GIN aliases."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010_character_search_v1"
down_revision: Union[str, None] = "009_character_provisional"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX characters_aliases_gin ON characters "
        "USING gin (aliases jsonb_path_ops)"
    )
    op.execute(
        "CREATE INDEX characters_display_name_lower_idx "
        "ON characters (project_id, lower(display_name) text_pattern_ops)"
    )


def downgrade() -> None:
    op.drop_index("characters_display_name_lower_idx", table_name="characters")
    op.drop_index("characters_aliases_gin", table_name="characters")
