"""Scene beat business logic."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BeatKeyConflictError, ChapterLockedError, NotFoundError
from app.models.chapter import Chapter
from app.models.scene_beat import SceneBeat
from app.repositories.beat import BeatRepository
from app.schemas.beat import SceneBeat as SceneBeatSchema
from app.schemas.beat import SceneBeatCreateRequest, SceneBeatUpdateRequest
from app.services.chapter_status import is_chapter_locked


class BeatService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.beats = BeatRepository(session)

    def _ensure_editable(self, chapter: Chapter) -> None:
        if is_chapter_locked(chapter.status):
            raise ChapterLockedError()

    async def list_beats(self, chapter: Chapter) -> list[SceneBeatSchema]:
        items = await self.beats.list_for_chapter(chapter.id)
        return [SceneBeatSchema.model_validate(item) for item in items]

    async def create_beat(
        self, chapter: Chapter, payload: SceneBeatCreateRequest
    ) -> SceneBeatSchema:
        self._ensure_editable(chapter)
        if await self.beats.beat_key_exists(chapter.id, payload.beat_key):
            raise BeatKeyConflictError(payload.beat_key)
        beat = SceneBeat(
            project_id=chapter.project_id,
            chapter_id=chapter.id,
            beat_key=payload.beat_key,
            summary=payload.summary,
            sort_order=payload.sort_order,
            completed=payload.completed,
        )
        created = await self.beats.create(beat)
        await self.session.refresh(created)
        return SceneBeatSchema.model_validate(created)

    async def update_beat(
        self,
        chapter: Chapter,
        beat_id: uuid.UUID,
        payload: SceneBeatUpdateRequest,
    ) -> SceneBeatSchema:
        self._ensure_editable(chapter)
        beat = await self.beats.get(chapter.id, beat_id)
        if beat is None:
            raise NotFoundError()
        if payload.beat_key is not None:
            if await self.beats.beat_key_exists(chapter.id, payload.beat_key, exclude_id=beat_id):
                raise BeatKeyConflictError(payload.beat_key)
            beat.beat_key = payload.beat_key
        if payload.summary is not None:
            beat.summary = payload.summary
        if payload.sort_order is not None:
            beat.sort_order = payload.sort_order
        if payload.completed is not None:
            beat.completed = payload.completed
        updated = await self.beats.update(beat)
        await self.session.refresh(updated)
        return SceneBeatSchema.model_validate(updated)

    async def delete_beat(self, chapter: Chapter, beat_id: uuid.UUID) -> None:
        self._ensure_editable(chapter)
        beat = await self.beats.get(chapter.id, beat_id)
        if beat is None:
            raise NotFoundError()
        await self.beats.delete(beat)
