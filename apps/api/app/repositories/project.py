"""Project data access."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ProjectStatus
from app.models.project import Project, ProjectMember
from app.utils.pagination import PageParams


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def slug_exists(self, slug: str) -> bool:
        result = await self.session.scalar(select(Project.id).where(Project.slug == slug))
        return result is not None

    async def create(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        return project

    async def add_member(self, member: ProjectMember) -> ProjectMember:
        self.session.add(member)
        await self.session.flush()
        return member

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        return await self.session.get(Project, project_id)

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        status: ProjectStatus | None,
        query: str | None,
        page: PageParams,
    ) -> tuple[list[Project], int]:
        filters = [ProjectMember.user_id == user_id]
        if status is not None:
            filters.append(Project.status == status)
        if query:
            filters.append(Project.title.ilike(f"%{query}%"))

        base = (
            select(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(*filters)
            .order_by(Project.updated_at.desc())
        )
        count_stmt = (
            select(func.count())
            .select_from(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(*filters)
        )
        total = int(await self.session.scalar(count_stmt) or 0)
        rows = await self.session.scalars(base.offset(page.offset).limit(page.page_size))
        return list(rows.all()), total

    async def update(self, project: Project) -> Project:
        await self.session.flush()
        return project

    async def count_chapters(self, project_id: uuid.UUID) -> int:
        from app.models.chapter import Chapter

        return int(
            await self.session.scalar(
                select(func.count()).select_from(Chapter).where(Chapter.project_id == project_id)
            )
            or 0
        )

    async def count_bible_entries(self, project_id: uuid.UUID) -> int:
        from app.models.bible import BibleEntryStaging

        return int(
            await self.session.scalar(
                select(func.count())
                .select_from(BibleEntryStaging)
                .where(BibleEntryStaging.project_id == project_id)
            )
            or 0
        )

    async def is_member(self, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        result = await self.session.scalar(
            select(ProjectMember.id).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        return result is not None
