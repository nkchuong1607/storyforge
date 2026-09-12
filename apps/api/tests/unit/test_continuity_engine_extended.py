"""Extended continuity engine unit tests."""

import uuid

import pytest

from app.models.character import Character
from app.services.continuity.engine import (
    build_state_diff_stub,
    check_character_status_regression,
    check_character_unknown_in_cast,
    check_location_teleport_without_transition,
    check_world_rule_rank_violation_stub,
)


@pytest.mark.unit
def test_character_status_regression_warn() -> None:
    issue = check_character_status_regression(
        entity_id=uuid.uuid4(),
        display_name="Test",
        proposal={
            "event_type": "status_change",
            "payload": {"from": "deceased", "to": "alive"},
        },
        chapter_number=1,
    )
    assert issue is not None
    assert issue.code == "character_status_regression"


@pytest.mark.unit
def test_character_unknown_in_cast() -> None:
    char = Character(project_id=uuid.uuid4(), display_name="Known", tier=0)
    issues = check_character_unknown_in_cast(
        prose="Unknown Hero đi qua rừng.",
        characters=[char],
        chapter_number=1,
    )
    assert len(issues) >= 1


@pytest.mark.unit
def test_build_state_diff_death_keyword() -> None:
    char = Character(project_id=uuid.uuid4(), display_name="Lý Phong", tier=0)
    char.id = uuid.uuid4()
    diff = build_state_diff_stub(
        prose="Lý Phong chết trên chiến trường.",
        characters=[char],
        beats=[],
    )
    assert len(diff["ledger_proposals"]) >= 1


@pytest.mark.unit
def test_location_teleport_warn() -> None:
    beats = [
        {"summary": "location: A"},
        {"summary": "location: B"},
    ]
    issues = check_location_teleport_without_transition(prose="", beats=beats, chapter_number=1)
    assert len(issues) == 1


@pytest.mark.unit
def test_world_rule_rank_stub_empty_glossary() -> None:
    issues = check_world_rule_rank_violation_stub(
        prose="Tu luyện",
        snapshot_json={"entries": []},
        chapter_number=1,
    )
    assert issues == []
