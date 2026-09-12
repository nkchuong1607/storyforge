"""Psyche card validation unit tests."""

import pytest

from app.utils.psyche_validation import (
    merge_psyche_card,
    psyche_has_t2_minimum,
    psyche_meets_t3_minimum,
    validate_psyche_card_for_tier,
)


@pytest.mark.unit
def test_merge_psyche_card_partial() -> None:
    merged = merge_psyche_card(
        {"drive": "Revenge", "moral_boundaries": ["no kill"]},
        {"arc_flags": {"allow_moral_break": True}},
    )
    assert merged["drive"] == "Revenge"
    assert merged["arc_flags"]["allow_moral_break"] is True


@pytest.mark.unit
def test_t3_requires_value_hierarchy_and_boundaries() -> None:
    assert not psyche_meets_t3_minimum({"traits": ["brave"]})
    assert not psyche_meets_t3_minimum({"moral_boundaries": ["no kill"]})
    assert psyche_meets_t3_minimum(
        {
            "value_hierarchy": ["family"],
            "moral_boundaries": ["no kill"],
        }
    )
    assert psyche_meets_t3_minimum(
        {
            "traits": ["brave"],
            "moral_boundaries": ["no kill"],
        }
    )


@pytest.mark.unit
def test_t2_accepts_drive_or_legacy_traits() -> None:
    assert psyche_has_t2_minimum({"drive": "Revenge"})
    assert psyche_has_t2_minimum({"traits": ["brave"]})
    assert not psyche_has_t2_minimum({})


@pytest.mark.unit
def test_validate_psyche_card_for_t3() -> None:
    details = validate_psyche_card_for_tier(
        tier=3,
        psyche_card={"moral_boundaries": []},
    )
    assert any(d["field"] == "psyche_card.moral_boundaries" for d in details)
