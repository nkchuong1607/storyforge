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
from app.services.scene_engine import SceneEngineService


class BeatService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.beats = BeatRepository(session)
        self.scene_engine = SceneEngineService(session)

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
        payload_dict = payload.model_dump()
        self.scene_engine.apply_beat_defaults(
            SceneBeat(
                project_id=chapter.project_id,
                chapter_id=chapter.id,
                beat_key="",
                sort_order=0,
            ),
            payload_dict,
        )
        settings = await self.scene_engine.settings_repo.ensure_settings(chapter.project_id)
        if payload.completed:
            self.scene_engine.validate_beat_fields(
                completed=payload.completed,
                outcome=payload.outcome or "",
                settings_row=settings,
            )
        beat = SceneBeat(
            project_id=chapter.project_id,
            chapter_id=chapter.id,
            beat_key=payload.beat_key,
            summary=payload.summary,
            sort_order=payload.sort_order,
            completed=payload.completed,
            goal=payload.goal or "",
            conflict=payload.conflict or "",
            outcome=payload.outcome or "",
            stakes_level=payload.stakes_level,
            pressure_tags=[t.model_dump() for t in payload.pressure_tags],
            pov_character_id=payload.pov_character_id,
            scene_type=payload.scene_type.value
            if hasattr(payload.scene_type, "value")
            else payload.scene_type,
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
        payload_dict = payload.model_dump(exclude_unset=True)
        self.scene_engine.apply_beat_defaults(beat, payload_dict)
        settings = await self.scene_engine.settings_repo.ensure_settings(chapter.project_id)
        completed = payload.completed if payload.completed is not None else beat.completed
        outcome = payload.outcome if payload.outcome is not None else beat.outcome
        self.scene_engine.validate_beat_fields(
            completed=completed,
            outcome=outcome,
            settings_row=settings,
        )
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
        if payload.goal is not None:
            beat.goal = payload.goal
        if payload.conflict is not None:
            beat.conflict = payload.conflict
        if payload.outcome is not None:
            beat.outcome = payload.outcome
        if "stakes_level" in payload_dict:
            beat.stakes_level = payload.stakes_level
        if payload.pressure_tags is not None:
            beat.pressure_tags = [t.model_dump() for t in payload.pressure_tags]
        if "pov_character_id" in payload_dict:
            beat.pov_character_id = payload.pov_character_id
        if payload.scene_type is not None:
            beat.scene_type = (
                payload.scene_type.value
                if hasattr(payload.scene_type, "value")
                else payload.scene_type
            )
        updated = await self.beats.update(beat)
        await self.session.refresh(updated)
        return SceneBeatSchema.model_validate(updated)

    async def delete_beat(self, chapter: Chapter, beat_id: uuid.UUID) -> None:
        self._ensure_editable(chapter)
        beat = await self.beats.get(chapter.id, beat_id)
        if beat is None:
            raise NotFoundError()
        await self.beats.delete(beat)
