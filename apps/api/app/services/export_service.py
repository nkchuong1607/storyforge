"""Export job enqueue and download business logic."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.exceptions import (
    ExportJobNotDoneError,
    ExportJobRunningError,
    InvalidExportOptionsError,
    NotFoundError,
)
from app.models.enums import ExportChapterScope, ExportJobStatus, ExportJobType
from app.models.export_job import ExportJob
from app.models.project import Project
from app.repositories.export import ExportRepository
from app.schemas.export import ExportJob as ExportJobSchema
from app.schemas.export import ExportJobCreateRequest, ExportJobOptions
from app.services.export.queue import get_export_queue
from app.services.export_processor import process_export_job
from app.utils.pagination import PageParams, paginated


class ExportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.export = ExportRepository(session)
        self.settings = get_settings()

    def _job_schema(self, job: ExportJob, project_id: uuid.UUID) -> ExportJobSchema:
        options = ExportJobOptions.model_validate(job.options_json or {})
        download_url = None
        if job.status == ExportJobStatus.done.value and job.artifact_filename:
            download_url = f"/projects/{project_id}/export/jobs/{job.id}/download"
        return ExportJobSchema(
            id=job.id,
            project_id=job.project_id,
            job_type=ExportJobType(job.job_type),
            status=ExportJobStatus(job.status),
            options=options,
            artifact_filename=job.artifact_filename,
            artifact_size_bytes=job.artifact_size_bytes,
            download_url=download_url,
            error_message=job.error_message,
            result_json=job.result_json,
            started_at=job.started_at,
            finished_at=job.finished_at,
            created_at=job.created_at,
        )

    def _validate_options(self, options: ExportJobOptions) -> None:
        if options.chapter_scope == ExportChapterScope.selected and not options.chapter_ids:
            raise InvalidExportOptionsError("selected scope requires chapter_ids")

    async def enqueue_job(
        self,
        project: Project,
        user_id: uuid.UUID,
        payload: ExportJobCreateRequest,
    ) -> ExportJobSchema:
        self._validate_options(payload.options)
        job = ExportJob(
            project_id=project.id,
            requested_by_user_id=user_id,
            job_type=payload.job_type.value,
            status=ExportJobStatus.pending.value,
            options_json=payload.options.model_dump(mode="json"),
        )
        created = await self.export.create(job)
        await self.session.flush()

        if self.settings.export_sync:
            await process_export_job(self.session, created.id)
        else:
            queue = get_export_queue()
            queue.enqueue(created.id, project.id, payload.job_type.value)

        await self.session.refresh(created)
        return self._job_schema(created, project.id)

    async def list_jobs(self, project: Project, page: PageParams):
        items, total = await self.export.list_jobs(project.id, page)
        return paginated(
            [self._job_schema(j, project.id) for j in items],
            page.page,
            page.page_size,
            total,
        )

    async def get_job(self, project: Project, job_id: uuid.UUID) -> ExportJobSchema:
        job = await self.export.get(project.id, job_id)
        if job is None:
            raise NotFoundError()
        return self._job_schema(job, project.id)

    async def cancel_job(self, project: Project, job_id: uuid.UUID) -> None:
        job = await self.export.get(project.id, job_id)
        if job is None:
            raise NotFoundError()
        if job.status == ExportJobStatus.running.value:
            raise ExportJobRunningError()
        if job.artifact_path:
            path = Path(job.artifact_path)
            if path.exists():
                path.unlink()
        await self.export.delete(job)

    async def download_artifact(self, project: Project, job_id: uuid.UUID) -> FileResponse:
        job = await self.export.get(project.id, job_id)
        if job is None:
            raise NotFoundError()
        if job.status != ExportJobStatus.done.value or not job.artifact_path:
            raise ExportJobNotDoneError()
        path = Path(job.artifact_path)
        if not path.exists():
            raise NotFoundError(message="Artifact file missing")
        return FileResponse(
            path,
            filename=job.artifact_filename or path.name,
            media_type="application/octet-stream",
        )
