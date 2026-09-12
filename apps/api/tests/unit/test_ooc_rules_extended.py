"""Extended OOC psychology rule unit tests."""

import uuid

import pytest

from app.models.character import Character
from app.models.psych_state import PsychState
from app.services.continuity.psychology import (
    build_psych_state_proposals,
    check_arc_beat_skip,
    check_unearned_belief_shift,
    check_voice_taboo_break,
    run_psychology_checks,
)


def _character(**kwargs) -> Character:
    return Character(
        project_id=uuid.uuid4(),
        display_name=kwargs.get("display_name", "Lý Phong"),
        tier=kwargs.get("tier", 3),
        psyche_card=kwargs.get("psyche_card", {}),
    )


def _prior(stress: int = 3) -> PsychState:
    return PsychState(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        character_id=uuid.uuid4(),
        chapter_id=uuid.uuid4(),
        stress_level=stress,
        dominant_emotion="calm",
        active_goal="",
        settled_at=__import__("datetime").datetime.now(__import__("datetime").UTC),
        created_at=__import__("datetime").datetime.now(__import__("datetime").UTC),
    )


@pytest.mark.unit
def test_arc_beat_skip_warn() -> None:
    char = _character(
        psyche_card={
            "moral_boundaries": ["x"],
            "arc_flags": {"expected_arc_beats": ["betrayal_ch7", "redemption_ch15"]},
        }
    )
    issue = check_arc_beat_skip(
        character=char,
        prose="Lý Phong redemption_ch15 on the mountain.",
        chapter_number=1,
        chapter_id=uuid.uuid4(),
    )
    assert issue is not None
    assert issue.code == "psych_arc_beat_skip"


@pytest.mark.unit
def test_unearned_belief_shift_warn() -> None:
    char = _character(
        psyche_card={"drive": "Revenge", "moral_boundaries": ["x"], "value_hierarchy": ["a"]}
    )
    prior = _prior(stress=2)
    prior.character_id = char.id
    proposal = {
        "character_id": str(char.id),
        "belief_updates": [{"from_belief": "Revenge path", "to_belief": "Peace"}],
        "stress_level": 3,
        "trigger_event_refs": [],
    }
    issue = check_unearned_belief_shift(
        character=char,
        chapter_number=5,
        chapter_id=uuid.uuid4(),
        prior_psych=prior,
        psych_state_proposals=[proposal],
    )
    assert issue is not None
    assert issue.code == "psych_unearned_belief_shift"


@pytest.mark.unit
def test_voice_taboo_break_warn() -> None:
    char = _character(
        psyche_card={
            "moral_boundaries": ["x"],
            "voice_taboo": ["xin lỗi"],
        }
    )
    issue = check_voice_taboo_break(
        character=char,
        prose='"xin lỗi" — Lý Phong nói.',
        chapter_number=3,
        chapter_id=uuid.uuid4(),
    )
    assert issue is not None
    assert issue.code == "psych_voice_taboo_break"


@pytest.mark.unit
def test_build_psych_state_proposals() -> None:
    char = _character(
        psyche_card={
            "value_hierarchy": ["gia đình"],
            "moral_boundaries": ["no kill"],
        }
    )
    char.id = uuid.uuid4()
    proposals, patches = build_psych_state_proposals(
        prose="Lý Phong tức giận và phản bội sư phụ.",
        characters=[char],
        beats=[{"id": str(uuid.uuid4()), "summary": "goal: confront master"}],
        chapter_id=uuid.uuid4(),
        prior_states={},
    )
    assert len(proposals) == 1
    assert proposals[0]["stress_level"] >= 3
    assert proposals[0]["trigger_event_refs"]


@pytest.mark.unit
def test_value_jump_escape_with_triggers() -> None:
    char = _character(
        psyche_card={
            "value_hierarchy": ["gia đình", "công lý"],
            "moral_boundaries": ["x"],
        }
    )
    from app.services.continuity.psychology import check_value_hierarchy_jump

    issue = check_value_hierarchy_jump(
        character=char,
        prose="Lý Phong bỏ rơi gia đình.",
        chapter_number=1,
        chapter_id=uuid.uuid4(),
        psych_state_proposals=[
            {
                "character_id": str(char.id),
                "belief_updates": [{"from_belief": "a", "to_belief": "b"}],
                "trigger_event_refs": ["beat:123"],
            }
        ],
    )
    assert issue is None


@pytest.mark.unit
def test_run_psychology_full_pipeline() -> None:
    char = _character(
        psyche_card={
            "value_hierarchy": ["gia đình"],
            "moral_boundaries": ["không giết vô tội"],
            "voice_taboo": ["xin lỗi"],
        }
    )
    issues = run_psychology_checks(
        prose='Lý Phong hạ sát dân thường. "xin lỗi" — Lý Phong.',
        chapter_number=1,
        chapter_id=uuid.uuid4(),
        characters=[char],
        prior_states={},
    )
    codes = {i.code for i in issues}
    assert "psych_ooc_moral_boundary_violation" in codes
    assert "psych_voice_taboo_break" in codes
