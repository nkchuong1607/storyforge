"""Stakes context pack service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.project import Project
from app.repositories.chapter import ChapterRepository
from app.repositories.stakes import StakesRepository
from app.schemas.stakes import (
    StakesContextPackCheckpoint,
    StakesContextPackRequest,
    StakesContextPackResponse,
)
from app.services.continuity.stakes import resolve_act_for_chapter


class StakesContextPackService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chapters = ChapterRepository(session)
        self.stakes = StakesRepository(session)

    async def build_context_pack(
        self, project: Project, payload: StakesContextPackRequest
    ) -> StakesContextPackResponse:
        chapter = await self.chapters.get(project.id, payload.chapter_id)
        if chapter is None:
            raise NotFoundError()

        settings = await self.stakes.ensure_settings(project.id)
        act_number, _, _ = resolve_act_for_chapter(chapter.number, settings)
        entries = await self.stakes.list_entries_for_act(project.id, act_number)
        checkpoints = [
            StakesContextPackCheckpoint(
                checkpoint_key=e.checkpoint_key,
                target_level=e.target_level,
                status=e.status,
            )
            for e in entries
        ]
        peak = max((e.target_level for e in entries), default=0)
        return StakesContextPackResponse(
            act_number=act_number,
            current_peak_level=peak or None,
            checkpoints=checkpoints,
        )
