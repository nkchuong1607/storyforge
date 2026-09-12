"""Power continuity rules unit tests."""

import uuid

import pytest

from app.models.character import Character
from app.models.enums import ContinuitySeverity
from app.models.power_system import PowerSystemSettings
from app.services.continuity.power import (
    PowerRankContext,
    PowerTechniqueContext,
    build_cultivation_proposals,
    is_power_module_enabled,
    run_power_checks,
)


def _rank(key: str, name: str, order: int) -> PowerRankContext:
    return PowerRankContext(
        id=uuid.uuid4(),
        rank_key=key,
        display_name=name,
        sort_order=order,
    )


def _character(name: str) -> Character:
    char = Character(project_id=uuid.uuid4(), display_name=name, role_one_liner="")
    char.id = uuid.uuid4()
    return char


@pytest.mark.unit
def test_rank_jump_without_breakthrough_fail() -> None:
    ranks = [
        _rank("qi", "Luyện Khí", 0),
        _rank("foundation", "Trúc Cơ", 1),
        _rank("core", "Kim Đan", 2),
    ]
    char = _character("Lâm Phong")
    settings = PowerSystemSettings(
        project_id=uuid.uuid4(),
        enabled=True,
        priority_gap=2,
        max_rank_jump_per_chapter=1,
        require_breakthrough_event=True,
    )
    genre_pack = {"modules": {"power_system": {"enabled": True}}}
    prose = "Lâm Phong đột phá lên Kim Đan trong một đêm."
    issues = run_power_checks(
        prose=prose,
        chapter_number=7,
        characters=[char],
        ranks=ranks,
        techniques=[],
        settings=settings,
        genre_pack=genre_pack,
        ledger_tail=[
            {
                "entity_id": str(char.id),
                "event_type": "cultivation_change",
                "payload": {"to_rank_id": str(ranks[0].id)},
            }
        ],
        ledger_proposals=[],
    )
    codes = [i.code for i in issues]
    assert "power_rank_jump_without_breakthrough" in codes
    assert any(i.severity == ContinuitySeverity.FAIL.value for i in issues)


@pytest.mark.unit
def test_breakthrough_proposal_passes() -> None:
    ranks = [_rank("qi", "Luyện Khí", 0), _rank("foundation", "Trúc Cơ", 1)]
    char = _character("Lâm Phong")
    settings = PowerSystemSettings(
        project_id=uuid.uuid4(),
        enabled=True,
        priority_gap=2,
        max_rank_jump_per_chapter=1,
        require_breakthrough_event=True,
    )
    genre_pack = {"modules": {"power_system": {"enabled": True}}}
    proposals = [
        {
            "entity_id": str(char.id),
            "event_type": "cultivation_change",
            "payload": {
                "from_rank_id": str(ranks[0].id),
                "to_rank_id": str(ranks[1].id),
                "breakthrough": True,
            },
        }
    ]
    issues = run_power_checks(
        prose="Lâm Phong lên Trúc Cơ sau độ kiếp.",
        chapter_number=3,
        characters=[char],
        ranks=ranks,
        techniques=[],
        settings=settings,
        genre_pack=genre_pack,
        ledger_tail=[
            {
                "entity_id": str(char.id),
                "event_type": "cultivation_change",
                "payload": {"to_rank_id": str(ranks[0].id)},
            }
        ],
        ledger_proposals=proposals,
    )
    assert not any(i.code == "power_rank_jump_without_breakthrough" for i in issues)


@pytest.mark.unit
def test_technique_ineligible_fail() -> None:
    ranks = [_rank("qi", "Luyện Khí", 0), _rank("core", "Kim Đan", 2)]
    char = _character("Lâm Phong")
    technique = PowerTechniqueContext(
        id=uuid.uuid4(),
        technique_key="azure_sword",
        display_name="Thanh Vân Kiếm",
        min_rank_id=ranks[1].id,
        min_rank_sort_order=2,
        sect_requirement=None,
    )
    settings = PowerSystemSettings(
        project_id=uuid.uuid4(),
        enabled=True,
        priority_gap=2,
        max_rank_jump_per_chapter=1,
        require_breakthrough_event=True,
    )
    issues = run_power_checks(
        prose="Lâm Phong vung Thanh Vân Kiếm.",
        chapter_number=2,
        characters=[char],
        ranks=ranks,
        techniques=[technique],
        settings=settings,
        genre_pack={"modules": {"power_system": {"enabled": True}}},
        ledger_tail=[
            {
                "entity_id": str(char.id),
                "event_type": "cultivation_change",
                "payload": {"to_rank_id": str(ranks[0].id)},
            }
        ],
        ledger_proposals=[],
    )
    assert any(i.code == "power_technique_ineligible" for i in issues)


@pytest.mark.unit
def test_power_module_disabled_skips() -> None:
    settings = PowerSystemSettings(
        project_id=uuid.uuid4(),
        enabled=True,
        priority_gap=2,
        max_rank_jump_per_chapter=1,
        require_breakthrough_event=True,
    )
    genre_pack = {"modules": {"power_system": {"enabled": False}}}
    assert is_power_module_enabled(settings, genre_pack) is False


@pytest.mark.unit
def test_rank_regression_fail() -> None:
    ranks = [_rank("qi", "Luyện Khí", 0), _rank("foundation", "Trúc Cơ", 1)]
    char = _character("Lâm Phong")
    settings = PowerSystemSettings(
        project_id=uuid.uuid4(),
        enabled=True,
        priority_gap=2,
        max_rank_jump_per_chapter=1,
        require_breakthrough_event=True,
    )
    issues = run_power_checks(
        prose="Lâm Phong tụt về Luyện Khí.",
        chapter_number=4,
        characters=[char],
        ranks=ranks,
        techniques=[],
        settings=settings,
        genre_pack={"modules": {"power_system": {"enabled": True}}},
        ledger_tail=[
            {
                "entity_id": str(char.id),
                "event_type": "cultivation_change",
                "payload": {"to_rank_id": str(ranks[1].id)},
            }
        ],
        ledger_proposals=[],
    )
    assert any(i.code == "power_rank_regression" for i in issues)


@pytest.mark.unit
def test_combat_upset_warn_when_relaxed() -> None:
    ranks = [_rank("qi", "Luyện Khí", 0), _rank("core", "Kim Đan", 2)]
    winner = _character("A")
    loser = _character("B")
    settings = PowerSystemSettings(
        project_id=uuid.uuid4(),
        enabled=True,
        priority_gap=1,
        max_rank_jump_per_chapter=1,
        require_breakthrough_event=True,
    )
    issues = run_power_checks(
        prose="A đánh bại B trong trận chiến.",
        chapter_number=1,
        characters=[winner, loser],
        ranks=ranks,
        techniques=[],
        settings=settings,
        genre_pack={
            "modules": {"power_system": {"enabled": True}},
            "thresholds": {"power_combat_upset": "warn"},
        },
        ledger_tail=[
            {
                "entity_id": str(winner.id),
                "event_type": "cultivation_change",
                "payload": {"to_rank_id": str(ranks[0].id)},
            },
            {
                "entity_id": str(loser.id),
                "event_type": "cultivation_change",
                "payload": {"to_rank_id": str(ranks[1].id)},
            },
        ],
        ledger_proposals=[],
    )
    assert any(i.code == "power_upset_without_justification" for i in issues)


@pytest.mark.unit
def test_unknown_rank_label_warn() -> None:
    ranks = [_rank("qi", "Luyện Khí", 0)]
    char = _character("Lâm Phong")
    settings = PowerSystemSettings(
        project_id=uuid.uuid4(),
        enabled=True,
        priority_gap=2,
        max_rank_jump_per_chapter=1,
        require_breakthrough_event=True,
    )
    issues = run_power_checks(
        prose="Lâm Phong tu luyện cảnh giới mới lạ.",
        chapter_number=1,
        characters=[char],
        ranks=ranks,
        techniques=[],
        settings=settings,
        genre_pack={"modules": {"power_system": {"enabled": True}}},
        ledger_tail=[],
        ledger_proposals=[],
    )
    assert any(i.code == "power_unknown_rank_label" for i in issues)


@pytest.mark.unit
def test_cultivation_proposals_extract() -> None:
    ranks = [_rank("qi", "Luyện Khí", 0), _rank("foundation", "Trúc Cơ", 1)]
    char = _character("Lâm Phong")
    proposals = build_cultivation_proposals(
        prose="Lâm Phong đạt Trúc Cơ.",
        characters=[char],
        ranks=ranks,
        ledger_tail=[
            {
                "entity_id": str(char.id),
                "event_type": "cultivation_change",
                "payload": {"to_rank_id": str(ranks[0].id)},
            }
        ],
    )
    assert len(proposals) == 1
    assert proposals[0]["event_type"] == "cultivation_change"
