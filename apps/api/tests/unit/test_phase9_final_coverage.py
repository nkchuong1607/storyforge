"""Final Phase 9 coverage helpers."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.bible import BibleEntryStaging
from app.models.enums import BibleSection, ResearchNoteStatus
from app.models.export_job import ExportJob
from app.models.project import Project
from app.models.research import ResearchNote
from app.schemas.research import ResearchPromoteRequest
from app.services.export_processor import process_export_job
from app.services.research import ResearchService
from app.workers.export_worker import ExportWorker


@pytest.mark.unit
async def test_export_worker_skips_missing_job() -> None:
    session_factory = MagicMock()
    session = AsyncMock()
    session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
    session_factory.return_value.__aexit__ = AsyncMock(return_value=None)
    session.get = AsyncMock(return_value=None)
    worker = ExportWorker(session_factory)
    await worker.process_job(uuid.uuid4())


@pytest.mark.unit
async def test_export_processor_skips_non_pending_job() -> None:
    session = AsyncMock()
    job = ExportJob(
        project_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        job_type="epub",
        status="done",
        options_json={},
    )
    job.id = uuid.uuid4()
    session.get = AsyncMock(return_value=job)
    await process_export_job(session, job.id)
    assert job.status == "done"


@pytest.mark.unit
async def test_research_promote_updates_existing_staging() -> None:
    session = AsyncMock()
    service = ResearchService(session)
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = uuid.uuid4()
    project.bible_version_current = 1
    note = ResearchNote(
        project_id=project.id,
        title="T",
        body_md="body",
        tags=[],
        status=ResearchNoteStatus.active.value,
    )
    note.id = uuid.uuid4()
    staging = BibleEntryStaging(
        project_id=project.id,
        entry_key="world.rule",
        section=BibleSection.world_rules,
        title="Old",
        content_md="old",
        metadata_={},
        base_bible_version=0,
        created_by=uuid.uuid4(),
    )
    staging.id = uuid.uuid4()
    service.research.get_note = AsyncMock(return_value=note)
    service.bible.get_staging_entry = AsyncMock(return_value=staging)
    service.bible.update_staging_entry = AsyncMock(return_value=staging)
    service.research.update_note = AsyncMock(return_value=note)
    session.refresh = AsyncMock()

    result = await service.promote_note(
        project,
        uuid.uuid4(),
        note.id,
        ResearchPromoteRequest(
            section="world",
            title="Updated",
            staging_entry_id=staging.id,
        ),
    )
    assert result.staging_entry_id == staging.id


@pytest.mark.unit
async def test_export_processor_project_missing() -> None:
    session = AsyncMock()
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
    with (
        patch("app.services.export_processor.ExportRepository") as export_repo_cls,
        patch("app.services.export_processor.ProjectRepository") as project_repo_cls,
    ):
        export_repo_cls.return_value.update = AsyncMock()
        project_repo_cls.return_value.get_by_id = AsyncMock(return_value=None)
        await process_export_job(session, job_id)
        assert job.status == "failed"
