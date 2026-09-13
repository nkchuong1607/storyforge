"""Phase 2 service unit tests with mocked repositories."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import (
    BeatKeyConflictError,
    ChapterLockedError,
    ContinuityCheckRequiredError,
    ContinuityFailBlocksSettleError,
    InvalidChapterStatusTransitionError,
    NotFoundError,
    ValidationAppError,
)
from app.models.chapter import Chapter
from app.models.continuity import ContinuityReport
from app.models.enums import ChapterStatus, ContinuityResult, ContinuitySeverity, ProseSource
from app.models.project import Project
from app.models.prose_version import ProseVersion
from app.models.scene_beat import SceneBeat
from app.schemas.beat import SceneBeatCreateRequest, SceneBeatUpdateRequest
from app.schemas.chapter import ChapterUpdateRequest
from app.schemas.continuity import ContinuityCheckRequest, ContinuityOverrideCreateRequest
from app.schemas.prose import ProseVersionCreateRequest
from app.services.beat import BeatService
from app.services.chapter import ChapterService
from app.services.continuity_service import ContinuityService
from app.services.prose import ProseService
from app.services.settle import SettleService
from app.utils.pagination import PageParams


def _chapter(**kwargs) -> Chapter:
    chapter = Chapter(
        project_id=kwargs.get("project_id", uuid.uuid4()),
        number=1,
        title="Ch 1",
        status=kwargs.get("status", ChapterStatus.drafting),
    )
    chapter.id = kwargs.get("id", uuid.uuid4())
    chapter.word_count = kwargs.get("word_count", 0)
    chapter.bible_version_at_draft = kwargs.get("bible_version_at_draft")
    chapter.current_prose_version = kwargs.get("current_prose_version")
    chapter.created_at = datetime.now(tz=UTC)
    chapter.updated_at = datetime.now(tz=UTC)
    return chapter


def _project(**kwargs) -> Project:
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = kwargs.get("id", uuid.uuid4())
    project.bible_version_current = kwargs.get("bible_version_current", 0)
    return project


@pytest.mark.unit
async def test_beat_service_locked_raises() -> None:
    service = BeatService(AsyncMock())
    with pytest.raises(ChapterLockedError):
        service._ensure_editable(_chapter(status=ChapterStatus.locked))


@pytest.mark.unit
async def test_beat_service_create_conflict() -> None:
    session = AsyncMock()
    service = BeatService(session)
    service.beats.beat_key_exists = AsyncMock(return_value=True)
    with pytest.raises(BeatKeyConflictError):
        await service.create_beat(
            _chapter(),
            SceneBeatCreateRequest(beat_key="1.1", summary="s", sort_order=1),
        )


@pytest.mark.unit
async def test_beat_service_update_not_found() -> None:
    session = AsyncMock()
    service = BeatService(session)
    service.beats.get = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.update_beat(_chapter(), uuid.uuid4(), SceneBeatUpdateRequest(summary="x"))


@pytest.mark.unit
async def test_beat_service_crud_success() -> None:
    session = AsyncMock()
    service = BeatService(session)
    chapter = _chapter()
    beat = SceneBeat(
        project_id=chapter.project_id,
        chapter_id=chapter.id,
        beat_key="1.1",
        summary="s",
        sort_order=1,
    )
    beat.id = uuid.uuid4()
    beat.completed = False
    beat.created_at = datetime.now(tz=UTC)
    beat.updated_at = datetime.now(tz=UTC)
    service.beats.beat_key_exists = AsyncMock(return_value=False)
    service.beats.create = AsyncMock(return_value=beat)
    service.beats.get = AsyncMock(return_value=beat)
    service.beats.update = AsyncMock(return_value=beat)
    service.beats.delete = AsyncMock()
    service.beats.list_for_chapter = AsyncMock(return_value=[beat])
    session.refresh = AsyncMock()
    settings = MagicMock(require_outcome_on_complete=True)
    service.scene_engine.settings_repo.ensure_settings = AsyncMock(return_value=settings)

    created = await service.create_beat(
        chapter, SceneBeatCreateRequest(beat_key="1.1", summary="s", sort_order=1)
    )
    assert created.beat_key == "1.1"
    listed = await service.list_beats(chapter)
    assert len(listed) == 1
    updated = await service.update_beat(
        chapter,
        beat.id,
        SceneBeatUpdateRequest(completed=True, outcome="Resolved outcome"),
    )
    assert updated.beat_key == "1.1"
    await service.delete_beat(chapter, beat.id)


@pytest.mark.unit
async def test_chapter_service_get_update() -> None:
    session = AsyncMock()
    service = ChapterService(session)
    chapter = _chapter()
    service.chapters.get = AsyncMock(return_value=chapter)
    service.chapters.update = AsyncMock(return_value=chapter)
    session.refresh = AsyncMock()
    project = _project(id=chapter.project_id)

    result = await service.get_chapter(project, chapter.id)
    assert result.title == "Ch 1"

    updated = await service.update_chapter(
        project, chapter.id, ChapterUpdateRequest(title="New Title")
    )
    assert updated.title == "New Title"

    chapter.status = ChapterStatus.locked
    with pytest.raises(ChapterLockedError):
        await service.update_chapter(project, chapter.id, ChapterUpdateRequest(title="X"))


@pytest.mark.unit
async def test_chapter_service_invalid_transition() -> None:
    session = AsyncMock()
    service = ChapterService(session)
    chapter = _chapter(status=ChapterStatus.planned)
    service.chapters.get = AsyncMock(return_value=chapter)
    project = _project(id=chapter.project_id)
    with pytest.raises(InvalidChapterStatusTransitionError):
        await service.update_chapter(
            project, chapter.id, ChapterUpdateRequest(status=ChapterStatus.locked)
        )


@pytest.mark.unit
async def test_prose_service_create_and_compare() -> None:
    session = AsyncMock()
    service = ProseService(session)
    chapter = _chapter(status=ChapterStatus.planned)
    project = _project(id=chapter.project_id)
    prose = ProseVersion(
        project_id=project.id,
        chapter_id=chapter.id,
        version=1,
        content="hello world",
        word_count=2,
        created_by=uuid.uuid4(),
    )
    prose.source = ProseSource.human
    prose.created_at = datetime.now(tz=UTC)
    service.prose.get_max_version = AsyncMock(return_value=0)
    service.prose.create = AsyncMock(return_value=prose)
    service.prose.get_version = AsyncMock(return_value=prose)
    session.refresh = AsyncMock()
    session.flush = AsyncMock()

    detail = await service.create_version(
        project, chapter, uuid.uuid4(), ProseVersionCreateRequest(content="hello world")
    )
    assert detail.version == 1
    assert chapter.status == ChapterStatus.drafting

    compare = await service.compare_versions(chapter, 1, 1)
    assert compare.word_count_delta == 0


@pytest.mark.unit
async def test_prose_service_locked() -> None:
    service = ProseService(AsyncMock())
    with pytest.raises(ChapterLockedError):
        service._ensure_editable(_chapter(status=ChapterStatus.locked))


@pytest.mark.unit
async def test_continuity_service_run_check() -> None:
    session = AsyncMock()
    service = ContinuityService(session)
    chapter = _chapter()
    project = _project(id=chapter.project_id)
    prose = ProseVersion(
        project_id=project.id,
        chapter_id=chapter.id,
        version=1,
        content="Lý Phong tu luyện.",
        word_count=3,
        created_by=uuid.uuid4(),
    )
    prose.created_at = datetime.now(tz=UTC)
    report = ContinuityReport(
        project_id=project.id,
        chapter_id=chapter.id,
        prose_version=1,
        result=ContinuityResult.PASS,
        issues_json=[],
        state_diff_json={"ledger_proposals": [], "bible_patch_candidates": []},
        stats_json={"passed": 1, "warnings": 0, "errors": 0},
        created_by=uuid.uuid4(),
    )
    report.id = uuid.uuid4()
    report.created_at = datetime.now(tz=UTC)

    service.prose.get_latest = AsyncMock(return_value=prose)
    service.bible.get_version = AsyncMock(return_value=MagicMock(snapshot_json={"entries": []}))
    service.characters.list_all_for_project = AsyncMock(return_value=[])
    service.bible.list_all_staging = AsyncMock(return_value=[])
    service.beats.list_for_chapter = AsyncMock(return_value=[])
    service.continuity.active_override_fingerprints = AsyncMock(return_value=set())
    service.ledger.list_settled_for_project = AsyncMock(return_value=[])
    service.continuity.create_report = AsyncMock(return_value=report)
    service.twists.list_payoffs_with_twists_for_chapter = AsyncMock(return_value=[])
    service.twists.list_plants_for_project = AsyncMock(return_value=[])
    service.twists.list_all_plans = AsyncMock(return_value=[])
    service.psych_states.list_latest_for_characters_before_chapter = AsyncMock(return_value={})
    power_settings = MagicMock(enabled=False)
    service.power.ensure_settings = AsyncMock(return_value=power_settings)
    service.power.list_ranks = AsyncMock(return_value=[])
    service.power.list_techniques = AsyncMock(return_value=[])
    scene_settings = MagicMock(enabled=True, strictness="standard")
    service.scene_engine.ensure_settings = AsyncMock(return_value=scene_settings)
    stakes_settings = MagicMock(
        enabled=True,
        act_count=3,
        chapters_per_act=[],
        flat_middle_window_chapters=3,
    )
    service.stakes.ensure_settings = AsyncMock(return_value=stakes_settings)
    service.stakes.list_entries = AsyncMock(return_value=[])
    service.relationships.list_all_for_project = AsyncMock(return_value=[])
    service.relationships.list_settled_events_for_project = AsyncMock(return_value=[])
    project.genre_profile = None
    project.genre_rule_pack_json = {}
    session.refresh = AsyncMock()
    session.flush = AsyncMock()

    result = await service.run_check(project, chapter, uuid.uuid4(), ContinuityCheckRequest())
    assert result.prose_version == 1


@pytest.mark.unit
async def test_continuity_service_override_validation() -> None:
    session = AsyncMock()
    service = ContinuityService(session)
    chapter = _chapter()
    project = _project(id=chapter.project_id)
    report = ContinuityReport(
        project_id=project.id,
        chapter_id=chapter.id,
        prose_version=1,
        result=ContinuityResult.FAIL,
        issues_json=[
            {
                "fingerprint": "fp1",
                "severity": "fail",
                "category": "character",
                "code": "x",
                "message": "m",
            }
        ],
        state_diff_json={},
        stats_json={},
        created_by=uuid.uuid4(),
    )
    report.id = uuid.uuid4()
    service.continuity.get_latest_report = AsyncMock(return_value=report)
    with pytest.raises(ValidationAppError):
        await service.create_override(
            project,
            chapter,
            uuid.uuid4(),
            ContinuityOverrideCreateRequest(issue_fingerprint="missing", reason="r"),
        )


@pytest.mark.unit
async def test_continuity_service_create_override_success() -> None:
    session = AsyncMock()
    service = ContinuityService(session)
    chapter = _chapter()
    project = _project(id=chapter.project_id)
    report = ContinuityReport(
        project_id=project.id,
        chapter_id=chapter.id,
        prose_version=1,
        result=ContinuityResult.FAIL,
        issues_json=[
            {
                "fingerprint": "fp1",
                "severity": "fail",
                "category": "character",
                "code": "x",
                "message": "m",
            }
        ],
        state_diff_json={},
        stats_json={},
        created_by=uuid.uuid4(),
    )
    report.id = uuid.uuid4()
    override = MagicMock()
    override.id = uuid.uuid4()
    override.issue_fingerprint = "fp1"
    override.severity_at_override = ContinuitySeverity.FAIL
    override.reason = "reason"
    override.created_at = datetime.now(tz=UTC)
    service.continuity.get_latest_report = AsyncMock(return_value=report)
    service.continuity.create_override = AsyncMock(return_value=override)
    session.refresh = AsyncMock()

    result = await service.create_override(
        project,
        chapter,
        uuid.uuid4(),
        ContinuityOverrideCreateRequest(issue_fingerprint="fp1", reason="reason"),
    )
    assert result.issue_fingerprint == "fp1"


@pytest.mark.unit
async def test_continuity_service_get_report_and_latest() -> None:
    session = AsyncMock()
    service = ContinuityService(session)
    chapter = _chapter()
    report = ContinuityReport(
        project_id=chapter.project_id,
        chapter_id=chapter.id,
        prose_version=1,
        result=ContinuityResult.PASS,
        issues_json=[],
        state_diff_json={},
        stats_json={"passed": 1, "warnings": 0, "errors": 0},
        created_by=uuid.uuid4(),
    )
    report.id = uuid.uuid4()
    report.created_at = datetime.now(tz=UTC)
    service.continuity.get_latest_report = AsyncMock(return_value=report)
    service.continuity.get_report = AsyncMock(return_value=report)

    latest = await service.get_latest_report(chapter)
    assert latest.report_id == report.id
    by_id = await service.get_report(chapter, report.id)
    assert by_id.prose_version == 1


@pytest.mark.unit
async def test_continuity_service_get_state_diff_from_report() -> None:
    session = AsyncMock()
    service = ContinuityService(session)
    chapter = _chapter()
    report = ContinuityReport(
        project_id=chapter.project_id,
        chapter_id=chapter.id,
        prose_version=1,
        result=ContinuityResult.PASS,
        issues_json=[],
        state_diff_json={"ledger_proposals": [{"x": 1}], "bible_patch_candidates": []},
        stats_json={},
        created_by=uuid.uuid4(),
    )
    service.continuity.get_latest_report = AsyncMock(return_value=report)
    diff = await service.get_state_diff(chapter)
    assert len(diff.ledger_proposals) == 1


@pytest.mark.unit
async def test_settle_service_fail_blocks() -> None:
    session = AsyncMock()
    service = SettleService(session)
    chapter = _chapter(status=ChapterStatus.reviewing)
    project = _project(id=chapter.project_id)
    report = ContinuityReport(
        project_id=project.id,
        chapter_id=chapter.id,
        prose_version=1,
        result=ContinuityResult.FAIL,
        issues_json=[
            {
                "fingerprint": "fp",
                "severity": "fail",
                "code": "character_deceased_appears_alive",
            }
        ],
        state_diff_json={"ledger_proposals": [], "bible_patch_candidates": []},
        stats_json={},
        created_by=uuid.uuid4(),
    )
    report.id = uuid.uuid4()
    service.continuity.get_idempotency = AsyncMock(return_value=None)
    service.continuity.get_latest_report = AsyncMock(return_value=report)
    service.continuity.active_override_fingerprints = AsyncMock(return_value=set())
    with pytest.raises(ContinuityFailBlocksSettleError):
        await service.settle_chapter(project, chapter, None, None)


@pytest.mark.unit
async def test_settle_service_requires_report() -> None:
    session = AsyncMock()
    service = SettleService(session)
    chapter = _chapter(status=ChapterStatus.reviewing)
    project = _project(id=chapter.project_id)
    service.continuity.get_idempotency = AsyncMock(return_value=None)
    service.continuity.get_latest_report = AsyncMock(return_value=None)
    with pytest.raises(ContinuityCheckRequiredError):
        await service.settle_chapter(project, chapter, None, None)


@pytest.mark.unit
async def test_settle_service_success_path() -> None:
    session = AsyncMock()
    service = SettleService(session)
    chapter = _chapter(status=ChapterStatus.reviewing)
    project = _project(id=chapter.project_id)
    report = ContinuityReport(
        project_id=project.id,
        chapter_id=chapter.id,
        prose_version=1,
        result=ContinuityResult.PASS,
        issues_json=[],
        state_diff_json={
            "ledger_proposals": [
                {
                    "entity_type": "character",
                    "entity_id": str(uuid.uuid4()),
                    "event_type": "status_change",
                    "payload": {"from": "alive", "to": "deceased"},
                }
            ],
            "bible_patch_candidates": [
                {
                    "entry_key": "locations.test",
                    "action": "promote_from_staging",
                    "staging_id": str(uuid.uuid4()),
                }
            ],
        },
        stats_json={},
        created_by=uuid.uuid4(),
    )
    report.id = uuid.uuid4()
    bible_version = MagicMock()
    bible_version.snapshot_json = {"entries": []}
    new_bible = MagicMock()

    service.continuity.get_idempotency = AsyncMock(return_value=None)
    service.continuity.get_latest_report = AsyncMock(return_value=report)
    service.continuity.active_override_fingerprints = AsyncMock(return_value=set())
    service.bible.get_version = AsyncMock(return_value=bible_version)
    service.bible.list_all_staging = AsyncMock(return_value=[])
    service.bible.create_version = AsyncMock(return_value=new_bible)
    service.ledger.create = AsyncMock()
    service.continuity.save_idempotency = AsyncMock()
    service.twists.mark_payoffs_revealed_for_chapter = AsyncMock(return_value=0)
    power_settings = MagicMock(enabled=False)
    service.power.ensure_settings = AsyncMock(return_value=power_settings)
    stakes_settings = MagicMock(enabled=False, act_count=3)
    service.stakes.ensure_settings = AsyncMock(return_value=stakes_settings)
    service.stakes.list_entries = AsyncMock(return_value=[])
    session.flush = AsyncMock()

    from app.services import settle as settle_module

    async def _fake_insert(*_args, **_kwargs):
        return new_bible

    settle_module.insert_bible_version = _fake_insert

    result = await service.settle_chapter(project, chapter, None, uuid.uuid4())
    assert result.status == ChapterStatus.locked
    assert result.bible_version_after == 1


@pytest.mark.unit
async def test_continuity_service_state_diff_fallback() -> None:
    session = AsyncMock()
    service = ContinuityService(session)
    chapter = _chapter()
    prose = ProseVersion(
        project_id=chapter.project_id,
        chapter_id=chapter.id,
        version=1,
        content="Lý Phong tu luyện.",
        word_count=3,
        created_by=uuid.uuid4(),
    )
    service.continuity.get_latest_report = AsyncMock(return_value=None)
    service.prose.get_latest = AsyncMock(return_value=prose)
    service.beats.list_for_chapter = AsyncMock(return_value=[])
    service.characters.list_all_for_project = AsyncMock(return_value=[])
    diff = await service.get_state_diff(chapter)
    assert diff.ledger_proposals == []


@pytest.mark.unit
async def test_prose_service_list_and_not_found() -> None:
    session = AsyncMock()
    service = ProseService(session)
    chapter = _chapter()
    service.prose.list_for_chapter = AsyncMock(return_value=([], 0))
    page = PageParams(page=1, page_size=20)
    result = await service.list_versions(chapter, page)
    assert result.pagination.total_items == 0
    service.prose.get_version = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.get_version(chapter, 99)


@pytest.mark.unit
async def test_settle_merge_and_reconcile() -> None:
    service = SettleService(AsyncMock())
    merged = service._merge_staging_into_snapshot(
        {"entries": [{"entry_key": "a", "content_md": "x"}]},
        [],
    )
    assert len(merged["entries"]) == 1


@pytest.mark.unit
async def test_settle_service_invalid_status() -> None:
    session = AsyncMock()
    service = SettleService(session)
    chapter = _chapter(status=ChapterStatus.drafting)
    project = _project(id=chapter.project_id)
    service.continuity.get_idempotency = AsyncMock(return_value=None)
    with pytest.raises(InvalidChapterStatusTransitionError):
        await service.settle_chapter(project, chapter, None, None)
