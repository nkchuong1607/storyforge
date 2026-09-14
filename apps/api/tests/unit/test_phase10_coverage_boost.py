"""Additional Phase 10 unit tests for coverage gate."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.enums import FactCheckRunStatus, FactClaimDisposition, ResearchNoteStatus
from app.models.fact_check import FactCheckRun, FactCitation, FactClaim
from app.models.project import Project
from app.models.project_reality_settings import ProjectRealitySettings
from app.models.prose_version import ProseVersion
from app.models.research import ResearchNote
from app.repositories.fact_check import FactCheckRepository
from app.repositories.reality_settings import RealitySettingsRepository
from app.schemas.fact_check import (
    FactCheckRunCreateRequest,
    FactClaimAcceptFixRequest,
    FactClaimDispositionRequest,
    FactClaimPromoteEvidenceRequest,
)
from app.services.fact_check.queue import (
    RedisFactCheckQueue,
    get_fact_check_queue,
    reset_fact_check_queue,
)
from app.services.fact_check_service import FactCheckService
from app.utils.pagination import PageParams
from app.workers.fact_check_worker import FactCheckWorker, process_sync_fact_check_queue


def _project() -> Project:
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = uuid.uuid4()
    return project


@pytest.mark.unit
async def test_fact_check_repository_methods() -> None:
    session = AsyncMock()
    repo = FactCheckRepository(session)
    run = FactCheckRun(
        project_id=uuid.uuid4(),
        chapter_id=uuid.uuid4(),
        prose_version_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        status="pending",
    )
    run.id = uuid.uuid4()
    session.scalar = AsyncMock(return_value=run)
    found = await repo.get_run(run.project_id, run.id)
    assert found is run

    scalars_result = MagicMock()
    scalars_result.all.return_value = []
    session.scalars = AsyncMock(return_value=scalars_result)
    claims = await repo.list_claims_for_run(run.id)
    assert claims == []


@pytest.mark.unit
async def test_reality_repository_ensure_creates() -> None:
    session = AsyncMock()
    repo = RealitySettingsRepository(session)
    session.get = AsyncMock(return_value=None)
    session.add = MagicMock()
    session.flush = AsyncMock()
    row = await repo.ensure_settings(uuid.uuid4())
    assert row.project_id is not None
    session.add.assert_called_once()


@pytest.mark.unit
async def test_fact_check_service_full_run_detail() -> None:
    session = AsyncMock()
    service = FactCheckService(session)
    project = _project()
    chapter_id = uuid.uuid4()
    run_id = uuid.uuid4()
    claim_id = uuid.uuid4()
    run = FactCheckRun(
        project_id=project.id,
        chapter_id=chapter_id,
        prose_version_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        status=FactCheckRunStatus.done.value,
        summary_json={"total_claims": 1, "pass": 0, "warn": 0, "fail": 1, "skipped": 0},
    )
    run.id = run_id
    run.created_at = datetime.now(UTC)
    claim = FactClaim(
        project_id=project.id,
        run_id=run_id,
        category="date",
        text="9 November 1985",
        normalized_text="1985-11-09",
        span_start=0,
        span_end=16,
        span_excerpt="...",
        source_type="prose",
        severity="fail",
        confidence=Decimal("0.91"),
        summary="Mismatch",
        proposed_correction="9 November 1989",
        author_disposition="open",
    )
    claim.id = claim_id
    claim.created_at = datetime.now(UTC)
    citation = FactCitation(
        project_id=project.id,
        claim_id=claim_id,
        provider_id="fake",
        url="https://fake.storyforge.test/x",
        title="T",
        snippet="s",
        retrieved_at=datetime.now(UTC),
    )
    citation.id = uuid.uuid4()
    service.fact_check.get_run = AsyncMock(return_value=run)
    service.fact_check.list_runs = AsyncMock(return_value=([run], 1))
    service.fact_check.list_claims_for_run = AsyncMock(return_value=[claim])
    service.fact_check.list_citations_for_claims = AsyncMock(return_value=[citation])

    detail = await service.get_run(project, run_id)
    assert detail.claims[0].citations
    listed = await service.list_runs(project, chapter_id, PageParams(page=1, page_size=10))
    assert listed.pagination.total_items == 1


@pytest.mark.unit
async def test_fact_check_disposition_accept_promote() -> None:
    session = AsyncMock()
    service = FactCheckService(session)
    project = _project()
    run_id = uuid.uuid4()
    claim = FactClaim(
        project_id=project.id,
        run_id=run_id,
        category="date",
        text="9 November 1985",
        source_type="prose",
        severity="fail",
        proposed_correction="9 November 1989",
        span_start=0,
        span_end=16,
        author_disposition="open",
    )
    claim.id = uuid.uuid4()
    claim.created_at = datetime.now(UTC)
    run = FactCheckRun(
        project_id=project.id,
        chapter_id=uuid.uuid4(),
        prose_version_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        status="done",
    )
    run.id = run_id
    service.fact_check.get_claim = AsyncMock(return_value=claim)
    service.fact_check.get_run = AsyncMock(return_value=run)
    citation = FactCitation(
        project_id=project.id,
        claim_id=claim.id,
        provider_id="fake",
        url="https://fake.storyforge.test/berlin-wall",
        title="Berlin Wall",
        snippet="Opened: 9 November 1989",
        retrieved_at=datetime.now(UTC),
    )
    citation.id = uuid.uuid4()
    service.fact_check.list_citations_for_claims = AsyncMock(return_value=[citation])
    note = ResearchNote(
        project_id=project.id,
        title="Berlin Wall fall date",
        body_md="body",
        tags=["fact-check"],
        status=ResearchNoteStatus.active.value,
    )
    note.id = uuid.uuid4()
    service.research.create_note = AsyncMock(return_value=note)
    session.refresh = AsyncMock()
    session.flush = AsyncMock()

    updated = await service.set_disposition(
        project,
        uuid.uuid4(),
        claim.id,
        FactClaimDispositionRequest(disposition=FactClaimDisposition.dismissed),
    )
    assert updated.author_disposition == FactClaimDisposition.dismissed

    handoff = await service.accept_fix(
        project,
        uuid.uuid4(),
        claim.id,
        FactClaimAcceptFixRequest(handoff_target="prompt_edit"),
    )
    assert handoff.handoff_payload["suggested_replacement"]

    promoted = await service.promote_evidence(
        project,
        uuid.uuid4(),
        claim.id,
        FactClaimPromoteEvidenceRequest(note_title="Berlin", tags=["berlin"]),
    )
    assert promoted.research_note_id == note.id


@pytest.mark.unit
async def test_fact_check_enqueue_sync_strict() -> None:
    session = AsyncMock()
    service = FactCheckService(session)
    project = _project()
    chapter_id = uuid.uuid4()
    prose = ProseVersion(
        project_id=project.id,
        chapter_id=chapter_id,
        version=1,
        content="On 9 November 1985.",
        word_count=3,
        created_by=uuid.uuid4(),
    )
    prose.id = uuid.uuid4()
    service.prose.get_latest = AsyncMock(return_value=prose)
    service.fact_check.pending_run_for_prose = AsyncMock(return_value=None)
    reality = ProjectRealitySettings(project_id=project.id)
    reality.reality_anchors = "strict"
    reality.enabled_categories = []
    reality.fact_check_blocks_settle = False
    reality.auto_run_on_save = False
    reality.include_research_notes = True
    service.reality.ensure_settings = AsyncMock(return_value=reality)
    run = FactCheckRun(
        project_id=project.id,
        chapter_id=chapter_id,
        prose_version_id=prose.id,
        requested_by_user_id=uuid.uuid4(),
        status=FactCheckRunStatus.done.value,
        summary_json={"total_claims": 1, "pass": 0, "warn": 0, "fail": 1, "skipped": 0},
    )
    run.id = uuid.uuid4()
    run.created_at = datetime.now(UTC)
    service.fact_check.create_run = AsyncMock(return_value=run)
    service.fact_check.get_run = AsyncMock(return_value=run)
    service.fact_check.list_claims_for_run = AsyncMock(return_value=[])
    service.fact_check.list_citations_for_claims = AsyncMock(return_value=[])
    session.refresh = AsyncMock()

    with patch.object(service.settings, "fact_check_sync", True):
        with patch("app.services.fact_check_service.process_fact_check_run", AsyncMock()):
            detail = await service.enqueue_run(
                project,
                chapter_id,
                uuid.uuid4(),
                FactCheckRunCreateRequest(force_refresh=True, categories=["date"]),
            )
    assert detail.status == FactCheckRunStatus.done


@pytest.mark.unit
def test_redis_fact_check_queue_enqueue() -> None:
    with patch("redis.from_url") as from_url:
        client = MagicMock()
        from_url.return_value = client
        queue = RedisFactCheckQueue("redis://localhost:6379/0", "storyforge:fact_check_runs")
        run_id = uuid.uuid4()
        queue.enqueue(run_id, uuid.uuid4(), uuid.uuid4())
        client.lpush.assert_called_once()


@pytest.mark.unit
def test_get_fact_check_queue_sync() -> None:
    reset_fact_check_queue()
    with patch("app.services.fact_check.queue.get_settings") as gs:
        settings = MagicMock()
        settings.fact_check_sync = True
        gs.return_value = settings
        queue = get_fact_check_queue()
        assert hasattr(queue, "pending")


@pytest.mark.unit
async def test_fact_check_worker_process_run() -> None:
    session_factory = MagicMock()
    session = AsyncMock()
    session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
    session_factory.return_value.__aexit__ = AsyncMock(return_value=None)
    run = FactCheckRun(
        project_id=uuid.uuid4(),
        chapter_id=uuid.uuid4(),
        prose_version_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        status="pending",
    )
    run.id = uuid.uuid4()
    session.get = AsyncMock(return_value=run)
    session.commit = AsyncMock()
    worker = FactCheckWorker(session_factory)
    with patch("app.workers.fact_check_worker.process_fact_check_run", AsyncMock()):
        await worker.process_run(run.id)


@pytest.mark.unit
async def test_process_sync_fact_check_queue_helper() -> None:
    reset_fact_check_queue()
    from app.services.fact_check.queue import SyncFactCheckQueue

    queue = SyncFactCheckQueue()
    run_id = uuid.uuid4()
    queue.enqueue(run_id, uuid.uuid4(), uuid.uuid4())
    with patch("app.services.fact_check.queue.get_fact_check_queue", return_value=queue):
        with patch("app.workers.fact_check_worker.FactCheckWorker.process_run", AsyncMock()):
            await process_sync_fact_check_queue(MagicMock())
