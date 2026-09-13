"""Document bible_entry_staging metadata keys for Phase 9 promote/series."""

from typing import Sequence, Union

from alembic import op

revision: str = "027_bible_staging_series_meta"
down_revision: Union[str, None] = "026_export_jobs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # metadata_json already exists from Phase 1; document Phase 9 keys:
    # source_research_note_id, series_override, overrides_series_key, override_reason
    op.execute(
        "COMMENT ON COLUMN bible_entry_staging.metadata IS "
        "'JSON metadata; Phase 9 keys: source_research_note_id, series_override, "
        "overrides_series_key, override_reason'"
    )


def downgrade() -> None:
    op.execute("COMMENT ON COLUMN bible_entry_staging.metadata IS NULL")
