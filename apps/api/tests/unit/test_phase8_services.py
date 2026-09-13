"""Unit tests for Phase 8 services."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import (
    InvalidActNumberError,
    InvalidRelationshipPairError,
    InvalidStakesLevelError,
    NotFoundError,
    RelationshipExistsError,
    SceneMissingOutcomeError,
)
from app.models.chapter import Chapter
from app.models.enums import ChapterStatus, RelationType, StakesEntryStatus
from app.models.project import Project
from app.models.relationship import Relationship
from app.models.scene_beat import SceneBeat
from app.models.stakes_ledger_entry import StakesLedgerEntry
from app.schemas.relationship import RelationshipCreateRequest, RelationshipUpdateRequest
from app.schemas.scene_engine import SceneEngineSettingsUpdateRequest
from app.schemas.stakes import StakesEntryCreateRequest, StakesEntryUpdateRequest
from app.services.relationship import RelationshipService
from app.services.relationship_context_pack import RelationshipContextPackService
from app.services.scene_context_pack import SceneContextPackService
from app.services.scene_engine import SceneEngineService
from app.services.stakes import StakesService
from app.services.stakes_context_pack import StakesContextPackService


def _project() -> Project:
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = uuid.uuid4()
    return project


def _chapter(project_id: uuid.UUID) -> Chapter:
    chapter = Chapter(project_id=project_id, number=1, title="Ch1", status=ChapterStatus.drafting)
    chapter.id = uuid.uuid4()
    return chapter


@pytest.mark.unit
async def test_scene_engine_settings_and_lint() -> None:
    session = AsyncMock()
    service = SceneEngineService(session)
    project = _project()
    chapter = _chapter(project.id)
    settings = MagicMock(
        project_id=project.id,
        enabled=True,
        require_conflict=True,
        require_outcome_on_complete=True,
        min_goal_length=8,
        llm_auditor_enabled=False,
        strictness="standard",
        updated_at=datetime.now(UTC),
    )
    beat = SceneBeat(
        project_id=project.id,
        chapter_id=chapter.id,
        beat_key="1.1",
        summary="s",
        sort_order=0,
        completed=True,
        goal="long goal text",
        conflict="",
        outcome="done",
    )
    beat.id = uuid.uuid4()
    service.settings_repo.ensure_settings = AsyncMock(return_value=settings)
    service.beats.list_for_chapter = AsyncMock(return_value=[beat])
    service.characters.list_all_for_project = AsyncMock(return_value=[])
    service.stakes.list_entries_for_act = AsyncMock(return_value=[])
    project.genre_profile = None
    project.genre_rule_pack_json = {}

    got = await service.get_settings(project)
    assert got.enabled is True
    updated = await service.update_settings(
        project, SceneEngineSettingsUpdateRequest(strictness="relaxed")
    )
    assert updated.strictness == "relaxed"
    lint = await service.run_scene_lint(project, chapter)
    assert lint.chapter_id == chapter.id
    with pytest.raises(InvalidStakesLevelError):
        service._validate_stakes_level(9)
    with pytest.raises(SceneMissingOutcomeError):
        service.validate_beat_fields(completed=True, outcome="", settings_row=settings)


@pytest.mark.unit
async def test_relationship_service_crud_and_graph() -> None:
    session = AsyncMock()
    service = RelationshipService(session)
    project = _project()
    char_a = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    char_b = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
    rel = Relationship(
        project_id=project.id,
        character_a_id=char_a,
        character_b_id=char_b,
        relation_type="rival",
        baseline_intensity=0,
    )
    rel.id = uuid.uuid4()
    rel.created_at = datetime.now(UTC)
    rel.updated_at = datetime.now(UTC)
    rel.notes_md = ""

    char_a_obj = MagicMock(id=char_a, display_name="A", tier=2)
    char_b_obj = MagicMock(id=char_b, display_name="B", tier=2)
    service.characters.get_by_id = AsyncMock(
        side_effect=lambda _pid, cid: char_a_obj if cid == char_a else char_b_obj
    )
    service.relationships.list_for_project = AsyncMock(return_value=([rel], 1))
    service.relationships.get_by_pair = AsyncMock(return_value=None)
    service.relationships.create = AsyncMock(return_value=rel)
    service.relationships.get = AsyncMock(return_value=rel)
    service.relationships.update = AsyncMock(return_value=rel)
    service.relationships.delete = AsyncMock()
    service.relationships.list_events = AsyncMock(return_value=[])
    service.relationships.list_all_for_project = AsyncMock(return_value=[rel])
    service.relationships.list_settled_events_for_project = AsyncMock(return_value=[])
    service.stakes = MagicMock()
    service.stakes.ensure_settings = AsyncMock(
        return_value=MagicMock(act_count=3, chapters_per_act=[])
    )
    session.refresh = AsyncMock()

    created = await service.create_relationship(
        project,
        RelationshipCreateRequest(
            character_a_id=char_b,
            character_b_id=char_a,
            relation_type=RelationType.rival,
        ),
    )
    assert created.relation_type == RelationType.rival
    listed = await service.list_relationships(project)
    assert listed.total == 1
    graph = await service.get_graph(project)
    assert len(graph.edges) == 1
    await service.list_events(project, rel.id)
    await service.update_relationship(project, rel.id, RelationshipUpdateRequest(notes_md="notes"))
    await service.delete_relationship(project, rel.id)
    service.relationships.get_by_pair = AsyncMock(return_value=rel)
    with pytest.raises(RelationshipExistsError):
        await service.create_relationship(
            project,
            RelationshipCreateRequest(
                character_a_id=char_a,
                character_b_id=char_b,
                relation_type=RelationType.rival,
            ),
        )
    with pytest.raises(InvalidRelationshipPairError):
        await service.create_relationship(
            project,
            RelationshipCreateRequest(
                character_a_id=char_a,
                character_b_id=char_a,
                relation_type=RelationType.rival,
            ),
        )
    service.relationships.get = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.get_relationship(project, uuid.uuid4())


@pytest.mark.unit
async def test_stakes_service_crud_and_board() -> None:
    session = AsyncMock()
    service = StakesService(session)
    project = _project()
    settings = MagicMock(
        project_id=project.id,
        act_count=3,
        chapters_per_act=[],
        enabled=True,
        flat_middle_window_chapters=3,
        updated_at=datetime.now(UTC),
    )
    entry = StakesLedgerEntry(
        project_id=project.id,
        act_number=1,
        checkpoint_key="act1_mid",
        title="Mid",
        target_level=3,
        status="planned",
    )
    entry.id = uuid.uuid4()
    entry.created_at = datetime.now(UTC)
    entry.updated_at = datetime.now(UTC)
    entry.description_md = ""
    entry.sort_order = 0
    service.stakes.ensure_settings = AsyncMock(return_value=settings)
    service.stakes.list_entries = AsyncMock(return_value=[entry])
    service.stakes.get_by_checkpoint = AsyncMock(return_value=None)
    service.stakes.create_entry = AsyncMock(return_value=entry)
    service.stakes.get_entry = AsyncMock(return_value=entry)
    service.stakes.update_entry = AsyncMock(return_value=entry)
    service.stakes.delete_entry = AsyncMock()
    service.chapters.get = AsyncMock(return_value=_chapter(project.id))
    session.refresh = AsyncMock()

    got = await service.get_settings(project)
    assert got.act_count == 3
    from app.schemas.stakes import ActStructureSettingsUpdateRequest

    await service.update_settings(project, ActStructureSettingsUpdateRequest(act_count=2))
    created = await service.create_entry(
        project,
        StakesEntryCreateRequest(
            act_number=1,
            checkpoint_key="act1_mid",
            title="Mid",
            target_level=3,
        ),
    )
    assert created.checkpoint_key == "act1_mid"
    board = await service.get_board(project)
    assert len(board.acts) == 2
    await service.update_entry(
        project,
        entry.id,
        StakesEntryUpdateRequest(status=StakesEntryStatus.planted),
    )
    await service.delete_entry(project, entry.id)
    with pytest.raises(InvalidActNumberError):
        await service.create_entry(
            project,
            StakesEntryCreateRequest(
                act_number=9,
                checkpoint_key="x",
                title="x",
                target_level=1,
            ),
        )


@pytest.mark.unit
async def test_context_pack_services() -> None:
    project = _project()
    chapter = _chapter(project.id)

    scene_session = AsyncMock()
    scene_service = SceneContextPackService(scene_session)
    beat = SceneBeat(
        project_id=project.id,
        chapter_id=chapter.id,
        beat_key="1.1",
        summary="s",
        sort_order=0,
        goal="goal",
        conflict="c",
        outcome="o",
    )
    scene_service.chapters.get = AsyncMock(return_value=chapter)
    scene_service.beats.list_for_chapter = AsyncMock(return_value=[beat])
    scene_pack = await scene_service.build_context_pack(
        project, MagicMock(chapter_id=chapter.id, beat_ids=[], include_empty=False)
    )
    assert len(scene_pack.beats) == 1

    rel_session = AsyncMock()
    rel_service = RelationshipContextPackService(rel_session)
    rel_service.chapters.get = AsyncMock(return_value=chapter)
    rel_service.beats.list_for_chapter = AsyncMock(return_value=[])
    rel_service.relationships.list_all_for_project = AsyncMock(return_value=[])
    rel_service.relationships.list_settled_events_for_project = AsyncMock(return_value=[])
    rel_pack = await rel_service.build_context_pack(
        project, MagicMock(chapter_id=chapter.id, character_ids=[])
    )
    assert rel_pack.edges == []

    stakes_session = AsyncMock()
    stakes_service = StakesContextPackService(stakes_session)
    stakes_service.chapters.get = AsyncMock(return_value=chapter)
    settings = MagicMock(act_count=3, chapters_per_act=[])
    stakes_service.stakes.ensure_settings = AsyncMock(return_value=settings)
    stakes_service.stakes.list_entries_for_act = AsyncMock(return_value=[])
    stakes_pack = await stakes_service.build_context_pack(project, MagicMock(chapter_id=chapter.id))
    assert stakes_pack.act_number >= 1


@pytest.mark.unit
async def test_relationship_context_pack_filters_and_secrets() -> None:
    project = _project()
    chapter = _chapter(project.id)
    char_a = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    char_b = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")

    session = AsyncMock()
    service = RelationshipContextPackService(session)
    service.chapters.get = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.build_context_pack(
            project, MagicMock(chapter_id=chapter.id, character_ids=[char_a])
        )

    rel = Relationship(
        project_id=project.id,
        character_a_id=char_a,
        character_b_id=char_b,
        relation_type="rival",
        baseline_intensity=1,
    )
    rel.id = uuid.uuid4()
    secret_event = MagicMock(
        relationship_id=rel.id,
        event_type="betrayal",
        intensity_delta=2,
        chapter_number=1,
        payload={"visibility": "secret", "knows": [str(char_b)]},
    )
    visible_event = MagicMock(
        relationship_id=rel.id,
        event_type="alliance",
        intensity_delta=1,
        chapter_number=2,
        payload={"visibility": "public"},
    )
    pov_beat = SceneBeat(
        project_id=project.id,
        chapter_id=chapter.id,
        beat_key="1.1",
        summary="s",
        sort_order=0,
        pov_character_id=char_a,
    )
    service.chapters.get = AsyncMock(return_value=chapter)
    service.beats.list_for_chapter = AsyncMock(return_value=[pov_beat])
    service.relationships.list_all_for_project = AsyncMock(return_value=[rel])
    service.relationships.list_settled_events_for_project = AsyncMock(
        return_value=[visible_event, secret_event]
    )

    pack = await service.build_context_pack(
        project, MagicMock(chapter_id=chapter.id, character_ids=[char_a])
    )
    assert len(pack.edges) == 1
    assert pack.edges[0].recent_events[0]["event_type"] == "alliance"


@pytest.mark.unit
async def test_stakes_service_not_found_and_board_boundaries() -> None:
    session = AsyncMock()
    service = StakesService(session)
    project = _project()
    settings = MagicMock(
        project_id=project.id,
        act_count=2,
        chapters_per_act=[
            {"act_number": 1, "label": "Act I", "start_chapter": 1, "end_chapter": 5},
            {"act_number": 2, "label": "Act II", "start_chapter": 6, "end_chapter": 10},
        ],
        enabled=True,
        flat_middle_window_chapters=3,
        updated_at=datetime.now(UTC),
    )
    planted = StakesLedgerEntry(
        project_id=project.id,
        act_number=1,
        checkpoint_key="open",
        title="Open",
        target_level=2,
        status="planted",
    )
    planted.id = uuid.uuid4()
    planted.created_at = datetime.now(UTC)
    planted.updated_at = datetime.now(UTC)
    planted.description_md = ""
    planted.sort_order = 0
    planted.resolve_chapter_id = None

    service.stakes.ensure_settings = AsyncMock(return_value=settings)
    service.stakes.get_entry = AsyncMock(return_value=None)
    missing_id = uuid.uuid4()
    with pytest.raises(NotFoundError):
        await service.get_entry(project, missing_id)
    with pytest.raises(NotFoundError):
        await service.delete_entry(project, missing_id)

    service.stakes.list_entries = AsyncMock(return_value=[planted])
    board = await service.get_board(project)
    assert board.acts[0].label == "Act I"
    assert board.acts[0].start_chapter == 1
    assert board.warnings.open_fail_count == 1
