"""Foreshadow fairness rule unit tests."""

import uuid

from app.models.enums import GenreProfile, TwistPlanStatus
from app.services.continuity.foreshadow import (
    ForeshadowPayoffContext,
    ForeshadowPlantContext,
    ForeshadowTwistContext,
    count_eligible_plants,
    evaluate_payoff_fairness,
    run_foreshadow_checks,
)


def _twist(**kwargs) -> ForeshadowTwistContext:
    defaults = {
        "twist_id": uuid.uuid4(),
        "title": "Test Twist",
        "secret_truth": "Hidden truth",
        "status": TwistPlanStatus.armed,
        "constraints_json": {},
        "genre_strictness": None,
    }
    defaults.update(kwargs)
    return ForeshadowTwistContext(**defaults)


def test_count_eligible_plants_before_payoff_chapter() -> None:
    twist_id = uuid.uuid4()
    plants = [
        ForeshadowPlantContext(uuid.uuid4(), twist_id, uuid.uuid4(), 3),
        ForeshadowPlantContext(uuid.uuid4(), twist_id, uuid.uuid4(), 5),
    ]
    assert count_eligible_plants(plants, twist_id, 4) == 1
    assert count_eligible_plants(plants, twist_id, 6) == 2


def test_mystery_zero_plants_fail_fairness() -> None:
    twist = _twist(status=TwistPlanStatus.armed)
    payoff = ForeshadowPayoffContext(
        payoff_id=uuid.uuid4(),
        twist=twist,
        target_chapter_id=uuid.uuid4(),
        target_chapter_number=5,
        min_plants=1,
        required_plant_ids=[],
    )
    codes, state = evaluate_payoff_fairness(
        payoff=payoff, plants=[], genre_profile=GenreProfile.mystery
    )
    assert "foreshadow_payoff_without_plants" in codes
    assert state == "fail"


def test_xianxia_zero_plants_warn_fairness() -> None:
    twist = _twist(status=TwistPlanStatus.armed)
    payoff = ForeshadowPayoffContext(
        payoff_id=uuid.uuid4(),
        twist=twist,
        target_chapter_id=uuid.uuid4(),
        target_chapter_number=5,
        min_plants=1,
        required_plant_ids=[],
    )
    codes, state = evaluate_payoff_fairness(
        payoff=payoff, plants=[], genre_profile=GenreProfile.xianxia
    )
    assert codes
    assert state == "warn"


def test_strict_twist_overrides_xianxia_to_fail() -> None:
    twist = _twist(status=TwistPlanStatus.armed, genre_strictness="strict")
    payoff = ForeshadowPayoffContext(
        payoff_id=uuid.uuid4(),
        twist=twist,
        target_chapter_id=uuid.uuid4(),
        target_chapter_number=5,
        min_plants=1,
        required_plant_ids=[],
    )
    codes, state = evaluate_payoff_fairness(
        payoff=payoff, plants=[], genre_profile=GenreProfile.xianxia
    )
    assert codes
    assert state == "fail"


def test_unseeded_reveal_fail_on_payoff_chapter() -> None:
    twist_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    twist = _twist(twist_id=twist_id, status=TwistPlanStatus.seeded)
    payoff = ForeshadowPayoffContext(
        payoff_id=uuid.uuid4(),
        twist=twist,
        target_chapter_id=chapter_id,
        target_chapter_number=5,
        min_plants=1,
        required_plant_ids=[],
    )
    issues = run_foreshadow_checks(
        chapter_id=chapter_id,
        chapter_number=5,
        prose="Some prose",
        genre_profile=GenreProfile.mystery,
        payoffs=[payoff],
        plants=[],
        all_twists=[twist],
    )
    codes = {i.code for i in issues}
    assert "foreshadow_unseeded_reveal" in codes


def test_secret_truth_in_prose_fails_f5() -> None:
    twist_id = uuid.uuid4()
    secret = "Sư phụ là sát thủ"
    twist = _twist(twist_id=twist_id, secret_truth=secret)
    issues = run_foreshadow_checks(
        chapter_id=uuid.uuid4(),
        chapter_number=2,
        prose=f"Draft mentions {secret} accidentally",
        genre_profile=GenreProfile.xianxia,
        payoffs=[],
        plants=[],
        all_twists=[twist],
    )
    assert any(i.code == "foreshadow_constrained_fact_leaked" for i in issues)


def test_evidence_excludes_secret_truth() -> None:
    twist_id = uuid.uuid4()
    twist = _twist(twist_id=twist_id, status=TwistPlanStatus.armed)
    payoff = ForeshadowPayoffContext(
        payoff_id=uuid.uuid4(),
        twist=twist,
        target_chapter_id=uuid.uuid4(),
        target_chapter_number=3,
        min_plants=2,
        required_plant_ids=[],
    )
    issues = run_foreshadow_checks(
        chapter_id=uuid.uuid4(),
        chapter_number=3,
        prose="text",
        genre_profile=GenreProfile.mystery,
        payoffs=[payoff],
        plants=[],
        all_twists=[twist],
    )
    for issue in issues:
        assert "secret_truth" not in issue.evidence
        assert twist.secret_truth not in issue.message
