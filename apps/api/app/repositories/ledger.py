"""Ledger event data access."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import LedgerEntityType
from app.models.ledger_event import LedgerEvent


class LedgerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, event: LedgerEvent) -> LedgerEvent:
        self.session.add(event)
        await self.session.flush()
        return event

    async def count_for_chapter(self, chapter_id: uuid.UUID) -> int:
        from sqlalchemy import func

        result = await self.session.scalar(
            select(func.count())
            .select_from(LedgerEvent)
            .where(LedgerEvent.chapter_id == chapter_id)
        )
        return int(result or 0)

    async def list_settled_for_project(self, project_id: uuid.UUID) -> list[LedgerEvent]:
        rows = await self.session.scalars(
            select(LedgerEvent)
            .where(
                LedgerEvent.project_id == project_id,
                LedgerEvent.settled_at.is_not(None),
            )
            .order_by(LedgerEvent.settled_at.asc())
        )
        return list(rows.all())

    async def list_tail_for_entity(
        self,
        project_id: uuid.UUID,
        entity_type: LedgerEntityType,
        entity_id: uuid.UUID,
        *,
        limit: int = 5,
    ) -> list[LedgerEvent]:
        rows = await self.session.scalars(
            select(LedgerEvent)
            .where(
                LedgerEvent.project_id == project_id,
                LedgerEvent.entity_type == entity_type,
                LedgerEvent.entity_id == entity_id,
                LedgerEvent.settled_at.is_not(None),
            )
            .order_by(LedgerEvent.settled_at.desc())
            .limit(limit)
        )
        return list(rows.all())
