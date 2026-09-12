"""Character data access."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import Character
from app.models.enums import CharacterStatus
from app.utils.pagination import PageParams


class CharacterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, project_id: uuid.UUID, character_id: uuid.UUID) -> Character | None:
        return await self.session.scalar(
            select(Character).where(
                Character.project_id == project_id,
                Character.id == character_id,
            )
        )

    async def get_by_display_name(
        self, project_id: uuid.UUID, display_name: str
    ) -> Character | None:
        return await self.session.scalar(
            select(Character).where(
                Character.project_id == project_id,
                func.lower(Character.display_name) == display_name.strip().casefold(),
            )
        )

    async def create(self, character: Character) -> Character:
        self.session.add(character)
        await self.session.flush()
        return character

    async def list_all_for_project(self, project_id: uuid.UUID) -> list[Character]:
        rows = await self.session.scalars(
            select(Character)
            .where(Character.project_id == project_id)
            .order_by(Character.display_name.asc())
        )
        return list(rows.all())

    async def list_for_project(
        self,
        project_id: uuid.UUID,
        page: PageParams,
        *,
        tier: int | None = None,
        status: CharacterStatus | None = None,
        exclude_archived: bool = True,
        q: str | None = None,
    ) -> tuple[list[Character], int]:
        filters: list[Any] = [Character.project_id == project_id]
        if tier is not None:
            filters.append(Character.tier == tier)
        if status is not None:
            filters.append(Character.status == status)
        elif exclude_archived:
            filters.append(Character.status != CharacterStatus.archived)
        if q:
            pattern = f"{q.strip().casefold()}%"
            filters.append(
                or_(
                    func.lower(Character.display_name).like(pattern),
                    Character.aliases.contains([q.strip()]),
                )
            )

        base = (
            select(Character)
            .where(*filters)
            .order_by(Character.tier.desc(), Character.display_name.asc())
        )
        total = int(
            await self.session.scalar(select(func.count()).select_from(Character).where(*filters))
            or 0
        )
        rows = await self.session.scalars(base.offset(page.offset).limit(page.page_size))
        return list(rows.all()), total

    async def search_keyword(
        self,
        project_id: uuid.UUID,
        query: str,
        *,
        limit: int = 20,
    ) -> list[Character]:
        pattern = f"{query.strip().casefold()}%"
        rows = await self.session.scalars(
            select(Character)
            .where(
                Character.project_id == project_id,
                Character.status != CharacterStatus.archived,
                or_(
                    func.lower(Character.display_name).like(pattern),
                    Character.aliases.contains([query.strip()]),
                ),
            )
            .order_by(Character.tier.desc(), Character.appearance_count.desc())
            .limit(limit)
        )
        return list(rows.all())

    async def list_t3_for_project(self, project_id: uuid.UUID) -> list[Character]:
        rows = await self.session.scalars(
            select(Character).where(
                Character.project_id == project_id,
                Character.tier == 3,
                Character.status != CharacterStatus.archived,
            )
        )
        return list(rows.all())

    async def find_by_name_or_alias(self, project_id: uuid.UUID, name: str) -> Character | None:
        normalized = name.strip().casefold()
        rows = await self.session.scalars(
            select(Character).where(
                Character.project_id == project_id,
                Character.status != CharacterStatus.archived,
            )
        )
        for character in rows.all():
            if character.display_name.strip().casefold() == normalized:
                return character
            for alias in character.aliases or []:
                if str(alias).strip().casefold() == normalized:
                    return character
        return None

    async def name_exists_for_project(
        self,
        project_id: uuid.UUID,
        display_name: str,
        *,
        exclude_id: uuid.UUID | None = None,
    ) -> bool:
        filters = [
            Character.project_id == project_id,
            func.lower(Character.display_name) == display_name.strip().casefold(),
        ]
        if exclude_id is not None:
            filters.append(Character.id != exclude_id)
        result = await self.session.scalar(
            select(func.count()).select_from(Character).where(*filters)
        )
        return int(result or 0) > 0
