"""Unit tests for tier promotion validation."""

import pytest

from app.utils.tier_validation import (
    TierRequirementsError,
    compute_tier_suggest,
    validate_tier_promotion,
)


@pytest.mark.unit
def test_t1_requires_voice_or_relation() -> None:
    with pytest.raises(TierRequirementsError):
        validate_tier_promotion(
            current_tier=0,
            role_one_liner="Seed",
            psyche_card=None,
            metadata={},
        )


@pytest.mark.unit
def test_t1_passes_with_voice_hint() -> None:
    assert (
        validate_tier_promotion(
            current_tier=0,
            role_one_liner="Seed",
            psyche_card=None,
            metadata={"voice_hint": "trầm ấm"},
        )
        == 1
    )


@pytest.mark.unit
def test_t2_requires_psyche_skeleton() -> None:
    with pytest.raises(TierRequirementsError):
        validate_tier_promotion(
            current_tier=1,
            role_one_liner="Seed",
            psyche_card={},
            metadata={"voice_hint": "trầm ấm"},
        )


@pytest.mark.unit
def test_t3_requires_confirm_and_psyche_minimum() -> None:
    with pytest.raises(TierRequirementsError):
        validate_tier_promotion(
            current_tier=2,
            role_one_liner="Seed",
            psyche_card={"traits": ["kiên định"]},
            metadata={"voice_hint": "trầm ấm"},
            confirm_t3=False,
        )

    with pytest.raises(TierRequirementsError):
        validate_tier_promotion(
            current_tier=2,
            role_one_liner="Seed",
            psyche_card={"traits": ["kiên định"], "moral_boundaries": ["không giết vô tội"]},
            metadata={"voice_hint": "trầm ấm"},
            confirm_t3=True,
        )

    assert (
        validate_tier_promotion(
            current_tier=2,
            role_one_liner="Seed",
            psyche_card={
                "traits": ["kiên định"],
                "moral_boundaries": ["không giết vô tội"],
            },
            metadata={"voice_hint": "trầm ấm", "arc_note": "báo thù"},
            confirm_t3=True,
        )
        == 3
    )


@pytest.mark.unit
def test_compute_tier_suggest() -> None:
    assert compute_tier_suggest(2, {}) is False
    assert compute_tier_suggest(3, {}) is True
    assert compute_tier_suggest(1, {"tier_suggest": True}) is True
