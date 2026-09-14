"""Full fact-check processor path with mocks."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.enums import FactCheckRunStatus, RealityAnchorsMode
from app.models.fact_check import FactCheckRun
from app.models.project_reality_settings import ProjectRealitySettings
from app.models.prose_version import ProseVersion
from app.models.research import ResearchNote
from app.services.fact_check_processor import process_fact_check_run


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_fact_check_run_success_with_claims() -> None:
    session = AsyncMock()
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    prose_id = uuid.uuid4()
    run = FactCheckRun(
        project_id=project_id,
        chapter_id=chapter_id,
        prose_version_id=prose_id,
        requested_by_user_id=uuid.uuid4(),
        status=FactCheckRunStatus.pending.value,
        options_json={"force_refresh": False, "categories": None},
    )
    run.id = run_id
    prose = ProseVersion(
        project_id=project_id,
        chapter_id=chapter_id,
        version=1,
        content="The wall fell on 9 November 1985.",
        word_count=8,
        created_by=uuid.uuid4(),
    )
    prose.id = prose_id
    reality = ProjectRealitySettings(project_id=project_id)
    reality.reality_anchors = RealityAnchorsMode.strict.value
    reality.enabled_categories = []
    reality.include_research_notes = True

    def get_side_effect(model, pk):
        if pk == run_id:
            return run
        if pk == prose_id:
            return prose
        return None

    session.get = AsyncMock(side_effect=get_side_effect)

    note = ResearchNote(
        project_id=project_id,
        title="Ref",
        body_md="1985 reference",
        tags=["fact-check"],
        status="active",
    )
    note.id = uuid.uuid4()
    note.updated_at = datetime.now(UTC)

    fc_repo = MagicMock()
    fc_repo.update_run = AsyncMock()
    fc_repo.create_claim = AsyncMock(side_effect=lambda c: c)
    fc_repo.create_citation = AsyncMock()

    research_repo = MagicMock()
    research_repo.list_notes = AsyncMock(return_value=([note], 1))
    research_repo.list_all_links_for_project = AsyncMock(return_value=[])

    with patch("app.services.fact_check_processor.RealitySettingsRepository") as rr:
        rr.return_value.ensure_settings = AsyncMock(return_value=reality)
        with patch("app.services.fact_check_processor.FactCheckRepository", return_value=fc_repo):
            with patch(
                "app.services.fact_check_processor.ResearchRepository", return_value=research_repo
            ):
                with patch("app.services.fact_check_processor.get_settings") as gs:
                    gs.return_value = MagicMock(
                        fact_check_http=False,
                        fact_check_cache=True,
                    )
                    await process_fact_check_run(session, run_id)

    assert run.status == FactCheckRunStatus.done.value
    assert run.summary_json is not None
    assert run.summary_json["total_claims"] >= 1
    fc_repo.create_claim.assert_called()
    fc_repo.create_citation.assert_called()
