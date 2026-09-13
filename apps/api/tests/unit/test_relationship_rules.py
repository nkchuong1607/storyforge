"""Unit tests for relationship continuity rules."""

import uuid
from types import SimpleNamespace

from app.models.enums import ContinuitySeverity
from app.services.continuity.relationship import (
    build_relationship_event_proposals,
    compute_intensity,
    run_relationship_checks,
)


def test_intensity_running_total() -> None:
    events = [
        SimpleNamespace(intensity_delta=-2),
        SimpleNamespace(intensity_delta=1),
    ]
    assert compute_intensity(0, events) == -1


def test_betrayal_without_proposal_fail() -> None:
    char_a = SimpleNamespace(id=uuid.uuid4(), display_name="Lâm Phong", tier=2)
    char_b = SimpleNamespace(id=uuid.uuid4(), display_name="Hàn Vân", tier=2)
    rel = SimpleNamespace(
        id=uuid.uuid4(),
        character_a_id=min(char_a.id, char_b.id),
        character_b_id=max(char_a.id, char_b.id),
        relation_type="rival",
        baseline_intensity=0,
    )
    issues = run_relationship_checks(
        prose="Lâm Phong phản bội Hàn Vân đâm sau lưng",
        chapter_number=12,
        characters=[char_a, char_b],
        relationships=[rel],
        settled_events=[],
        relationship_event_proposals=[],
        beats=[],
    )
    assert any(i.code == "relationship_intensity_jump_without_event" for i in issues)
    assert issues[0].severity == ContinuitySeverity.FAIL.value


def test_build_betrayal_proposal() -> None:
    char_a = SimpleNamespace(id=uuid.uuid4(), display_name="Lâm Phong", tier=2)
    char_b = SimpleNamespace(id=uuid.uuid4(), display_name="Hàn Vân", tier=2)
    rel = SimpleNamespace(
        id=uuid.uuid4(),
        character_a_id=min(char_a.id, char_b.id),
        character_b_id=max(char_a.id, char_b.id),
        relation_type="rival",
        baseline_intensity=0,
    )
    proposals = build_relationship_event_proposals(
        prose="Lâm Phong phản bội Hàn Vân",
        relationships=[rel],
        characters=[char_a, char_b],
        chapter_id=uuid.uuid4(),
    )
    assert len(proposals) == 1
    assert proposals[0]["event_type"] == "betrayal"
