"""OOC psychology rule unit tests."""

import uuid

import pytest

from app.models.character import Character
from app.services.continuity.psychology import (
    character_applies_psychology_rules,
    check_ooc_moral_boundary,
    check_value_hierarchy_jump,
    psych_fingerprint,
    run_psychology_checks,
)


def _character(**kwargs) -> Character:
    return Character(
        project_id=uuid.uuid4(),
        display_name=kwargs.get("display_name", "Lý Phong"),
        tier=kwargs.get("tier", 3),
        psyche_card=kwargs.get("psyche_card"),
    )


@pytest.mark.unit
def test_t0_skips_psychology_rules() -> None:
    char = _character(tier=0, psyche_card={"moral_boundaries": ["không giết vô tội"]})
    assert not character_applies_psychology_rules(char)


@pytest.mark.unit
def test_ooc_moral_boundary_fail() -> None:
    char = _character(
        psyche_card={
            "value_hierarchy": ["gia đình"],
            "moral_boundaries": ["không giết vô tội"],
        }
    )
    chapter_id = uuid.uuid4()
    issue = check_ooc_moral_boundary(
        character=char,
        prose="Lý Phong hạ sát dân thường trong làng.",
        chapter_number=7,
        chapter_id=chapter_id,
    )
    assert issue is not None
    assert issue.code == "psych_ooc_moral_boundary_violation"
    assert issue.severity == "fail"
    assert issue.category == "psychology"


@pytest.mark.unit
def test_ooc_allow_moral_break_warn() -> None:
    char = _character(
        psyche_card={
            "moral_boundaries": ["không giết vô tội"],
            "arc_flags": {"allow_moral_break": True},
        }
    )
    issue = check_ooc_moral_boundary(
        character=char,
        prose="Lý Phong hạ sát dân thường.",
        chapter_number=7,
        chapter_id=uuid.uuid4(),
    )
    assert issue is not None
    assert issue.severity == "warn"
    assert issue.code == "psych_moral_boundary_crossed"


@pytest.mark.unit
def test_value_hierarchy_jump_warn() -> None:
    char = _character(
        psyche_card={
            "value_hierarchy": ["gia đình", "công lý"],
            "moral_boundaries": ["no kill"],
        }
    )
    issue = check_value_hierarchy_jump(
        character=char,
        prose="Lý Phong bỏ rơi gia đình để trả thù.",
        chapter_number=5,
        chapter_id=uuid.uuid4(),
    )
    assert issue is not None
    assert issue.code == "psych_value_hierarchy_jump"


@pytest.mark.unit
def test_fingerprint_stable() -> None:
    cid = uuid.uuid4()
    chid = uuid.uuid4()
    fp1 = psych_fingerprint(cid, "ooc_moral", "abc123", chid)
    fp2 = psych_fingerprint(cid, "ooc_moral", "abc123", chid)
    assert fp1 == fp2


@pytest.mark.unit
def test_run_psychology_checks_skips_empty_card() -> None:
    char = _character(tier=2, psyche_card=None)
    issues = run_psychology_checks(
        prose="Lý Phong hạ sát dân thường.",
        chapter_number=1,
        chapter_id=uuid.uuid4(),
        characters=[char],
        prior_states={},
    )
    assert issues == []
