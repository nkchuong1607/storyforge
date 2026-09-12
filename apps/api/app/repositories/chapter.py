"""Chapter data access."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chapter import Chapter
from app.utils.pagination import PageParams


class ChapterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, chapter: Chapter) -> Chapter:
        self.session.add(chapter)
        await self.session.flush()
        return chapter

    async def chapter_number_exists(self, project_id: uuid.UUID, number: int) -> bool:
        result = await self.session.scalar(
            select(Chapter.id).where(
                Chapter.project_id == project_id,
                Chapter.number == number,
            )
        )
        return result is not None

    async def get(self, project_id: uuid.UUID, chapter_id: uuid.UUID) -> Chapter | None:
        return await self.session.scalar(
            select(Chapter).where(
                Chapter.id == chapter_id,
                Chapter.project_id == project_id,
            )
        )

    async def get_by_id(self, chapter_id: uuid.UUID) -> Chapter | None:
        return await self.session.get(Chapter, chapter_id)

    async def update(self, chapter: Chapter) -> Chapter:
        await self.session.flush()
        return chapter

    async def list_for_project(
        self, project_id: uuid.UUID, page: PageParams
    ) -> tuple[list[Chapter], int]:
        filters = [Chapter.project_id == project_id]
        base = select(Chapter).where(*filters).order_by(Chapter.number.asc())
        total = int(
            await self.session.scalar(select(func.count()).select_from(Chapter).where(*filters))
            or 0
        )
        rows = await self.session.scalars(base.offset(page.offset).limit(page.page_size))
        return list(rows.all()), total
