"""Prompt edit session and turn data access."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt_edit import PromptEditSession, PromptEditTurn


class PromptEditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(self, session_row: PromptEditSession) -> PromptEditSession:
        self.session.add(session_row)
        await self.session.flush()
        return session_row

    async def get_session(
        self, project_id: uuid.UUID, session_id: uuid.UUID
    ) -> PromptEditSession | None:
        return await self.session.scalar(
            select(PromptEditSession).where(
                PromptEditSession.project_id == project_id,
                PromptEditSession.id == session_id,
            )
        )

    async def list_sessions_for_chapter(
        self, project_id: uuid.UUID, chapter_id: uuid.UUID
    ) -> list[PromptEditSession]:
        rows = await self.session.scalars(
            select(PromptEditSession)
            .where(
                PromptEditSession.project_id == project_id,
                PromptEditSession.chapter_id == chapter_id,
            )
            .order_by(PromptEditSession.created_at.desc())
        )
        return list(rows.all())

    async def create_turn(self, turn: PromptEditTurn) -> PromptEditTurn:
        self.session.add(turn)
        await self.session.flush()
        return turn

    async def get_turn(self, project_id: uuid.UUID, turn_id: uuid.UUID) -> PromptEditTurn | None:
        return await self.session.scalar(
            select(PromptEditTurn).where(
                PromptEditTurn.project_id == project_id,
                PromptEditTurn.id == turn_id,
            )
        )

    async def max_turn_index(self, session_id: uuid.UUID) -> int:
        from sqlalchemy import func

        result = await self.session.scalar(
            select(func.max(PromptEditTurn.turn_index)).where(
                PromptEditTurn.session_id == session_id
            )
        )
        return int(result) if result is not None else 0

    async def list_turns_for_session(self, session_id: uuid.UUID) -> list[PromptEditTurn]:
        rows = await self.session.scalars(
            select(PromptEditTurn)
            .where(PromptEditTurn.session_id == session_id)
            .order_by(PromptEditTurn.turn_index.asc())
        )
        return list(rows.all())

    async def prose_version_exists_for_turn(self, turn_id: uuid.UUID) -> bool:
        from app.models.prose_version import ProseVersion

        result = await self.session.scalar(
            select(ProseVersion.id).where(ProseVersion.prompt_edit_turn_id == turn_id)
        )
        return result is not None
