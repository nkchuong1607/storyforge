"""Series and bible slice persistence."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.series import Series, SeriesBibleSlice, SeriesProject
from app.utils.pagination import PageParams


class SeriesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, series: Series) -> Series:
        self.session.add(series)
        await self.session.flush()
        return series

    async def get(self, series_id: uuid.UUID) -> Series | None:
        return await self.session.get(Series, series_id)

    async def get_for_owner(self, series_id: uuid.UUID, owner_id: uuid.UUID) -> Series | None:
        return await self.session.scalar(
            select(Series).where(Series.id == series_id, Series.owner_user_id == owner_id)
        )

    async def slug_exists(self, owner_id: uuid.UUID, slug: str) -> bool:
        row = await self.session.scalar(
            select(Series.id).where(Series.owner_user_id == owner_id, Series.slug == slug)
        )
        return row is not None

    async def list_for_owner(
        self, owner_id: uuid.UUID, page: PageParams
    ) -> tuple[list[Series], int]:
        query = select(Series).where(Series.owner_user_id == owner_id)
        total = await self.session.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = await self.session.scalars(
            query.order_by(Series.updated_at.desc()).offset(page.offset).limit(page.page_size)
        )
        return list(rows.all()), int(total)

    async def count_projects(self, series_id: uuid.UUID) -> int:
        return (
            await self.session.scalar(
                select(func.count())
                .select_from(SeriesProject)
                .where(SeriesProject.series_id == series_id)
            )
            or 0
        )

    async def list_series_projects(
        self, series_id: uuid.UUID
    ) -> list[tuple[SeriesProject, Project]]:
        rows = await self.session.execute(
            select(SeriesProject, Project)
            .join(Project, Project.id == SeriesProject.project_id)
            .where(SeriesProject.series_id == series_id)
            .order_by(SeriesProject.book_order)
        )
        return [(row[0], row[1]) for row in rows.all()]

    async def get_series_project(
        self, series_id: uuid.UUID, project_id: uuid.UUID
    ) -> SeriesProject | None:
        return await self.session.scalar(
            select(SeriesProject).where(
                SeriesProject.series_id == series_id,
                SeriesProject.project_id == project_id,
            )
        )

    async def get_series_for_project(self, project_id: uuid.UUID) -> Series | None:
        project = await self.session.get(Project, project_id)
        if project is None or project.series_id is None:
            return None
        return await self.session.get(Series, project.series_id)

    async def attach_project(self, link: SeriesProject, project: Project) -> SeriesProject:
        self.session.add(link)
        project.series_id = link.series_id
        await self.session.flush()
        return link

    async def detach_project(self, link: SeriesProject, project: Project) -> None:
        project.series_id = None
        await self.session.delete(link)
        await self.session.flush()

    async def get_latest_slice(self, series_id: uuid.UUID) -> SeriesBibleSlice | None:
        return await self.session.scalar(
            select(SeriesBibleSlice)
            .where(SeriesBibleSlice.series_id == series_id)
            .order_by(SeriesBibleSlice.version.desc())
            .limit(1)
        )

    async def create_slice(self, slice_row: SeriesBibleSlice) -> SeriesBibleSlice:
        self.session.add(slice_row)
        await self.session.flush()
        return slice_row

    async def next_slice_version(self, series_id: uuid.UUID) -> int:
        current = await self.get_latest_slice(series_id)
        return (current.version + 1) if current else 1

    async def get_series_by_hub(self, hub_project_id: uuid.UUID) -> Series | None:
        return await self.session.scalar(
            select(Series).where(Series.hub_project_id == hub_project_id)
        )

    async def project_in_series(self, project_id: uuid.UUID) -> bool:
        row = await self.session.scalar(
            select(SeriesProject.series_id).where(SeriesProject.project_id == project_id)
        )
        return row is not None
