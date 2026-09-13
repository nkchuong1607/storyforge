"""Additional Phase 8 continuity and context pack unit tests."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.models.enums import ContinuitySeverity
from app.services.continuity.relationship import run_relationship_checks
from app.services.continuity.scene import build_scene_structure_summary, run_scene_structure_checks
from app.services.continuity.scene_llm_stub import run_scene_llm_auditor
from app.services.continuity.stakes import (
    build_stakes_ledger_proposals,
    build_stakes_snapshot,
    run_stakes_checks,
)
from app.services.relationship_context_pack import RelationshipContextPackService


@pytest.mark.unit
async def test_scene_stakes_drift_and_summary() -> None:
    beat_id = uuid.uuid4()
    beat = SimpleNamespace(
        id=beat_id,
        beat_key="1.1",
        summary="s",
        sort_order=0,
        completed=True,
        goal="long enough goal",
        conflict="c",
        outcome="o",
        stakes_level=5,
        pov_character_id=None,
        scene_type="scene",
    )
    entry = SimpleNamespace(target_level=2, status="planned")
    issues = run_scene_structure_checks(
        beats=[beat],
        chapter_number=1,
        settings=SimpleNamespace(
            enabled=True,
            require_conflict=True,
            require_outcome_on_complete=True,
            min_goal_length=8,
            strictness="standard",
        ),
        characters=[],
        genre_pack={},
        stakes_entries=[entry],
        relationship_event_proposals=[],
    )
    assert any(i.code == "scene_stakes_level_drift" for i in issues)
    summary = build_scene_structure_summary([beat])
    assert summary["beats_with_outcome"] == 1


@pytest.mark.unit
async def test_relationship_type_contradiction_and_secret_leak() -> None:
    char_a = SimpleNamespace(id=uuid.uuid4(), display_name="A", tier=2)
    char_b = SimpleNamespace(id=uuid.uuid4(), display_name="B", tier=2)
    rel_id = uuid.uuid4()
    rel = SimpleNamespace(
        id=rel_id,
        character_a_id=min(char_a.id, char_b.id),
        character_b_id=max(char_a.id, char_b.id),
        relation_type="enemy",
        baseline_intensity=-2,
    )
    settled = [
        SimpleNamespace(
            relation_type_after="enemy",
            payload={"visibility": "secret", "knows": []},
        )
    ]
    beat = SimpleNamespace(pov_character_id=char_a.id)
    issues = run_relationship_checks(
        prose="A và B là đồng minh ally",
        chapter_number=3,
        characters=[char_a, char_b],
        relationships=[rel],
        settled_events=[SimpleNamespace(relationship_id=rel_id, **settled[0].__dict__)],
        relationship_event_proposals=[],
        beats=[beat],
    )
    codes = {i.code for i in issues}
    assert "relationship_type_contradiction" in codes
    assert "relationship_secret_visibility_leak" in codes


@pytest.mark.unit
async def test_stakes_proposals_and_snapshot() -> None:
    beat = SimpleNamespace(stakes_level=3)
    entry = SimpleNamespace(
        id=uuid.uuid4(),
        act_number=1,
        status="planned",
        target_level=3,
        checkpoint_key="mid",
        title="Mid",
    )
    proposals = build_stakes_ledger_proposals(
        beats=[beat],
        entries=[entry],
        chapter_id=uuid.uuid4(),
        act_number=1,
    )
    assert proposals[0]["status"] == "planted"
    snapshot = build_stakes_snapshot(
        [entry],
        SimpleNamespace(act_count=1, enabled=True),
    )
    assert snapshot["act_count"] == 1


@pytest.mark.unit
async def test_stakes_plant_without_beat_stakes() -> None:
    entry = SimpleNamespace(
        id=uuid.uuid4(),
        act_number=1,
        target_level=4,
        status="planted",
        plant_chapter_id=uuid.uuid4(),
        resolve_chapter_id=None,
        checkpoint_key="mid",
    )
    issues = run_stakes_checks(
        project_id=uuid.uuid4(),
        chapter_number=1,
        settings=SimpleNamespace(
            enabled=True,
            act_count=1,
            chapters_per_act=[{"act_number": 1, "start_chapter": 1, "end_chapter": 5}],
            flat_middle_window_chapters=3,
        ),
        entries=[entry],
        beats=[SimpleNamespace(stakes_level=1)],
        genre_pack={},
        stakes_ledger_proposals=[],
    )
    assert any(i.code == "stakes_plant_without_beat_stakes" for i in issues)


@pytest.mark.unit
async def test_relationship_context_pack_with_secret_filtering() -> None:
    project = SimpleNamespace(id=uuid.uuid4())
    chapter = SimpleNamespace(id=uuid.uuid4(), number=1)
    char_id = uuid.uuid4()
    rel = SimpleNamespace(
        id=uuid.uuid4(),
        character_a_id=char_id,
        character_b_id=uuid.uuid4(),
        relation_type="rival",
        baseline_intensity=0,
    )
    event = SimpleNamespace(
        relationship_id=rel.id,
        event_type="trust_shift",
        intensity_delta=-1,
        chapter_number=1,
        payload={"visibility": "secret", "knows": []},
    )
    service = RelationshipContextPackService(AsyncMock())
    service.chapters.get = AsyncMock(return_value=chapter)
    service.beats.list_for_chapter = AsyncMock(return_value=[])
    service.relationships.list_all_for_project = AsyncMock(return_value=[rel])
    service.relationships.list_settled_events_for_project = AsyncMock(return_value=[event])
    pack = await service.build_context_pack(
        project,
        SimpleNamespace(chapter_id=chapter.id, character_ids=[char_id, rel.character_b_id]),
    )
    assert pack.edges[0].recent_events == []


@pytest.mark.unit
async def test_scene_llm_auditor_fixture() -> None:
    beat = SimpleNamespace(id=uuid.uuid4())
    issues = await run_scene_llm_auditor([beat], uuid.uuid4())
    assert len(issues) >= 1
    assert issues[0].severity == ContinuitySeverity.WARN.value
