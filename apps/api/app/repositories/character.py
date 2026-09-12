"""Character data access."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import Character
from app.utils.pagination import PageParams


class CharacterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, character: Character) -> Character:
        self.session.add(character)
        await self.session.flush()
        return character

    async def list_for_project(
        self, project_id: uuid.UUID, page: PageParams
    ) -> tuple[list[Character], int]:
        filters = [Character.project_id == project_id]
        base = select(Character).where(*filters).order_by(Character.display_name.asc())
        total = int(
            await self.session.scalar(select(func.count()).select_from(Character).where(*filters))
            or 0
        )
        rows = await self.session.scalars(base.offset(page.offset).limit(page.page_size))
        return list(rows.all()), total
