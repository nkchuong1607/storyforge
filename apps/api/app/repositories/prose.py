"""Prose version data access."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prose_version import ProseVersion
from app.utils.pagination import PageParams


class ProseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_max_version(self, chapter_id: uuid.UUID) -> int:
        result = await self.session.scalar(
            select(func.max(ProseVersion.version)).where(ProseVersion.chapter_id == chapter_id)
        )
        return int(result or 0)

    async def get_version(self, chapter_id: uuid.UUID, version: int) -> ProseVersion | None:
        return await self.session.scalar(
            select(ProseVersion).where(
                ProseVersion.chapter_id == chapter_id,
                ProseVersion.version == version,
            )
        )

    async def get_latest(self, chapter_id: uuid.UUID) -> ProseVersion | None:
        return await self.session.scalar(
            select(ProseVersion)
            .where(ProseVersion.chapter_id == chapter_id)
            .order_by(ProseVersion.version.desc())
            .limit(1)
        )

    async def create(self, prose: ProseVersion) -> ProseVersion:
        self.session.add(prose)
        await self.session.flush()
        return prose

    async def list_for_chapter(
        self, chapter_id: uuid.UUID, page: PageParams
    ) -> tuple[list[ProseVersion], int]:
        filters = [ProseVersion.chapter_id == chapter_id]
        base = select(ProseVersion).where(*filters).order_by(ProseVersion.version.desc())
        total = int(
            await self.session.scalar(
                select(func.count()).select_from(ProseVersion).where(*filters)
            )
            or 0
        )
        rows = await self.session.scalars(base.offset(page.offset).limit(page.page_size))
        return list(rows.all()), total
