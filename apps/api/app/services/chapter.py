"""Chapter business logic."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ChapterNumberConflictError
from app.models.chapter import Chapter
from app.models.project import Project
from app.repositories.chapter import ChapterRepository
from app.schemas.chapter import Chapter as ChapterSchema
from app.schemas.chapter import ChapterCreateRequest
from app.utils.pagination import PageParams, paginated


class ChapterService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chapters = ChapterRepository(session)

    async def list_chapters(self, project: Project, page: PageParams):
        items, total = await self.chapters.list_for_project(project.id, page)
        chapters = [ChapterSchema.model_validate(item) for item in items]
        return paginated(chapters, page.page, page.page_size, total)

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
