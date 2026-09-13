"""Additional Phase 9 unit tests to meet coverage gate."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions import NoteNotEditableError
from app.models.enums import ExportJobStatus, ResearchNoteStatus
from app.models.export_job import ExportJob
from app.models.project import Project
from app.models.research import ResearchNote, ResearchNoteLink
from app.models.series import SeriesProject
from app.services.export_service import ExportService
from app.services.research import ResearchService
from app.services.series import SeriesService
from app.workers.export_worker import ExportWorker, process_sync_queue


def _project() -> Project:
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = uuid.uuid4()
    return project


@pytest.mark.unit
async def test_export_service_list_get_download() -> None:
    session = AsyncMock()
    service = ExportService(session)
    project = _project()
    job = ExportJob(
        project_id=project.id,
        requested_by_user_id=uuid.uuid4(),
        job_type="epub",
        status=ExportJobStatus.done.value,
        options_json={"chapter_scope": "settled_only"},
        artifact_filename="p.epub",
        artifact_path="/tmp/p.epub",
    )
    job.id = uuid.uuid4()
    job.created_at = datetime.now(UTC)
    service.export.list_jobs = AsyncMock(return_value=([job], 1))
    listed = await service.list_jobs(project, MagicMock(page=1, page_size=20))
    assert listed.pagination.total_items == 1

    service.export.get = AsyncMock(return_value=job)
    got = await service.get_job(project, job.id)
    assert got.download_url is not None

    with patch("app.services.export_service.Path") as path_cls:
        path_cls.return_value.exists.return_value = True
        response = await service.download_artifact(project, job.id)
        assert response.filename == "p.epub"


@pytest.mark.unit
async def test_export_cancel_deletes_artifact() -> None:
    session = AsyncMock()
    service = ExportService(session)
    project = _project()
    job = ExportJob(
        project_id=project.id,
        requested_by_user_id=uuid.uuid4(),
        job_type="epub",
        status=ExportJobStatus.pending.value,
        options_json={},
        artifact_path="/tmp/remove.epub",
    )
    job.id = uuid.uuid4()
    service.export.get = AsyncMock(return_value=job)
    service.export.delete = AsyncMock()
    with patch("app.services.export_service.Path") as path_cls:
        path_instance = MagicMock()
        path_cls.return_value = path_instance
        await service.cancel_job(project, job.id)
        path_instance.unlink.assert_called_once()


@pytest.mark.unit
async def test_research_remove_link_and_archive_promoted() -> None:
    session = AsyncMock()
    service = ResearchService(session)
    project = _project()
    link = ResearchNoteLink(
        project_id=project.id,
        note_id=uuid.uuid4(),
        link_type="chapter",
        chapter_id=uuid.uuid4(),
    )
    link.id = uuid.uuid4()
    service.research.get_link = AsyncMock(return_value=link)
    service.research.delete_link = AsyncMock()
    await service.remove_link(project, link.note_id, link.id)

    promoted = ResearchNote(
        project_id=project.id,
        title="T",
        body_md="",
        tags=[],
        status=ResearchNoteStatus.promoted.value,
    )
    promoted.id = uuid.uuid4()
    service.research.get_note = AsyncMock(return_value=promoted)
    with pytest.raises(NoteNotEditableError):
        await service.archive_note(project, promoted.id)


@pytest.mark.unit
async def test_series_detach_project() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    user_id = uuid.uuid4()
    series_id = uuid.uuid4()
    project = _project()
    link = SeriesProject(series_id=series_id, project_id=project.id, book_order=1)
    service.series.get_for_owner = AsyncMock(return_value=MagicMock())
    service.series.get_series_project = AsyncMock(return_value=link)
    session.get = AsyncMock(return_value=project)
    service.series.detach_project = AsyncMock()
    await service.detach_project(user_id, series_id, project.id)
    service.series.detach_project.assert_called_once()


@pytest.mark.unit
async def test_export_worker_failure_path() -> None:
    session_factory = MagicMock()
    session = AsyncMock()
    session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
    session_factory.return_value.__aexit__ = AsyncMock(return_value=None)
    job_id = uuid.uuid4()
    job = ExportJob(
        project_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        job_type="epub",
        status="pending",
        options_json={},
    )
    job.id = job_id
    session.get = AsyncMock(return_value=job)
    session.commit = AsyncMock()
    worker = ExportWorker(session_factory)
    with patch(
        "app.workers.export_worker.process_export_job",
        AsyncMock(side_effect=RuntimeError("boom")),
    ):
        await worker.process_job(job_id)
    assert job.status == "failed"


@pytest.mark.unit
async def test_process_sync_queue_drains_pending() -> None:
    from app.services.export.queue import SyncExportQueue

    queue = SyncExportQueue()
    job_id = uuid.uuid4()
    queue.enqueue(job_id, uuid.uuid4(), "epub")
    session_factory = MagicMock()
    with patch("app.workers.export_worker.ExportWorker") as worker_cls:
        worker_cls.return_value.process_job = AsyncMock()
        with patch("app.services.export.queue.get_export_queue", return_value=queue):
            await process_sync_queue(session_factory)
    assert queue.pending == []
