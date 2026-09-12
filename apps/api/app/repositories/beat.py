"""Scene beat data access."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scene_beat import SceneBeat


class BeatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_chapter(self, chapter_id: uuid.UUID) -> list[SceneBeat]:
        rows = await self.session.scalars(
            select(SceneBeat)
            .where(SceneBeat.chapter_id == chapter_id)
            .order_by(SceneBeat.sort_order.asc())
        )
        return list(rows.all())

    async def get(self, chapter_id: uuid.UUID, beat_id: uuid.UUID) -> SceneBeat | None:
        return await self.session.scalar(
            select(SceneBeat).where(
                SceneBeat.id == beat_id,
                SceneBeat.chapter_id == chapter_id,
            )
        )

    async def beat_key_exists(
        self, chapter_id: uuid.UUID, beat_key: str, *, exclude_id: uuid.UUID | None = None
    ) -> bool:
        query = select(SceneBeat.id).where(
            SceneBeat.chapter_id == chapter_id,
            SceneBeat.beat_key == beat_key,
        )
        if exclude_id is not None:
            query = query.where(SceneBeat.id != exclude_id)
        return (await self.session.scalar(query)) is not None

    async def create(self, beat: SceneBeat) -> SceneBeat:
        self.session.add(beat)
        await self.session.flush()
        return beat

    async def update(self, beat: SceneBeat) -> SceneBeat:
        await self.session.flush()
        return beat

    async def delete(self, beat: SceneBeat) -> None:
        await self.session.delete(beat)
        await self.session.flush()
