"""Phase 10 service unit tests with mocks."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import (
    ClaimAlreadyPromotedError,
    ClaimNoCitationsError,
    ClaimNoProposedCorrectionError,
    FactCheckRunPendingError,
    InvalidClaimCategoryError,
    InvalidRealityAnchorsError,
    NotFoundError,
)
from app.models.enums import (
    FactCheckRunStatus,
    ResearchNoteStatus,
)
from app.models.fact_check import FactCheckRun, FactCitation, FactClaim
from app.models.project import Project
from app.models.project_reality_settings import ProjectRealitySettings
from app.models.prose_version import ProseVersion
from app.models.research import ResearchNote
from app.schemas.fact_check import (
    FactClaimAcceptFixRequest,
)
from app.schemas.reality_settings import ProjectRealitySettingsUpdate
from app.services.fact_check.queue import SyncFactCheckQueue, reset_fact_check_queue
from app.services.fact_check_service import FactCheckService
from app.services.reality_settings_service import RealitySettingsService


def _project() -> Project:
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = uuid.uuid4()
    return project


def _reality_row(project_id: uuid.UUID) -> ProjectRealitySettings:
    row = ProjectRealitySettings(project_id=project_id)
    row.reality_anchors = "strict"
    row.enabled_categories = []
    row.fact_check_blocks_settle = False
    row.auto_run_on_save = False
    row.include_research_notes = True
    row.updated_at = datetime.now(UTC)
    return row


@pytest.mark.unit
async def test_reality_settings_get_and_patch() -> None:
    session = AsyncMock()
    service = RealitySettingsService(session)
    project = _project()
    row = _reality_row(project.id)
    service.repo.ensure_settings = AsyncMock(return_value=row)
    session.refresh = AsyncMock()

    settings = await service.get_settings(project)
    assert settings.reality_anchors.value == "strict"

    updated = await service.update_settings(
        project,
        ProjectRealitySettingsUpdate(reality_anchors="off"),
    )
    assert updated.reality_anchors.value == "off"


@pytest.mark.unit
async def test_reality_settings_invalid_category() -> None:
    service = RealitySettingsService(AsyncMock())
    with pytest.raises(InvalidClaimCategoryError):
        service._validate_categories(["not_a_category"])


@pytest.mark.unit
async def test_reality_settings_invalid_anchors() -> None:
    session = AsyncMock()
    service = RealitySettingsService(session)
    project = _project()
    row = _reality_row(project.id)
    service.repo.ensure_settings = AsyncMock(return_value=row)
    session.refresh = AsyncMock()
    payload = ProjectRealitySettingsUpdate.model_construct(reality_anchors="invalid")
    with pytest.raises(InvalidRealityAnchorsError):
        await service.update_settings(project, payload)


@pytest.mark.unit
async def test_fact_check_enqueue_off_skips() -> None:
    session = AsyncMock()
    service = FactCheckService(session)
    project = _project()
    chapter_id = uuid.uuid4()
    prose = ProseVersion(
        project_id=project.id,
        chapter_id=chapter_id,
        version=1,
        content="text",
        word_count=1,
        created_by=uuid.uuid4(),
    )
    prose.id = uuid.uuid4()
    service.prose.get_latest = AsyncMock(return_value=prose)
    service.fact_check.pending_run_for_prose = AsyncMock(return_value=None)
    reality = _reality_row(project.id)
    reality.reality_anchors = "off"
    service.reality.ensure_settings = AsyncMock(return_value=reality)
    run = FactCheckRun(
        project_id=project.id,
        chapter_id=chapter_id,
        prose_version_id=prose.id,
        requested_by_user_id=uuid.uuid4(),
        status=FactCheckRunStatus.pending.value,
    )
    run.id = uuid.uuid4()
    run.created_at = datetime.now(UTC)
    service.fact_check.create_run = AsyncMock(return_value=run)
    session.refresh = AsyncMock()

    detail = await service.enqueue_run(project, chapter_id, uuid.uuid4(), None)
    assert detail.status == FactCheckRunStatus.done
    assert detail.skipped_reason == "reality_off"


@pytest.mark.unit
async def test_fact_check_duplicate_pending() -> None:
    session = AsyncMock()
    service = FactCheckService(session)
    project = _project()
    chapter_id = uuid.uuid4()
    prose = ProseVersion(
        project_id=project.id,
        chapter_id=chapter_id,
        version=1,
        content="text",
        word_count=1,
        created_by=uuid.uuid4(),
    )
    prose.id = uuid.uuid4()
    service.prose.get_latest = AsyncMock(return_value=prose)
    service.fact_check.pending_run_for_prose = AsyncMock(return_value=MagicMock())
    with pytest.raises(FactCheckRunPendingError):
        await service.enqueue_run(project, chapter_id, uuid.uuid4(), None)


@pytest.mark.unit
async def test_fact_check_accept_fix_no_correction() -> None:
    session = AsyncMock()
    service = FactCheckService(session)
    project = _project()
    claim = FactClaim(
        project_id=project.id,
        run_id=uuid.uuid4(),
        category="date",
        text="x",
        source_type="prose",
        severity="fail",
        author_disposition="open",
    )
    claim.id = uuid.uuid4()
    claim.proposed_correction = None
    service.fact_check.get_claim = AsyncMock(return_value=claim)
    with pytest.raises(ClaimNoProposedCorrectionError):
        await service.accept_fix(project, uuid.uuid4(), claim.id, FactClaimAcceptFixRequest())


@pytest.mark.unit
async def test_fact_check_promote_no_citations() -> None:
    session = AsyncMock()
    service = FactCheckService(session)
    project = _project()
    claim = FactClaim(
        project_id=project.id,
        run_id=uuid.uuid4(),
        category="date",
        text="x",
        source_type="prose",
        severity="fail",
        author_disposition="open",
    )
    claim.id = uuid.uuid4()
    service.fact_check.get_claim = AsyncMock(return_value=claim)
    service.fact_check.list_citations_for_claims = AsyncMock(return_value=[])
    with pytest.raises(ClaimNoCitationsError):
        await service.promote_evidence(project, uuid.uuid4(), claim.id, None)


@pytest.mark.unit
async def test_fact_check_promote_already_promoted() -> None:
    session = AsyncMock()
    service = FactCheckService(session)
    project = _project()
    note_id = uuid.uuid4()
    claim = FactClaim(
        project_id=project.id,
        run_id=uuid.uuid4(),
        category="date",
        text="x",
        source_type="prose",
        severity="fail",
        author_disposition="open",
        promoted_research_note_id=note_id,
    )
    claim.id = uuid.uuid4()
    note = ResearchNote(
        project_id=project.id,
        title="T",
        body_md="b",
        tags=[],
        status=ResearchNoteStatus.active.value,
    )
    service.fact_check.get_claim = AsyncMock(return_value=claim)
    service.fact_check.list_citations_for_claims = AsyncMock(
        return_value=[
            FactCitation(
                project_id=project.id,
                claim_id=claim.id,
                provider_id="fake",
                url="https://example.com",
                title="T",
                snippet="s",
                retrieved_at=datetime.now(UTC),
            )
        ]
    )
    service.research.get_note = AsyncMock(return_value=note)
    with pytest.raises(ClaimAlreadyPromotedError):
        await service.promote_evidence(project, uuid.uuid4(), claim.id, None)


@pytest.mark.unit
async def test_sync_fact_check_queue() -> None:
    reset_fact_check_queue()
    queue = SyncFactCheckQueue()
    run_id = uuid.uuid4()
    queue.enqueue(run_id, uuid.uuid4(), uuid.uuid4())
    assert queue.pending[0]["run_id"] == str(run_id)


@pytest.mark.unit
async def test_fact_check_get_run_not_found() -> None:
    session = AsyncMock()
    service = FactCheckService(session)
    service.fact_check.get_run = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.get_run(_project(), uuid.uuid4())
