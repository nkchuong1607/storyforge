"""Unit tests for stakes continuity rules."""

import uuid
from types import SimpleNamespace

from app.services.continuity.stakes import run_stakes_checks


def _settings(**kwargs):
    defaults = {
        "enabled": True,
        "act_count": 3,
        "chapters_per_act": [
            {"act_number": 1, "start_chapter": 1, "end_chapter": 3},
            {"act_number": 2, "start_chapter": 4, "end_chapter": 6},
            {"act_number": 3, "start_chapter": 7, "end_chapter": 9},
        ],
        "flat_middle_window_chapters": 3,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_flat_middle_warn_in_act_2() -> None:
    entries = [
        SimpleNamespace(
            id=uuid.uuid4(),
            act_number=2,
            target_level=3,
            status="planned",
            plant_chapter_id=None,
            resolve_chapter_id=None,
            checkpoint_key="act2_mid",
        )
    ]
    issues = run_stakes_checks(
        project_id=uuid.uuid4(),
        chapter_number=5,
        settings=_settings(),
        entries=entries,
        beats=[],
        genre_pack={"strictness": {"stakes": "standard"}},
        stakes_ledger_proposals=[],
    )
    assert any(i.code == "stakes_flat_middle" for i in issues)


def test_unresolved_past_act_fail_strict() -> None:
    entries = [
        SimpleNamespace(
            id=uuid.uuid4(),
            act_number=1,
            target_level=3,
            status="planted",
            plant_chapter_id=uuid.uuid4(),
            resolve_chapter_id=None,
            checkpoint_key="act1_mid",
        )
    ]
    issues = run_stakes_checks(
        project_id=uuid.uuid4(),
        chapter_number=5,
        settings=_settings(),
        entries=entries,
        beats=[],
        genre_pack={
            "strictness": {"stakes": "strict"},
            "thresholds": {"stakes_unresolved_past_act": "fail"},
        },
        stakes_ledger_proposals=[],
    )
    assert any(i.code == "stakes_unresolved_past_act" for i in issues)
    assert any(i.severity == "fail" for i in issues)
