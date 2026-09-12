"""PsychState data access — append-only after settle."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import PsychStateAlreadySettledError, PsychStateImmutableError
from app.models.chapter import Chapter
from app.models.psych_state import PsychState
from app.utils.pagination import PageParams


class PsychStateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, project_id: uuid.UUID, psych_state_id: uuid.UUID
    ) -> PsychState | None:
        return await self.session.scalar(
            select(PsychState).where(
                PsychState.project_id == project_id,
                PsychState.id == psych_state_id,
            )
        )

    async def get_by_character_chapter(
        self,
        project_id: uuid.UUID,
        character_id: uuid.UUID,
        chapter_id: uuid.UUID,
    ) -> PsychState | None:
        return await self.session.scalar(
            select(PsychState).where(
                PsychState.project_id == project_id,
                PsychState.character_id == character_id,
                PsychState.chapter_id == chapter_id,
            )
        )

    async def exists_for_character_chapter(
        self,
        project_id: uuid.UUID,
        character_id: uuid.UUID,
        chapter_id: uuid.UUID,
    ) -> bool:
        row = await self.get_by_character_chapter(project_id, character_id, chapter_id)
        return row is not None

    async def create(self, psych_state: PsychState) -> PsychState:
        existing = await self.get_by_character_chapter(
            psych_state.project_id,
            psych_state.character_id,
            psych_state.chapter_id,
        )
        if existing is not None:
            raise PsychStateAlreadySettledError()
        self.session.add(psych_state)
        await self.session.flush()
        return psych_state

    def assert_immutable(self, psych_state: PsychState) -> None:
        if psych_state.settled_at is not None:
            raise PsychStateImmutableError()

    async def list_timeline(
        self,
        project_id: uuid.UUID,
        character_id: uuid.UUID,
        page: PageParams,
        *,
        from_chapter_number: int | None = None,
        to_chapter_number: int | None = None,
    ) -> tuple[list[tuple[PsychState, int]], int]:
        filters: list[Any] = [
            PsychState.project_id == project_id,
            PsychState.character_id == character_id,
        ]
        if from_chapter_number is not None:
            filters.append(Chapter.number >= from_chapter_number)
        if to_chapter_number is not None:
            filters.append(Chapter.number <= to_chapter_number)

        base = (
            select(PsychState, Chapter.number)
            .join(Chapter, Chapter.id == PsychState.chapter_id)
            .where(*filters)
            .order_by(Chapter.number.asc(), PsychState.settled_at.asc())
        )
        count_stmt = select(func.count()).select_from(base.subquery())
        total = int(await self.session.scalar(count_stmt) or 0)

        offset = (page.page - 1) * page.page_size
        rows = await self.session.execute(base.offset(offset).limit(page.page_size))
        return list(rows.all()), total

    async def get_latest_before_chapter(
        self,
        project_id: uuid.UUID,
        character_id: uuid.UUID,
        target_chapter_number: int,
    ) -> tuple[PsychState, int] | None:
        row = await self.session.execute(
            select(PsychState, Chapter.number)
            .join(Chapter, Chapter.id == PsychState.chapter_id)
            .where(
                PsychState.project_id == project_id,
                PsychState.character_id == character_id,
                Chapter.number < target_chapter_number,
            )
            .order_by(Chapter.number.desc(), PsychState.settled_at.desc())
            .limit(1)
        )
        result = row.first()
        return result if result is None else (result[0], result[1])

    async def list_latest_for_characters_before_chapter(
        self,
        project_id: uuid.UUID,
        character_ids: list[uuid.UUID],
        target_chapter_number: int,
    ) -> dict[uuid.UUID, tuple[PsychState, int]]:
        if not character_ids:
            return {}
        rows = await self.session.execute(
            select(PsychState, Chapter.number)
            .join(Chapter, Chapter.id == PsychState.chapter_id)
            .where(
                PsychState.project_id == project_id,
                PsychState.character_id.in_(character_ids),
                Chapter.number < target_chapter_number,
            )
            .order_by(PsychState.character_id, Chapter.number.desc(), PsychState.settled_at.desc())
        )
        latest: dict[uuid.UUID, tuple[PsychState, int]] = {}
        for psych_state, chapter_number in rows.all():
            if psych_state.character_id not in latest:
                latest[psych_state.character_id] = (psych_state, chapter_number)
        return latest
