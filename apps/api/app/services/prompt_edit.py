"""Prompt edit business logic."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.exceptions import (
    ChapterLockedError,
    LLMProviderError,
    NotFoundError,
    PromptEditAlreadyAppliedError,
    PromptEditRateLimitedError,
)
from app.models.chapter import Chapter
from app.models.enums import ProseSource
from app.models.project import Project
from app.models.prompt_edit import PromptEditSession, PromptEditTurn
from app.models.prose_version import ProseVersion
from app.repositories.prompt_edit import PromptEditRepository
from app.repositories.prose import ProseRepository
from app.schemas.craft_pack import CraftContextPackRequest
from app.schemas.prompt_edit import (
    PromptEditApplyChapterSummary,
    PromptEditApplyRequest,
    PromptEditApplyResponse,
    PromptEditInstructRequest,
    PromptEditInstructResponse,
    PromptEditRegenerateRequest,
    PromptEditSessionListResponse,
    PromptEditSessionSummary,
    ProseVersionApplySummary,
)
from app.schemas.prompt_edit import (
    PromptEditTurn as PromptEditTurnSchema,
)
from app.services.chapter_status import is_chapter_locked
from app.services.craft_context_pack import CraftContextPackService
from app.services.llm.provider import complete_prose_edit
from app.utils.word_count import count_words

_rate_limit_store: dict[str, list[datetime]] = defaultdict(list)


class PromptEditService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.prompt_edit = PromptEditRepository(session)
        self.prose = ProseRepository(session)

    def _ensure_editable(self, chapter: Chapter) -> None:
        if is_chapter_locked(chapter.status):
            raise ChapterLockedError()

    def _check_rate_limit(self, chapter_id: uuid.UUID, user_id: uuid.UUID) -> None:
        settings = get_settings()
        key = f"{chapter_id}:{user_id}"
        now = datetime.now(UTC)
        window_start = now - timedelta(hours=1)
        recent = [t for t in _rate_limit_store[key] if t > window_start]
        if len(recent) >= settings.prompt_edit_rate_limit_per_hour:
            raise PromptEditRateLimitedError()
        recent.append(now)
        _rate_limit_store[key] = recent

    def _turn_schema(self, turn: PromptEditTurn) -> PromptEditTurnSchema:
        return PromptEditTurnSchema.model_validate(turn)

    async def _craft_context_slice(self, project: Project, chapter: Chapter) -> dict | None:
        try:
            pack = await CraftContextPackService(self.session).build_context_pack(
                project,
                CraftContextPackRequest(
                    chapter_id=chapter.id,
                    chapter_number=chapter.number,
                ),
            )
        except NotFoundError:
            return None
        return {
            "craft_pack_id": pack.craft_pack_id,
            "craft_beats": [b.model_dump() for b in pack.craft_beats],
            "craft_checklist_open": [c.model_dump() for c in pack.craft_checklist_open],
            "active_clues": [c.model_dump(mode="json") for c in pack.active_clues],
            "active_misdirections": [m.model_dump(mode="json") for m in pack.active_misdirections],
        }

    async def _resolve_base_prose(
        self, chapter: Chapter, base_prose_version: int | None
    ) -> tuple[int, str]:
        if base_prose_version is not None:
            row = await self.prose.get_version(chapter.id, base_prose_version)
        else:
            row = await self.prose.get_latest(chapter.id)
        if row is None:
            raise NotFoundError(message="Prose version not found")
        return row.version, row.content

    async def instruct(
        self,
        project: Project,
        chapter: Chapter,
        user_id: uuid.UUID,
        payload: PromptEditInstructRequest,
    ) -> PromptEditInstructResponse:
        self._ensure_editable(chapter)
        self._check_rate_limit(chapter.id, user_id)
        base_version, prose_content = await self._resolve_base_prose(
            chapter, payload.base_prose_version
        )

        craft_context = await self._craft_context_slice(project, chapter)
        try:
            llm_result = await complete_prose_edit(
                prose=prose_content,
                instruction=payload.instruction,
                craft_context=craft_context,
            )
        except LLMProviderError:
            raise

        session = PromptEditSession(
            project_id=project.id,
            chapter_id=chapter.id,
            base_prose_version=base_version,
            status="active",
            created_by=user_id,
        )
        await self.prompt_edit.create_session(session)
        turn = PromptEditTurn(
            project_id=project.id,
            session_id=session.id,
            turn_index=1,
            instruction=payload.instruction,
            proposed_content=llm_result.content,
            model=llm_result.model,
            provider=llm_result.provider,
            latency_ms=llm_result.latency_ms,
            token_usage=llm_result.token_usage,
        )
        created_turn = await self.prompt_edit.create_turn(turn)
        await self.session.refresh(created_turn)
        return PromptEditInstructResponse(
            session_id=session.id,
            turn=self._turn_schema(created_turn),
            base_prose_version=base_version,
        )

    async def regenerate(
        self,
        project: Project,
        chapter: Chapter,
        user_id: uuid.UUID,
        payload: PromptEditRegenerateRequest,
    ) -> PromptEditInstructResponse:
        self._ensure_editable(chapter)
        self._check_rate_limit(chapter.id, user_id)
        session = await self.prompt_edit.get_session(project.id, payload.session_id)
        if session is None or session.chapter_id != chapter.id:
            raise NotFoundError()
        source_turn = await self.prompt_edit.get_turn(project.id, payload.turn_id)
        if source_turn is None or source_turn.session_id != session.id:
            raise NotFoundError()
        base_version, prose_content = await self._resolve_base_prose(
            chapter, session.base_prose_version
        )
        craft_context = await self._craft_context_slice(project, chapter)
        try:
            llm_result = await complete_prose_edit(
                prose=prose_content,
                instruction=source_turn.instruction,
                craft_context=craft_context,
            )
        except LLMProviderError:
            raise
        next_index = await self.prompt_edit.max_turn_index(session.id) + 1
        turn = PromptEditTurn(
            project_id=project.id,
            session_id=session.id,
            turn_index=next_index,
            instruction=source_turn.instruction,
            proposed_content=llm_result.content,
            model=llm_result.model,
            provider=llm_result.provider,
            latency_ms=llm_result.latency_ms,
            token_usage=llm_result.token_usage,
        )
        created_turn = await self.prompt_edit.create_turn(turn)
        await self.session.refresh(created_turn)
        return PromptEditInstructResponse(
            session_id=session.id,
            turn=self._turn_schema(created_turn),
            base_prose_version=base_version,
        )

    async def apply(
        self,
        project: Project,
        chapter: Chapter,
        user_id: uuid.UUID,
        payload: PromptEditApplyRequest,
    ) -> PromptEditApplyResponse:
        self._ensure_editable(chapter)
        session = await self.prompt_edit.get_session(project.id, payload.session_id)
        if session is None or session.chapter_id != chapter.id:
            raise NotFoundError()
        turn = await self.prompt_edit.get_turn(project.id, payload.turn_id)
        if turn is None or turn.session_id != session.id:
            raise NotFoundError()
        if not turn.proposed_content:
            raise NotFoundError(message="Turn has no proposed content")
        if await self.prompt_edit.prose_version_exists_for_turn(turn.id):
            raise PromptEditAlreadyAppliedError()

        next_version = await self.prose.get_max_version(chapter.id) + 1
        word_count = count_words(turn.proposed_content)
        prose = ProseVersion(
            project_id=project.id,
            chapter_id=chapter.id,
            version=next_version,
            content=turn.proposed_content,
            word_count=word_count,
            source=ProseSource.ai_editor,
            created_by=user_id,
            prompt_edit_turn_id=turn.id,
        )
        created = await self.prose.create(prose)
        chapter.word_count = word_count
        chapter.current_prose_version = next_version
        session.status = "applied"
        session.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(created)
        return PromptEditApplyResponse(
            prose_version=ProseVersionApplySummary(
                version=created.version,
                source=created.source.value,
                word_count=created.word_count,
                created_at=created.created_at,
                prompt_edit_turn_id=created.prompt_edit_turn_id,
            ),
            chapter=PromptEditApplyChapterSummary(
                current_prose_version=chapter.current_prose_version,
                word_count=chapter.word_count,
            ),
        )

    async def list_sessions(
        self, project: Project, chapter: Chapter
    ) -> PromptEditSessionListResponse:
        sessions = await self.prompt_edit.list_sessions_for_chapter(project.id, chapter.id)
        items: list[PromptEditSessionSummary] = []
        for session in sessions:
            turns = await self.prompt_edit.list_turns_for_session(session.id)
            items.append(
                PromptEditSessionSummary(
                    id=session.id,
                    status=session.status,
                    base_prose_version=session.base_prose_version,
                    turns=[self._turn_schema(t) for t in turns],
                    created_at=session.created_at,
                )
            )
        return PromptEditSessionListResponse(items=items)
