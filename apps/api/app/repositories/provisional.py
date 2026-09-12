"""Character provisional inbox data access."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character_provisional import CharacterProvisional
from app.models.enums import ProvisionalStatus
from app.utils.pagination import PageParams


class ProvisionalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, project_id: uuid.UUID, provisional_id: uuid.UUID
    ) -> CharacterProvisional | None:
        return await self.session.scalar(
            select(CharacterProvisional).where(
                CharacterProvisional.project_id == project_id,
                CharacterProvisional.id == provisional_id,
            )
        )

    async def create(self, provisional: CharacterProvisional) -> CharacterProvisional:
        self.session.add(provisional)
        await self.session.flush()
        return provisional

    async def list_for_project(
        self,
        project_id: uuid.UUID,
        page: PageParams,
        *,
        status: ProvisionalStatus | None = ProvisionalStatus.pending,
        chapter_id: uuid.UUID | None = None,
    ) -> tuple[list[CharacterProvisional], int]:
        filters: list[Any] = [CharacterProvisional.project_id == project_id]
        if status is not None:
            filters.append(CharacterProvisional.status == status)
        if chapter_id is not None:
            filters.append(CharacterProvisional.chapter_id == chapter_id)

        base = (
            select(CharacterProvisional)
            .where(*filters)
            .order_by(CharacterProvisional.created_at.desc())
        )
        total = int(
            await self.session.scalar(
                select(func.count()).select_from(CharacterProvisional).where(*filters)
            )
            or 0
        )
        rows = await self.session.scalars(base.offset(page.offset).limit(page.page_size))
        return list(rows.all()), total

    async def count_pending(self, project_id: uuid.UUID) -> int:
        result = await self.session.scalar(
            select(func.count())
            .select_from(CharacterProvisional)
            .where(
                CharacterProvisional.project_id == project_id,
                CharacterProvisional.status == ProvisionalStatus.pending,
            )
        )
        return int(result or 0)

    async def get_pending_by_fingerprint(
        self, project_id: uuid.UUID, fingerprint: str
    ) -> CharacterProvisional | None:
        return await self.session.scalar(
            select(CharacterProvisional).where(
                CharacterProvisional.project_id == project_id,
                CharacterProvisional.mention_fingerprint == fingerprint,
                CharacterProvisional.status == ProvisionalStatus.pending,
            )
        )

    async def has_pending_fingerprint(self, project_id: uuid.UUID, fingerprint: str) -> bool:
        row = await self.get_pending_by_fingerprint(project_id, fingerprint)
        return row is not None
