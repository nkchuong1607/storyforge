"""Unit tests for Phase 9 services."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import (
    ExportJobNotDoneError,
    InvalidExportOptionsError,
    InvalidLinkTargetError,
    NoteNotEditableError,
    NotFoundError,
    SeriesNotAttachedError,
)
from app.models.enums import ExportChapterScope, ResearchNoteStatus
from app.models.export_job import ExportJob
from app.models.project import Project
from app.models.research import ResearchNote
from app.schemas.export import ExportJobCreateRequest, ExportJobOptions
from app.schemas.research import (
    ResearchNoteCreateRequest,
    ResearchNoteLinkCreateRequest,
    ResearchNoteUpdateRequest,
    ResearchPromoteRequest,
)
from app.schemas.series import SeriesOverrideCreateRequest
from app.services.export_service import ExportService
from app.services.research import ResearchService
from app.services.series import SeriesService
from app.utils.pagination import PageParams


def _project() -> Project:
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = uuid.uuid4()
    project.bible_version_current = 0
    return project


@pytest.mark.unit
async def test_research_create_and_update() -> None:
    session = AsyncMock()
    service = ResearchService(session)
    project = _project()
    note = ResearchNote(
        project_id=project.id,
        title="T",
        body_md="body",
        tags=[],
        status=ResearchNoteStatus.active.value,
    )
    note.id = uuid.uuid4()
    note.created_at = datetime.now(UTC)
    note.updated_at = datetime.now(UTC)
    service.research.create_note = AsyncMock(return_value=note)
    session.refresh = AsyncMock()

    created = await service.create_note(project, ResearchNoteCreateRequest(title="T"))
    assert created.title == "T"

    service.research.get_note = AsyncMock(return_value=note)
    service.research.update_note = AsyncMock(return_value=note)
    updated = await service.update_note(project, note.id, ResearchNoteUpdateRequest(title="New"))
    assert updated.title == "New"


@pytest.mark.unit
async def test_research_archive_promoted_raises() -> None:
    session = AsyncMock()
    service = ResearchService(session)
    project = _project()
    note = ResearchNote(
        project_id=project.id,
        title="T",
        body_md="",
        tags=[],
        status=ResearchNoteStatus.promoted.value,
    )
    note.id = uuid.uuid4()
    service.research.get_note = AsyncMock(return_value=note)
    with pytest.raises(NoteNotEditableError):
        await service.update_note(project, note.id, ResearchNoteUpdateRequest(title="X"))


@pytest.mark.unit
async def test_research_invalid_link_target() -> None:
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
    service.research.get_note = AsyncMock(return_value=note)
    with pytest.raises(InvalidLinkTargetError):
        await service.add_link(
            project,
            note.id,
            ResearchNoteLinkCreateRequest(link_type="character"),
        )


@pytest.mark.unit
async def test_research_promote_creates_staging() -> None:
    session = AsyncMock()
    service = ResearchService(session)
    project = _project()
    note = ResearchNote(
        project_id=project.id,
        title="T",
        body_md="Canon body",
        tags=[],
        status=ResearchNoteStatus.active.value,
    )
    note.id = uuid.uuid4()
    staging = MagicMock(id=uuid.uuid4())
    service.research.get_note = AsyncMock(return_value=note)
    service.bible.entry_key_exists = AsyncMock(return_value=False)
    service.bible.create_staging_entry = AsyncMock(return_value=staging)
    service.research.update_note = AsyncMock(return_value=note)
    session.refresh = AsyncMock()

    result = await service.promote_note(
        project,
        uuid.uuid4(),
        note.id,
        ResearchPromoteRequest(section="world", title="Rule"),
    )
    assert result.staging_entry_id == staging.id


@pytest.mark.unit
async def test_series_override_requires_attachment() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    project = _project()
    project.series_id = None
    with pytest.raises(SeriesNotAttachedError):
        await service.create_override(
            project,
            uuid.uuid4(),
            SeriesOverrideCreateRequest(
                overrides_series_key="world.rules",
                section="world",
                title="Override",
                content_md="content",
            ),
        )


@pytest.mark.unit
async def test_export_invalid_options() -> None:
    session = AsyncMock()
    service = ExportService(session)
    project = _project()
    with pytest.raises(InvalidExportOptionsError):
        await service.enqueue_job(
            project,
            uuid.uuid4(),
            ExportJobCreateRequest(
                job_type="epub",
                options=ExportJobOptions(
                    chapter_scope=ExportChapterScope.selected,
                    chapter_ids=None,
                ),
            ),
        )


@pytest.mark.unit
async def test_export_sync_enqueue(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    service = ExportService(session)
    project = _project()
    job = ExportJob(
        project_id=project.id,
        requested_by_user_id=uuid.uuid4(),
        job_type="epub",
        status="pending",
        options_json={},
    )
    job.id = uuid.uuid4()
    job.created_at = datetime.now(UTC)
    service.export.create = AsyncMock(return_value=job)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    monkeypatch.setattr(service.settings, "export_sync", True)
    monkeypatch.setattr(
        "app.services.export_service.process_export_job",
        AsyncMock(),
    )

    result = await service.enqueue_job(
        project,
        uuid.uuid4(),
        ExportJobCreateRequest(job_type="epub"),
    )
    assert result.job_type.value == "epub"


@pytest.mark.unit
async def test_research_search_returns_response() -> None:
    session = AsyncMock()
    service = ResearchService(session)
    project = _project()
    note = ResearchNote(
        project_id=project.id,
        title="Huyết Đan",
        body_md="text",
        tags=[],
        status=ResearchNoteStatus.active.value,
    )
    note.id = uuid.uuid4()
    note.created_at = datetime.now(UTC)
    note.updated_at = datetime.now(UTC)
    service.research.search_notes = AsyncMock(return_value=([(note, 0.9, "snippet")], 1))

    result = await service.search_notes(
        project, query="Huyết", status=None, tag=None, page=PageParams()
    )
    assert result.total == 1
    assert result.query == "Huyết"


@pytest.mark.unit
async def test_research_promote_idempotent() -> None:
    session = AsyncMock()
    service = ResearchService(session)
    project = _project()
    staging_id = uuid.uuid4()
    note = ResearchNote(
        project_id=project.id,
        title="T",
        body_md="body",
        tags=[],
        status=ResearchNoteStatus.promoted.value,
        promoted_to_staging_id=staging_id,
    )
    note.id = uuid.uuid4()
    service.research.get_note = AsyncMock(return_value=note)
    result = await service.promote_note(
        project,
        uuid.uuid4(),
        note.id,
        ResearchPromoteRequest(section="world", title="Rule"),
    )
    assert result.staging_entry_id == staging_id


@pytest.mark.unit
async def test_research_archive_note() -> None:
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
    service.research.get_note = AsyncMock(return_value=note)
    service.research.update_note = AsyncMock(return_value=note)
    await service.archive_note(project, note.id)
    assert note.status == ResearchNoteStatus.archived.value


@pytest.mark.unit
async def test_series_inherited_slice_with_drift() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    project = _project()
    project.series_id = uuid.uuid4()
    project.last_seen_series_slice_version = 1
    series = MagicMock(id=project.series_id, title="Series")
    latest = MagicMock(
        version=3,
        slice_json={"world": {}},
        inherited_sections=["world"],
    )
    service.series.get = AsyncMock(return_value=series)
    service.series.get_latest_slice = AsyncMock(return_value=latest)

    result = await service.get_inherited_slice(project)
    assert result.drift_warning is True
    assert result.slice_version == 3


@pytest.mark.unit
async def test_series_create_override_success() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    project = _project()
    project.series_id = uuid.uuid4()
    staging = MagicMock(
        id=uuid.uuid4(),
        project_id=project.id,
        title="Override",
        content_md="md",
        metadata_={"series_override": True},
    )
    service.bible.create_staging_entry = AsyncMock(return_value=staging)
    session.refresh = AsyncMock()

    result = await service.create_override(
        project,
        uuid.uuid4(),
        SeriesOverrideCreateRequest(
            overrides_series_key="world.rules",
            section="world",
            title="Override",
            content_md="content",
            override_reason="planned",
        ),
    )
    assert result.metadata["series_override"] is True


@pytest.mark.unit
async def test_export_cancel_and_download_errors() -> None:
    session = AsyncMock()
    service = ExportService(session)
    project = _project()
    service.export.get = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.cancel_job(project, uuid.uuid4())

    pending_job = ExportJob(
        project_id=project.id,
        requested_by_user_id=uuid.uuid4(),
        job_type="epub",
        status="pending",
        options_json={},
    )
    pending_job.id = uuid.uuid4()
    service.export.get = AsyncMock(return_value=pending_job)
    with pytest.raises(ExportJobNotDoneError):
        await service.download_artifact(project, pending_job.id)
