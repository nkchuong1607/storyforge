"""Project business logic."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import SlugConflictError
from app.models.bible import BibleEntryStaging, BibleVersion
from app.models.chapter import Chapter
from app.models.character import Character
from app.models.enums import ProjectMemberRole, ProjectStatus
from app.models.project import Project, ProjectMember
from app.repositories.bible import BibleRepository
from app.repositories.chapter import ChapterRepository
from app.repositories.character import CharacterRepository
from app.repositories.project import ProjectRepository
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectDetail,
    ProjectSummary,
    ProjectUpdateRequest,
)
from app.templates.seeds import get_template_seed
from app.utils.pagination import PageParams, paginated
from app.utils.slug import next_slug_candidate, slugify_title


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.projects = ProjectRepository(session)
        self.bible = BibleRepository(session)
        self.chapters = ChapterRepository(session)
        self.characters = CharacterRepository(session)

    async def _resolve_unique_slug(self, base_slug: str) -> str:
        attempt = 1
        while True:
            candidate = next_slug_candidate(base_slug, attempt)
            if not await self.projects.slug_exists(candidate):
                return candidate
            attempt += 1
            if attempt > 100:
                raise SlugConflictError(base_slug, f"{base_slug}-2")

    async def _to_detail(self, project: Project) -> ProjectDetail:
        chapter_count = await self.projects.count_chapters(project.id)
        bible_entry_count = await self.projects.count_bible_entries(project.id)
        summary = ProjectSummary.model_validate(project)
        return ProjectDetail(
            **summary.model_dump(),
            created_by=project.created_by,
            created_at=project.created_at,
            settings=project.settings,
            chapter_count=chapter_count,
            bible_entry_count=bible_entry_count,
        )

    async def create_project(
        self, user_id: uuid.UUID, payload: ProjectCreateRequest
    ) -> ProjectDetail:
        base_slug = payload.slug or slugify_title(payload.title)
        slug = base_slug if payload.slug else await self._resolve_unique_slug(base_slug)

        seed = get_template_seed(payload.template)
        snapshot_json = seed.build_snapshot_json(payload.template)

        project = Project(
            slug=slug,
            title=payload.title,
            description=payload.description,
            language=payload.language,
            genre_profile=payload.genre_profile,
            template=payload.template,
            created_by=user_id,
        )
        await self.projects.create(project)

        await self.projects.add_member(
            ProjectMember(
                project_id=project.id,
                user_id=user_id,
                role=ProjectMemberRole.owner,
            )
        )

        await self.bible.create_version(
            BibleVersion(
                project_id=project.id,
                version=0,
                snapshot_json=snapshot_json,
            )
        )

        for entry in seed.bible_entries:
            await self.bible.create_staging_entry(
                BibleEntryStaging(
                    project_id=project.id,
                    entry_key=entry.entry_key,
                    section=entry.section,
                    title=entry.title,
                    content_md=entry.content_md,
                    metadata_=entry.metadata,
                    base_bible_version=0,
                    created_by=user_id,
                )
            )

        for chapter_seed in seed.chapters:
            await self.chapters.create(
                Chapter(
                    project_id=project.id,
                    number=chapter_seed.number,
                    title=chapter_seed.title,
                    status=chapter_seed.status,
                )
            )

        for character_seed in seed.characters:
            await self.characters.create(
                Character(
                    project_id=project.id,
                    display_name=character_seed.display_name,
                    role_one_liner=character_seed.role_one_liner,
                )
            )

        await self.session.flush()
        await self.session.refresh(project)
        return await self._to_detail(project)

    async def _suggest_slug(self, base_slug: str) -> str:
        attempt = 2
        while attempt <= 100:
            candidate = next_slug_candidate(base_slug, attempt)
            if not await self.projects.slug_exists(candidate):
                return candidate
            attempt += 1
        return f"{base_slug}-2"

    async def list_projects(
        self,
        user_id: uuid.UUID,
        *,
        status: ProjectStatus | None,
        query: str | None,
        page: PageParams,
    ):
        items, total = await self.projects.list_for_user(
            user_id, status=status, query=query, page=page
        )
        summaries = [ProjectSummary.model_validate(item) for item in items]
        return paginated(summaries, page.page, page.page_size, total)

    async def get_project(self, project: Project) -> ProjectDetail:
        return await self._to_detail(project)

    async def update_project(
        self, project: Project, payload: ProjectUpdateRequest
    ) -> ProjectDetail:
        if payload.title is not None:
            project.title = payload.title
        if payload.description is not None:
            project.description = payload.description
        if payload.status is not None:
            project.status = payload.status
        if payload.settings is not None:
            project.settings = payload.settings
        await self.projects.update(project)
        await self.session.refresh(project)
        return await self._to_detail(project)

    async def archive_project(self, project: Project) -> None:
        if project.status == ProjectStatus.archived:
            return
        project.status = ProjectStatus.archived
        await self.projects.update(project)

    async def create_with_conflict_check(
        self, user_id: uuid.UUID, payload: ProjectCreateRequest
    ) -> ProjectDetail:
        if payload.slug:
            if await self.projects.slug_exists(payload.slug):
                suggested = await self._suggest_slug(payload.slug)
                raise SlugConflictError(payload.slug, suggested)
        return await self.create_project(user_id, payload)
