"""Series and inherited bible slice business logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    NotFoundError,
    ProjectAlreadyInSeriesError,
    SeriesNotAttachedError,
    SlugConflictError,
)
from app.models.bible import BibleEntryStaging
from app.models.enums import (
    GenreProfile,
    Phase9BibleSection,
    ProjectLanguage,
    ProjectTemplate,
)
from app.models.project import Project, ProjectMember
from app.models.series import Series, SeriesBibleSlice, SeriesProject
from app.repositories.bible import BibleRepository
from app.repositories.series import SeriesRepository
from app.schemas.project import ProjectCreateRequest
from app.schemas.series import (
    ProjectInheritedSliceResponse,
    SeriesAttachProjectRequest,
    SeriesCreateRequest,
    SeriesDetail,
    SeriesOverrideCreateRequest,
    SeriesOverrideStagingEntry,
    SeriesProjectLink,
    SeriesSummary,
    SeriesUpdateRequest,
)
from app.schemas.series import (
    SeriesBibleSlice as SeriesBibleSliceSchema,
)
from app.services.project import ProjectService
from app.utils.pagination import PageParams, paginated
from app.utils.phase9_bible import (
    DEFAULT_INHERITED_SECTIONS,
    build_entry_key,
    phase9_section_to_bible_section,
    snapshot_to_slice_json,
)


class SeriesService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.series = SeriesRepository(session)
        self.bible = BibleRepository(session)

    async def _ensure_project_access(self, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
        membership = await self.session.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        if membership is None:
            raise NotFoundError()
        project = await self.session.get(Project, project_id)
        if project is None:
            raise NotFoundError()
        return project

    async def list_series(self, user_id: uuid.UUID, page: PageParams):
        items, total = await self.series.list_for_owner(user_id, page)
        summaries = []
        for item in items:
            book_count = await self.series.count_projects(item.id)
            summaries.append(
                SeriesSummary(
                    id=item.id,
                    title=item.title,
                    slug=item.slug,
                    book_count=book_count,
                    hub_project_id=item.hub_project_id,
                    created_at=item.created_at,
                )
            )
        return paginated(summaries, page.page, page.page_size, total)

    async def create_series(self, user_id: uuid.UUID, payload: SeriesCreateRequest) -> SeriesDetail:
        if await self.series.slug_exists(user_id, payload.slug):
            raise SlugConflictError(payload.slug, f"{payload.slug}-2")

        hub_project_id = None
        if payload.create_hub_project:
            hub_title = payload.hub_project_title or f"{payload.title} — Series Bible Hub"
            hub = await ProjectService(self.session).create_project(
                user_id,
                ProjectCreateRequest(
                    title=hub_title,
                    slug=f"{payload.slug}-hub",
                    language=ProjectLanguage.vi,
                    genre_profile=GenreProfile.custom,
                    template=ProjectTemplate.blank,
                ),
            )
            hub_project_id = hub.id

        series = Series(
            owner_user_id=user_id,
            title=payload.title,
            slug=payload.slug,
            hub_project_id=hub_project_id,
        )
        created = await self.series.create(series)
        await self.session.refresh(created)
        return await self.get_series(user_id, created.id)

    async def get_series(self, user_id: uuid.UUID, series_id: uuid.UUID) -> SeriesDetail:
        series = await self.series.get_for_owner(series_id, user_id)
        if series is None:
            raise NotFoundError()
        return await self._to_detail(series)

    async def _to_detail(self, series: Series) -> SeriesDetail:
        links = await self.series.list_series_projects(series.id)
        latest = await self.series.get_latest_slice(series.id)
        return SeriesDetail(
            id=series.id,
            title=series.title,
            slug=series.slug,
            hub_project_id=series.hub_project_id,
            slice_version_current=latest.version if latest else 0,
            projects=[
                SeriesProjectLink(
                    series_id=series.id,
                    project_id=proj.id,
                    book_order=link.book_order,
                    project_title=proj.title,
                    attached_at=link.attached_at,
                )
                for link, proj in links
            ],
            created_at=series.created_at,
            updated_at=series.updated_at,
        )

    async def update_series(
        self, user_id: uuid.UUID, series_id: uuid.UUID, payload: SeriesUpdateRequest
    ) -> SeriesDetail:
        series = await self.series.get_for_owner(series_id, user_id)
        if series is None:
            raise NotFoundError()
        if payload.title is not None:
            series.title = payload.title
        if payload.slug is not None and payload.slug != series.slug:
            if await self.series.slug_exists(user_id, payload.slug):
                raise SlugConflictError(payload.slug, f"{payload.slug}-2")
            series.slug = payload.slug
        await self.session.flush()
        await self.session.refresh(series)
        return await self._to_detail(series)

    async def get_bible_slice(
        self, user_id: uuid.UUID, series_id: uuid.UUID
    ) -> SeriesBibleSliceSchema:
        series = await self.series.get_for_owner(series_id, user_id)
        if series is None:
            raise NotFoundError()
        latest = await self.series.get_latest_slice(series_id)
        if latest is None:
            return SeriesBibleSliceSchema(
                series_id=series_id,
                version=0,
                slice_json={s: {} for s in DEFAULT_INHERITED_SECTIONS},
                inherited_sections=DEFAULT_INHERITED_SECTIONS,
                settled_at=datetime.now(UTC),
            )
        return SeriesBibleSliceSchema(
            series_id=latest.series_id,
            version=latest.version,
            slice_json=latest.slice_json,
            inherited_sections=list(latest.inherited_sections or DEFAULT_INHERITED_SECTIONS),
            settled_at=latest.settled_at,
        )

    async def attach_project(
        self,
        user_id: uuid.UUID,
        series_id: uuid.UUID,
        payload: SeriesAttachProjectRequest,
    ) -> SeriesProjectLink:
        series = await self.series.get_for_owner(series_id, user_id)
        if series is None:
            raise NotFoundError()
        project = await self._ensure_project_access(payload.project_id, user_id)
        if project.series_id is not None or await self.series.project_in_series(project.id):
            raise ProjectAlreadyInSeriesError()

        link = SeriesProject(
            series_id=series_id,
            project_id=project.id,
            book_order=payload.book_order,
        )
        created = await self.series.attach_project(link, project)
        await self.session.refresh(created)
        return SeriesProjectLink(
            series_id=series_id,
            project_id=project.id,
            book_order=created.book_order,
            project_title=project.title,
            attached_at=created.attached_at,
        )

    async def detach_project(
        self, user_id: uuid.UUID, series_id: uuid.UUID, project_id: uuid.UUID
    ) -> None:
        series = await self.series.get_for_owner(series_id, user_id)
        if series is None:
            raise NotFoundError()
        link = await self.series.get_series_project(series_id, project_id)
        if link is None:
            raise NotFoundError()
        project = await self.session.get(Project, project_id)
        if project is None:
            raise NotFoundError()
        await self.series.detach_project(link, project)

    async def get_inherited_slice(self, project: Project) -> ProjectInheritedSliceResponse:
        if project.series_id is None:
            raise SeriesNotAttachedError()
        series = await self.series.get(project.series_id)
        if series is None:
            raise SeriesNotAttachedError()
        latest = await self.series.get_latest_slice(series.id)
        slice_version = latest.version if latest else 0
        slice_json = latest.slice_json if latest else {s: {} for s in DEFAULT_INHERITED_SECTIONS}
        inherited = list(latest.inherited_sections) if latest else DEFAULT_INHERITED_SECTIONS
        last_seen = project.last_seen_series_slice_version
        drift = slice_version > (last_seen or 0)
        return ProjectInheritedSliceResponse(
            project_id=project.id,
            series_id=series.id,
            series_title=series.title,
            slice_version=slice_version,
            last_seen_slice_version=last_seen,
            inherited_sections=inherited,
            slice_json=slice_json,
            read_only=True,
            drift_warning=drift,
        )

    async def create_override(
        self,
        project: Project,
        user_id: uuid.UUID,
        payload: SeriesOverrideCreateRequest,
    ) -> SeriesOverrideStagingEntry:
        if project.series_id is None:
            raise SeriesNotAttachedError()
        try:
            phase9_section = Phase9BibleSection(payload.section)
        except ValueError as exc:
            raise SeriesNotAttachedError("Invalid section") from exc

        bible_section = phase9_section_to_bible_section(phase9_section)
        entry_key = build_entry_key(phase9_section, payload.title)
        metadata = {
            "series_override": True,
            "overrides_series_key": payload.overrides_series_key,
        }
        if payload.override_reason:
            metadata["override_reason"] = payload.override_reason

        staging = BibleEntryStaging(
            project_id=project.id,
            entry_key=entry_key,
            section=bible_section,
            title=payload.title,
            content_md=payload.content_md,
            metadata_=metadata,
            base_bible_version=project.bible_version_current,
            created_by=user_id,
        )
        created = await self.bible.create_staging_entry(staging)
        await self.session.refresh(created)
        return SeriesOverrideStagingEntry(
            id=created.id,
            project_id=created.project_id,
            section=payload.section,
            title=created.title,
            content_md=created.content_md,
            metadata=created.metadata_,
        )

    async def publish_slice_from_hub(
        self,
        hub_project: Project,
        snapshot_json: dict,
        bible_version: int,
    ) -> SeriesBibleSlice | None:
        """Append series bible slice when hub project settles."""
        series = await self.series.get_series_by_hub(hub_project.id)
        if series is None:
            return None
        version = await self.series.next_slice_version(series.id)
        inherited = DEFAULT_INHERITED_SECTIONS
        slice_row = SeriesBibleSlice(
            series_id=series.id,
            version=version,
            slice_json=snapshot_to_slice_json(snapshot_json, inherited),
            inherited_sections=inherited,
            settled_from_hub_bible_version=bible_version,
        )
        return await self.series.create_slice(slice_row)

    async def mark_slice_seen(self, project: Project) -> None:
        if project.series_id is None:
            return
        latest = await self.series.get_latest_slice(project.series_id)
        if latest:
            project.last_seen_series_slice_version = latest.version
