"""Phase 10 processor and orchestrator unit tests."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.models.enums import FactCheckRunStatus, RealityAnchorsMode
from app.models.fact_check import FactCheckRun
from app.models.project_reality_settings import ProjectRealitySettings
from app.providers.fact_check.orchestrator import verify_claim
from app.providers.fact_check.research_note import ResearchNoteEvidenceProvider
from app.providers.fact_check.types import ClaimDraft, ProviderContext, ResearchNoteSnapshot
from app.providers.fact_check.wikidata_stub import WikidataStubProvider
from app.providers.fact_check.wikipedia_stub import WikipediaSummaryProvider
from app.services.fact_check_processor import process_fact_check_run


@pytest.mark.unit
@pytest.mark.asyncio
async def test_orchestrator_merges_severity() -> None:
    claim = ClaimDraft(
        category="date",
        text="March 1945",
        normalized_text="1945-03",
        span_start=0,
        span_end=10,
        span_excerpt="March 1945",
        source_type="prose",
    )
    context = ProviderContext(
        project_id=uuid.uuid4(),
        research_notes=[],
        http_enabled=False,
        force_refresh=False,
        cache_enabled=True,
    )
    result = await verify_claim(claim, context, include_research=False)
    assert result.severity in ("pass", "warn", "fail")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_research_note_provider_match() -> None:
    note_id = uuid.uuid4()
    claim = ClaimDraft(
        category="historical_event",
        text="Berlin Wall",
        normalized_text="berlin wall",
        span_start=None,
        span_end=None,
        span_excerpt=None,
        source_type="research_note",
    )
    context = ProviderContext(
        project_id=uuid.uuid4(),
        research_notes=[
            ResearchNoteSnapshot(
                id=note_id,
                title="Berlin Wall",
                body_md="Berlin Wall opened November 1989",
                source_url="https://example.com",
                tags=["fact-check"],
                updated_at=datetime.now(UTC),
            )
        ],
        http_enabled=False,
        force_refresh=False,
        cache_enabled=True,
    )
    result = await ResearchNoteEvidenceProvider().verify(claim, context)
    assert result.severity == "pass"
    assert result.citations


@pytest.mark.unit
@pytest.mark.asyncio
async def test_wikidata_stub_no_fixture() -> None:
    claim = ClaimDraft(
        category="place",
        text="Unknown",
        normalized_text="unknown-place",
        span_start=0,
        span_end=7,
        span_excerpt="Unknown",
        source_type="prose",
    )
    context = ProviderContext(
        project_id=uuid.uuid4(),
        research_notes=[],
        http_enabled=True,
        force_refresh=False,
        cache_enabled=True,
    )
    result = await WikidataStubProvider().verify(claim, context)
    assert result.status == "inconclusive"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_wikipedia_stub_no_fixture() -> None:
    claim = ClaimDraft(
        category="public_figure",
        text="NoFixturePerson",
        normalized_text="nofixtureperson",
        span_start=0,
        span_end=15,
        span_excerpt="NoFixturePerson",
        source_type="prose",
    )
    context = ProviderContext(
        project_id=uuid.uuid4(),
        research_notes=[],
        http_enabled=True,
        force_refresh=False,
        cache_enabled=True,
    )
    result = await WikipediaSummaryProvider().verify(claim, context)
    assert result.severity == "warn"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_fact_check_run_reality_off() -> None:
    session = AsyncMock()
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()
    run = FactCheckRun(
        project_id=project_id,
        chapter_id=uuid.uuid4(),
        prose_version_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        status=FactCheckRunStatus.pending.value,
    )
    run.id = run_id
    session.get = AsyncMock(return_value=run)
    reality = ProjectRealitySettings(project_id=project_id)
    reality.reality_anchors = RealityAnchorsMode.off.value

    with patch("app.services.fact_check_processor.RealitySettingsRepository") as repo_cls:
        repo_cls.return_value.ensure_settings = AsyncMock(return_value=reality)
        with patch("app.services.fact_check_processor.FactCheckRepository") as fc_cls:
            fc_cls.return_value.update_run = AsyncMock()
            await process_fact_check_run(session, run_id)
    assert run.status == FactCheckRunStatus.done.value
    assert run.skipped_reason == "reality_off"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_fact_check_run_missing_prose() -> None:
    session = AsyncMock()
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()
    run = FactCheckRun(
        project_id=project_id,
        chapter_id=uuid.uuid4(),
        prose_version_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        status=FactCheckRunStatus.pending.value,
    )
    run.id = run_id

    def get_side_effect(model, pk):
        if model is FactCheckRun:
            return run
        return None

    session.get = AsyncMock(side_effect=get_side_effect)
    reality = ProjectRealitySettings(project_id=project_id)
    reality.reality_anchors = RealityAnchorsMode.strict.value

    with patch("app.services.fact_check_processor.RealitySettingsRepository") as repo_cls:
        repo_cls.return_value.ensure_settings = AsyncMock(return_value=reality)
        with patch("app.services.fact_check_processor.FactCheckRepository") as fc_cls:
            fc_cls.return_value.update_run = AsyncMock()
            await process_fact_check_run(session, run_id)
    assert run.status == FactCheckRunStatus.failed.value
