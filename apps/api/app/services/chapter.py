"""Chapter business logic."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ChapterLockedError, ChapterNumberConflictError, NotFoundError
from app.models.chapter import Chapter
from app.models.project import Project
from app.repositories.chapter import ChapterRepository
from app.schemas.chapter import Chapter as ChapterSchema
from app.schemas.chapter import ChapterCreateRequest, ChapterUpdateRequest
from app.services.chapter_status import is_chapter_locked, validate_status_transition
from app.utils.pagination import PageParams, paginated


class ChapterService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chapters = ChapterRepository(session)

    async def list_chapters(self, project: Project, page: PageParams):
        items, total = await self.chapters.list_for_project(project.id, page)
        chapters = [ChapterSchema.model_validate(item) for item in items]
        return paginated(chapters, page.page, page.page_size, total)

    async def get_chapter(self, project: Project, chapter_id) -> ChapterSchema:
        chapter = await self.chapters.get(project.id, chapter_id)
        if chapter is None:
            raise NotFoundError()
        return ChapterSchema.model_validate(chapter)

    async def create_chapter(
        self, project: Project, payload: ChapterCreateRequest
    ) -> ChapterSchema:
        if await self.chapters.chapter_number_exists(project.id, payload.number):
            raise ChapterNumberConflictError(payload.number)

        chapter = Chapter(
            project_id=project.id,
            number=payload.number,
            title=payload.title,
            status=payload.status,
        )
        created = await self.chapters.create(chapter)
        await self.session.refresh(created)
        return ChapterSchema.model_validate(created)

    async def update_chapter(
        self, project: Project, chapter_id, payload: ChapterUpdateRequest
    ) -> ChapterSchema:
        chapter = await self.chapters.get(project.id, chapter_id)
        if chapter is None:
            raise NotFoundError()
        if is_chapter_locked(chapter.status):
            raise ChapterLockedError()
        if payload.title is not None:
            chapter.title = payload.title
        if payload.status is not None:
            validate_status_transition(chapter.status, payload.status)
            chapter.status = payload.status
        updated = await self.chapters.update(chapter)
        await self.session.refresh(updated)
        return ChapterSchema.model_validate(updated)
