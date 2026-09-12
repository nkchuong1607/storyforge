"""Formalize psyche_card jsonb shape and backfill legacy Phase 3 keys."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "014_psyche_card_schema"
down_revision: Union[str, None] = "013_twist_payoffs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Backfill Phase 3 traits[] -> drive; preserve legacy keys under _legacy for read compat.
    op.execute(
        """
        UPDATE characters
        SET psyche_card = jsonb_set(
            COALESCE(psyche_card, '{}'::jsonb),
            '{drive}',
            to_jsonb(
                COALESCE(
                    NULLIF(psyche_card->>'drive', ''),
                    (psyche_card->'traits'->>0)
                )
            ),
            true
        )
        WHERE psyche_card IS NOT NULL
          AND psyche_card != '{}'::jsonb
          AND (psyche_card ? 'traits')
          AND NOT (psyche_card ? 'drive')
        """
    )
    op.execute(
        """
        UPDATE characters
        SET psyche_card = jsonb_set(
            psyche_card,
            '{_legacy}',
            COALESCE(psyche_card->'_legacy', '{}'::jsonb) || jsonb_build_object(
                'traits', psyche_card->'traits',
                'goals', psyche_card->'goals'
            ),
            true
        )
        WHERE psyche_card IS NOT NULL
          AND psyche_card != '{}'::jsonb
          AND (
            (psyche_card ? 'traits') OR (psyche_card ? 'goals')
          )
        """
    )
    op.execute(
        """
        UPDATE characters
        SET psyche_card = jsonb_set(
            COALESCE(psyche_card, '{}'::jsonb),
            '{need}',
            to_jsonb(
                COALESCE(
                    NULLIF(psyche_card->>'need', ''),
                    (psyche_card->'goals'->>0)
                )
            ),
            true
        )
        WHERE psyche_card IS NOT NULL
          AND psyche_card != '{}'::jsonb
          AND (psyche_card ? 'goals')
          AND NOT (psyche_card ? 'need')
        """
    )


def downgrade() -> None:
    # Legacy backfill is not reversed — data remains compatible.
    pass
