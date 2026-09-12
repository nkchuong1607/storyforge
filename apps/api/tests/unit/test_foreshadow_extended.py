"""Extended foreshadow rule unit tests."""

import uuid

from app.models.enums import GenreProfile, TwistPlanStatus
from app.services.continuity.foreshadow import (
    ForeshadowPayoffContext,
    ForeshadowPlantContext,
    ForeshadowTwistContext,
    run_foreshadow_checks,
)


def test_required_plants_missing_fail() -> None:
    twist_id = uuid.uuid4()
    missing_id = uuid.uuid4()
    twist = ForeshadowTwistContext(
        twist_id=twist_id,
        title="T",
        secret_truth="S",
        status=TwistPlanStatus.armed,
        constraints_json={},
        genre_strictness=None,
    )
    payoff = ForeshadowPayoffContext(
        payoff_id=uuid.uuid4(),
        twist=twist,
        target_chapter_id=uuid.uuid4(),
        target_chapter_number=5,
        min_plants=1,
        required_plant_ids=[missing_id],
    )
    issues = run_foreshadow_checks(
        chapter_id=uuid.uuid4(),
        chapter_number=5,
        prose="text",
        genre_profile=GenreProfile.mystery,
        payoffs=[payoff],
        plants=[],
        all_twists=[twist],
    )
    assert any(i.code == "foreshadow_required_plants_missing" for i in issues)


def test_plant_count_below_minimum_code() -> None:
    twist_id = uuid.uuid4()
    plant_id = uuid.uuid4()
    twist = ForeshadowTwistContext(
        twist_id=twist_id,
        title="T",
        secret_truth="S",
        status=TwistPlanStatus.armed,
        constraints_json={},
        genre_strictness=None,
    )
    payoff = ForeshadowPayoffContext(
        payoff_id=uuid.uuid4(),
        twist=twist,
        target_chapter_id=uuid.uuid4(),
        target_chapter_number=5,
        min_plants=2,
        required_plant_ids=[],
    )
    plants = [
        ForeshadowPlantContext(plant_id, twist_id, uuid.uuid4(), 3),
    ]
    issues = run_foreshadow_checks(
        chapter_id=uuid.uuid4(),
        chapter_number=5,
        prose="text",
        genre_profile=GenreProfile.mystery,
        payoffs=[payoff],
        plants=plants,
        all_twists=[twist],
    )
    codes = {i.code for i in issues}
    assert (
        "foreshadow_plant_count_below_minimum" in codes
        or "foreshadow_payoff_without_plants" in codes
    )


def test_knowledge_wall_warn() -> None:
    char_id = uuid.uuid4()
    twist_id = uuid.uuid4()
    secret = "Hidden knowledge"
    twist = ForeshadowTwistContext(
        twist_id=twist_id,
        title="T",
        secret_truth=secret,
        status=TwistPlanStatus.planted,
        constraints_json={
            "knowledge_walls": [{"character_id": str(char_id), "must_not_know_before_chapter": 10}]
        },
        genre_strictness=None,
    )
    issues = run_foreshadow_checks(
        chapter_id=uuid.uuid4(),
        chapter_number=3,
        prose=f"@{char_id} said {secret}",
        genre_profile=GenreProfile.xianxia,
        payoffs=[],
        plants=[],
        all_twists=[twist],
    )
    assert any(i.code == "foreshadow_knowledge_wall" for i in issues)
