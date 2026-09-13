"""Scene context pack service."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.project import Project
from app.repositories.beat import BeatRepository
from app.repositories.chapter import ChapterRepository
from app.schemas.scene_engine import (
    PressureTag,
    SceneContextPackBeat,
    SceneContextPackRequest,
    SceneContextPackResponse,
)
from app.services.scene_engine import SceneEngineService


class SceneContextPackService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chapters = ChapterRepository(session)
        self.beats = BeatRepository(session)

    async def build_context_pack(
        self, project: Project, payload: SceneContextPackRequest
    ) -> SceneContextPackResponse:
        chapter = await self.chapters.get(project.id, payload.chapter_id)
        if chapter is None:
            raise NotFoundError()

        beats = await self.beats.list_for_chapter(payload.chapter_id)
        if payload.beat_ids:
            beat_id_set = set(payload.beat_ids)
            beats = [b for b in beats if b.id in beat_id_set]

        result: list[SceneContextPackBeat] = []
        for beat in beats[: SceneEngineService.MAX_CONTEXT_BEATS]:
            if not payload.include_empty and not any(
                [beat.goal.strip(), beat.conflict.strip(), beat.outcome.strip()]
            ):
                continue
            tags = [PressureTag.model_validate(t) for t in (beat.pressure_tags or [])]
            result.append(
                SceneContextPackBeat(
                    beat_key=beat.beat_key,
                    goal=beat.goal,
                    conflict=beat.conflict,
                    outcome=beat.outcome,
                    stakes_level=beat.stakes_level,
                    pressure_tags=tags,
                )
            )

        return SceneContextPackResponse(beats=result)
