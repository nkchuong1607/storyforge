"""Unit tests for scene structure continuity rules."""

import uuid
from types import SimpleNamespace

from app.models.enums import ContinuitySeverity
from app.services.continuity.relationship import normalize_pair
from app.services.continuity.scene import run_scene_structure_checks
from app.services.continuity.stakes import resolve_act_for_chapter


def _settings(**kwargs):
    defaults = {
        "enabled": True,
        "require_conflict": True,
        "require_outcome_on_complete": True,
        "min_goal_length": 8,
        "strictness": "standard",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _beat(**kwargs):
    defaults = {
        "id": uuid.uuid4(),
        "beat_key": "1.1",
        "summary": "test",
        "sort_order": 0,
        "completed": True,
        "goal": "A long enough goal for the beat",
        "conflict": "Opposition",
        "outcome": "",
        "stakes_level": None,
        "pov_character_id": None,
        "scene_type": "scene",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_scene_engine_disabled() -> None:
    issues = run_scene_structure_checks(
        beats=[_beat(outcome="")],
        chapter_number=1,
        settings=_settings(enabled=False),
        characters=[],
        genre_pack={},
    )
    assert issues == []


def test_missing_outcome_is_fail() -> None:
    issues = run_scene_structure_checks(
        beats=[_beat(conflict="", outcome="Resolved")],
        chapter_number=1,
        settings=_settings(),
        characters=[],
        genre_pack={},
    )
    assert any(i.code == "scene_missing_conflict" for i in issues)
    assert issues[0].severity == ContinuitySeverity.WARN.value


def test_duplicate_sort_order_fail() -> None:
    issues = run_scene_structure_checks(
        beats=[
            _beat(sort_order=0, outcome="ok"),
            _beat(sort_order=0, beat_key="1.2", outcome="ok"),
        ],
        chapter_number=1,
        settings=_settings(),
        characters=[],
        genre_pack={},
    )
    assert any(i.code == "scene_beat_order_invalid" for i in issues)


def test_normalize_pair_orders_ids() -> None:
    a = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    b = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
    left, right = normalize_pair(b, a)
    assert left == a
    assert right == b


def test_resolve_act_even_split() -> None:
    settings = SimpleNamespace(act_count=3, chapters_per_act=[])
    act, start, end = resolve_act_for_chapter(5, settings, total_chapters=9)
    assert act == 2
    assert start <= 5 <= end
