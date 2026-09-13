"""Export job worker — processes pending jobs to local artifacts."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.enums import ExportJobStatus
from app.models.export_job import ExportJob
from app.services.export_processor import process_export_job


class ExportWorker:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def process_job(self, job_id: uuid.UUID) -> None:
        async with self.session_factory() as session:
            job = await session.get(ExportJob, job_id)
            if job is None or job.status not in (
                ExportJobStatus.pending.value,
                ExportJobStatus.running.value,
            ):
                return
            job.status = ExportJobStatus.running.value
            job.started_at = datetime.now(UTC)
            await session.commit()

        try:
            await self._run_job(job_id)
        except Exception as exc:
            async with self.session_factory() as session:
                job = await session.get(ExportJob, job_id)
                if job:
                    job.status = ExportJobStatus.failed.value
                    job.error_message = str(exc)
                    job.finished_at = datetime.now(UTC)
                    await session.commit()

    async def _run_job(self, job_id: uuid.UUID) -> None:
        async with self.session_factory() as session:
            await process_export_job(session, job_id)
            await session.commit()


async def process_sync_queue(session_factory: async_sessionmaker[AsyncSession]) -> None:
    """Process all jobs in sync queue (test helper)."""
    from app.services.export.queue import get_export_queue

    queue = get_export_queue()
    if not hasattr(queue, "pending"):
        return
    worker = ExportWorker(session_factory)
    for item in list(queue.pending):
        await worker.process_job(uuid.UUID(item["job_id"]))
    queue.pending.clear()
