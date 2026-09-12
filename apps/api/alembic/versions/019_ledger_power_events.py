"""Extend ledger_event_type enum for cultivation events."""

from typing import Sequence, Union

from alembic import op

revision: str = "019_ledger_power_events"
down_revision: Union[str, None] = "018_prompt_edit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE ledger_event_type ADD VALUE IF NOT EXISTS 'cultivation_change'")
    op.execute("ALTER TYPE ledger_event_type ADD VALUE IF NOT EXISTS 'technique_learned'")
    op.execute("ALTER TYPE ledger_event_type ADD VALUE IF NOT EXISTS 'resource_consumed'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values safely.
    pass
