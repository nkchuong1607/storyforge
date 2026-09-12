"""Prose version business logic."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ChapterLockedError, NotFoundError
from app.models.chapter import Chapter
from app.models.enums import ChapterStatus, ProseSource
from app.models.project import Project
from app.models.prose_version import ProseVersion
from app.repositories.prose import ProseRepository
from app.schemas.prose import (
    ProseVersionCompareResponse,
    ProseVersionCreateRequest,
    ProseVersionDetail,
    ProseVersionSummary,
)
from app.services.chapter_status import is_chapter_locked
from app.utils.pagination import PageParams, paginated
from app.utils.word_count import count_words


class ProseService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.prose = ProseRepository(session)

    def _ensure_editable(self, chapter: Chapter) -> None:
        if is_chapter_locked(chapter.status):
            raise ChapterLockedError()

    async def list_versions(self, chapter: Chapter, page: PageParams):
        items, total = await self.prose.list_for_chapter(chapter.id, page)
        summaries = [ProseVersionSummary.model_validate(item) for item in items]
        return paginated(summaries, page.page, page.page_size, total)

    async def get_version(self, chapter: Chapter, version: int) -> ProseVersionDetail:
        row = await self.prose.get_version(chapter.id, version)
        if row is None:
            raise NotFoundError()
        return ProseVersionDetail.model_validate(row)

    async def create_version(
        self,
        project: Project,
        chapter: Chapter,
        user_id: uuid.UUID,
        payload: ProseVersionCreateRequest,
    ) -> ProseVersionDetail:
        self._ensure_editable(chapter)
        next_version = await self.prose.get_max_version(chapter.id) + 1
        word_count = count_words(payload.content)
        prose = ProseVersion(
            project_id=project.id,
            chapter_id=chapter.id,
            version=next_version,
            content=payload.content,
            word_count=word_count,
            source=ProseSource.human,
            created_by=user_id,
        )
        created = await self.prose.create(prose)
        chapter.word_count = word_count
        chapter.current_prose_version = next_version
        if chapter.bible_version_at_draft is None:
            chapter.bible_version_at_draft = project.bible_version_current
        if chapter.status == ChapterStatus.planned:
            chapter.status = ChapterStatus.drafting
        await self.session.flush()
        await self.session.refresh(created)
        return ProseVersionDetail.model_validate(created)

    async def compare_versions(
        self, chapter: Chapter, from_version: int, to_version: int
    ) -> ProseVersionCompareResponse:
        from_row = await self.prose.get_version(chapter.id, from_version)
        to_row = await self.prose.get_version(chapter.id, to_version)
        if from_row is None or to_row is None:
            raise NotFoundError()
        return ProseVersionCompareResponse(
            from_version=from_version,
            to_version=to_version,
            word_count_delta=to_row.word_count - from_row.word_count,
            created_at_from=from_row.created_at,
            created_at_to=to_row.created_at,
        )
