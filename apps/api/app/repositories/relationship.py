"""Relationship data access."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.relationship import Relationship
from app.models.relationship_event import RelationshipEvent


class RelationshipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_project(
        self,
        project_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Relationship], int]:
        total = await self.session.scalar(
            select(func.count())
            .select_from(Relationship)
            .where(Relationship.project_id == project_id)
        )
        rows = await self.session.scalars(
            select(Relationship)
            .where(Relationship.project_id == project_id)
            .order_by(Relationship.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(rows.all()), int(total or 0)

    async def get(self, project_id: uuid.UUID, relationship_id: uuid.UUID) -> Relationship | None:
        return await self.session.scalar(
            select(Relationship).where(
                Relationship.project_id == project_id,
                Relationship.id == relationship_id,
            )
        )

    async def get_by_pair(
        self, project_id: uuid.UUID, character_a_id: uuid.UUID, character_b_id: uuid.UUID
    ) -> Relationship | None:
        a_id, b_id = sorted([character_a_id, character_b_id])
        return await self.session.scalar(
            select(Relationship).where(
                Relationship.project_id == project_id,
                Relationship.character_a_id == a_id,
                Relationship.character_b_id == b_id,
            )
        )

    async def list_all_for_project(self, project_id: uuid.UUID) -> list[Relationship]:
        rows = await self.session.scalars(
            select(Relationship).where(Relationship.project_id == project_id)
        )
        return list(rows.all())

    async def create(self, relationship: Relationship) -> Relationship:
        self.session.add(relationship)
        await self.session.flush()
        return relationship

    async def update(self, relationship: Relationship) -> Relationship:
        await self.session.flush()
        return relationship

    async def delete(self, relationship: Relationship) -> None:
        await self.session.delete(relationship)
        await self.session.flush()

    async def list_events(
        self, project_id: uuid.UUID, relationship_id: uuid.UUID
    ) -> list[RelationshipEvent]:
        rows = await self.session.scalars(
            select(RelationshipEvent)
            .where(
                RelationshipEvent.project_id == project_id,
                RelationshipEvent.relationship_id == relationship_id,
            )
            .order_by(RelationshipEvent.chapter_number.asc(), RelationshipEvent.settled_at.asc())
        )
        return list(rows.all())

    async def list_settled_events_for_project(
        self, project_id: uuid.UUID
    ) -> list[RelationshipEvent]:
        rows = await self.session.scalars(
            select(RelationshipEvent)
            .where(
                RelationshipEvent.project_id == project_id,
                RelationshipEvent.settled_at.is_not(None),
            )
            .order_by(RelationshipEvent.chapter_number.asc(), RelationshipEvent.settled_at.asc())
        )
        return list(rows.all())

    async def create_event(self, event: RelationshipEvent) -> RelationshipEvent:
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_event(
        self, project_id: uuid.UUID, event_id: uuid.UUID
    ) -> RelationshipEvent | None:
        return await self.session.scalar(
            select(RelationshipEvent).where(
                RelationshipEvent.project_id == project_id,
                RelationshipEvent.id == event_id,
            )
        )

    async def count_settled_events(self, relationship_id: uuid.UUID) -> int:
        result = await self.session.scalar(
            select(func.count())
            .select_from(RelationshipEvent)
            .where(
                RelationshipEvent.relationship_id == relationship_id,
                RelationshipEvent.settled_at.is_not(None),
            )
        )
        return int(result or 0)
