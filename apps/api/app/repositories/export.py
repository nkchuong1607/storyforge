"""Export job persistence."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export_job import ExportJob
from app.utils.pagination import PageParams


class ExportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, job: ExportJob) -> ExportJob:
        self.session.add(job)
        await self.session.flush()
        return job

    async def get(self, project_id: uuid.UUID, job_id: uuid.UUID) -> ExportJob | None:
        return await self.session.scalar(
            select(ExportJob).where(
                ExportJob.project_id == project_id,
                ExportJob.id == job_id,
            )
        )

    async def list_jobs(
        self, project_id: uuid.UUID, page: PageParams
    ) -> tuple[list[ExportJob], int]:
        query = select(ExportJob).where(ExportJob.project_id == project_id)
        total = await self.session.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = await self.session.scalars(
            query.order_by(ExportJob.created_at.desc()).offset(page.offset).limit(page.page_size)
        )
        return list(rows.all()), int(total)

    async def update(self, job: ExportJob) -> ExportJob:
        await self.session.flush()
        return job

    async def delete(self, job: ExportJob) -> None:
        await self.session.delete(job)
        await self.session.flush()
