"""Extend ledger enums for relationship and stakes events."""

from typing import Sequence, Union

from alembic import op

revision: str = "023_ledger_phase8_events"
down_revision: Union[str, None] = "022_stakes_ledger"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE ledger_entity_type ADD VALUE IF NOT EXISTS 'relationship'")
    op.execute("ALTER TYPE ledger_entity_type ADD VALUE IF NOT EXISTS 'stakes'")
    op.execute("ALTER TYPE ledger_event_type ADD VALUE IF NOT EXISTS 'relationship_change'")
    op.execute("ALTER TYPE ledger_event_type ADD VALUE IF NOT EXISTS 'stakes_escalation'")


def downgrade() -> None:
    pass
