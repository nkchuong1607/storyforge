"""Extended Phase 9 service unit tests for coverage."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions import (
    ExportJobRunningError,
    ProjectAlreadyInSeriesError,
    SlugConflictError,
)
from app.models.enums import ResearchNoteLinkType, ResearchNoteStatus
from app.models.export_job import ExportJob
from app.models.project import Project
from app.models.research import ResearchNote, ResearchNoteLink
from app.models.series import Series, SeriesBibleSlice
from app.schemas.research import ResearchNoteLinkCreateRequest
from app.schemas.series import (
    SeriesAttachProjectRequest,
    SeriesCreateRequest,
    SeriesUpdateRequest,
)
from app.services.export.builders import build_docx_bytes
from app.services.export_service import ExportService
from app.services.research import ResearchService
from app.services.series import SeriesService
from app.utils.pagination import PageParams
from app.workers.export_worker import ExportWorker


def _project() -> Project:
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = uuid.uuid4()
    project.bible_version_current = 0
    return project


@pytest.mark.unit
async def test_series_create_and_list() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    user_id = uuid.uuid4()
    series = Series(owner_user_id=user_id, title="S", slug="s")
    series.id = uuid.uuid4()
    series.created_at = datetime.now(UTC)
    series.updated_at = datetime.now(UTC)
    service.series.slug_exists = AsyncMock(return_value=False)
    service.series.create = AsyncMock(return_value=series)
    service.series.get_for_owner = AsyncMock(return_value=series)
    service.series.count_projects = AsyncMock(return_value=0)
    service.series.list_series_projects = AsyncMock(return_value=[])
    service.series.get_latest_slice = AsyncMock(return_value=None)
    session.refresh = AsyncMock()

    detail = await service.create_series(
        user_id,
        SeriesCreateRequest(title="S", slug="s", create_hub_project=False),
    )
    assert detail.slug == "s"

    service.series.list_for_owner = AsyncMock(return_value=([series], 1))
    service.series.count_projects = AsyncMock(return_value=0)
    listed = await service.list_series(user_id, PageParams())
    assert listed.pagination.total_items == 1


@pytest.mark.unit
async def test_series_slug_conflict() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    service.series.slug_exists = AsyncMock(return_value=True)
    with pytest.raises(SlugConflictError):
        await service.create_series(
            uuid.uuid4(),
            SeriesCreateRequest(title="S", slug="s", create_hub_project=False),
        )


@pytest.mark.unit
async def test_series_attach_project_conflict() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    user_id = uuid.uuid4()
    series_id = uuid.uuid4()
    project = _project()
    project.series_id = uuid.uuid4()
    series = Series(owner_user_id=user_id, title="S", slug="s")
    series.id = series_id
    service.series.get_for_owner = AsyncMock(return_value=series)
    service._ensure_project_access = AsyncMock(return_value=project)
    service.series.project_in_series = AsyncMock(return_value=True)
    with pytest.raises(ProjectAlreadyInSeriesError):
        await service.attach_project(
            user_id,
            series_id,
            SeriesAttachProjectRequest(project_id=project.id),
        )


@pytest.mark.unit
async def test_series_update_and_bible_slice() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    user_id = uuid.uuid4()
    series = Series(owner_user_id=user_id, title="S", slug="s")
    series.id = uuid.uuid4()
    series.created_at = datetime.now(UTC)
    series.updated_at = datetime.now(UTC)
    slice_row = SeriesBibleSlice(
        series_id=series.id,
        version=1,
        slice_json={"world": {}},
        inherited_sections=["world"],
    )
    slice_row.settled_at = datetime.now(UTC)
    service.series.get_for_owner = AsyncMock(return_value=series)
    service.series.slug_exists = AsyncMock(return_value=False)
    service.series.list_series_projects = AsyncMock(return_value=[])
    service.series.get_latest_slice = AsyncMock(return_value=slice_row)
    service.series.count_projects = AsyncMock(return_value=0)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    updated = await service.update_series(
        user_id, series.id, SeriesUpdateRequest(title="New title")
    )
    assert updated.title == "New title"
    bible = await service.get_bible_slice(user_id, series.id)
    assert bible.version == 1


@pytest.mark.unit
async def test_series_publish_slice_from_hub() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    project = _project()
    series = Series(owner_user_id=uuid.uuid4(), title="S", slug="s")
    series.id = uuid.uuid4()
    service.series.get_series_by_hub = AsyncMock(return_value=series)
    service.series.next_slice_version = AsyncMock(return_value=1)
    service.series.create_slice = AsyncMock(
        return_value=SeriesBibleSlice(
            series_id=series.id,
            version=1,
            slice_json={},
            inherited_sections=["world"],
        )
    )
    result = await service.publish_slice_from_hub(project, {"entries": []}, 1)
    assert result is not None


@pytest.mark.unit
async def test_research_list_and_link_place() -> None:
    session = AsyncMock()
    service = ResearchService(session)
    project = _project()
    note = ResearchNote(
        project_id=project.id,
        title="T",
        body_md="",
        tags=["a"],
        status=ResearchNoteStatus.active.value,
    )
    note.id = uuid.uuid4()
    note.created_at = datetime.now(UTC)
    note.updated_at = datetime.now(UTC)
    service.research.list_notes = AsyncMock(return_value=([note], 1))
    listed = await service.list_notes(
        project, status=ResearchNoteStatus.active, tag="a", page=PageParams()
    )
    assert listed.pagination.total_items == 1

    service.research.get_note = AsyncMock(return_value=note)
    link = ResearchNoteLink(
        project_id=project.id,
        note_id=note.id,
        link_type="place",
        bible_key="world.locations.hall",
    )
    link.id = uuid.uuid4()
    link.created_at = datetime.now(UTC)
    service.research.create_link = AsyncMock(return_value=link)
    session.refresh = AsyncMock()
    created_link = await service.add_link(
        project,
        note.id,
        ResearchNoteLinkCreateRequest(
            link_type=ResearchNoteLinkType.place,
            bible_key="world.locations.hall",
        ),
    )
    assert created_link.bible_key == "world.locations.hall"


@pytest.mark.unit
async def test_research_get_note_with_links() -> None:
    session = AsyncMock()
    service = ResearchService(session)
    project = _project()
    note = ResearchNote(
        project_id=project.id,
        title="T",
        body_md="",
        tags=[],
        status=ResearchNoteStatus.active.value,
    )
    note.id = uuid.uuid4()
    note.created_at = datetime.now(UTC)
    note.updated_at = datetime.now(UTC)
    service.research.get_note = AsyncMock(return_value=note)
    service.research.list_links = AsyncMock(return_value=[])
    detail = await service.get_note(project, note.id)
    assert detail.title == "T"


@pytest.mark.unit
async def test_export_cancel_running_job() -> None:
    session = AsyncMock()
    service = ExportService(session)
    project = _project()
    job = ExportJob(
        project_id=project.id,
        requested_by_user_id=uuid.uuid4(),
        job_type="epub",
        status="running",
        options_json={},
    )
    job.id = uuid.uuid4()
    service.export.get = AsyncMock(return_value=job)
    with pytest.raises(ExportJobRunningError):
        await service.cancel_job(project, job.id)


@pytest.mark.unit
def test_build_docx_bytes() -> None:
    project = _project()
    from app.models.chapter import Chapter
    from app.models.enums import ChapterStatus

    chapter = Chapter(
        project_id=project.id,
        number=1,
        title="Ch1",
        status=ChapterStatus.settled,
    )
    chapter.id = uuid.uuid4()
    data = build_docx_bytes(project, [chapter], {str(chapter.id): "Prose"}, strip_secrets=True)
    assert data[:2] == b"PK"


@pytest.mark.unit
async def test_export_worker_process_job() -> None:
    factory = MagicMock()
    session = AsyncMock()
    factory.return_value.__aenter__ = AsyncMock(return_value=session)
    factory.return_value.__aexit__ = AsyncMock(return_value=None)
    worker = ExportWorker(factory)
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
    with patch("app.workers.export_worker.process_export_job", AsyncMock()):
        await worker.process_job(job_id)
