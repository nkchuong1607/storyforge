"""Unit tests for craft continuity checklist rules."""

import uuid

from app.models.enums import GenreProfile, TwistPlanStatus
from app.services.continuity.craft import parse_checklist, run_craft_checks
from app.services.continuity.foreshadow import (
    ForeshadowPayoffContext,
    ForeshadowPlantContext,
    ForeshadowTwistContext,
)
from app.services.craft_defaults import mystery_fair_play_v1


def _twist(**overrides) -> ForeshadowTwistContext:
    defaults = {
        "twist_id": uuid.uuid4(),
        "title": "Killer identity",
        "secret_truth": "Butler did it",
        "status": TwistPlanStatus.armed,
        "constraints_json": {},
        "genre_strictness": None,
        "misdirection": None,
    }
    defaults.update(overrides)
    return ForeshadowTwistContext(**defaults)


def test_parse_checklist_from_pack() -> None:
    items = parse_checklist(mystery_fair_play_v1())
    assert len(items) == 4
    assert items[0].code == "craft_mystery_clue_after_reveal"


def test_clue_after_reveal_fail() -> None:
    twist = _twist()
    payoff_ch = uuid.uuid4()
    payoffs = [
        ForeshadowPayoffContext(
            payoff_id=uuid.uuid4(),
            twist=twist,
            target_chapter_id=payoff_ch,
            target_chapter_number=5,
            min_plants=2,
            required_plant_ids=[],
        )
    ]
    issues = run_craft_checks(
        chapter_id=payoff_ch,
        chapter_number=5,
        prose="Reveal chapter",
        genre_profile=GenreProfile.mystery,
        pack_json=mystery_fair_play_v1(),
        payoffs=payoffs,
        plants=[],
        all_twists=[twist],
    )
    codes = {i.code for i in issues}
    assert "craft_mystery_clue_after_reveal" in codes
    assert "craft_mystery_insufficient_plants" in codes


def test_unlabeled_misdirection_warn() -> None:
    twist = _twist()
    chapter_id = uuid.uuid4()
    issues = run_craft_checks(
        chapter_id=chapter_id,
        chapter_number=3,
        prose="This is a red herring nghi phạm giả.",
        genre_profile=GenreProfile.mystery,
        pack_json=mystery_fair_play_v1(),
        payoffs=[],
        plants=[],
        all_twists=[twist],
    )
    assert any(i.code == "craft_mystery_unlabeled_misdirection" for i in issues)
    assert issues[0].category == "craft"
    assert issues[0].severity == "warn"


def test_insufficient_plants_with_one_plant() -> None:
    twist = _twist()
    payoff_ch = uuid.uuid4()
    plant_ch = uuid.uuid4()
    payoffs = [
        ForeshadowPayoffContext(
            payoff_id=uuid.uuid4(),
            twist=twist,
            target_chapter_id=payoff_ch,
            target_chapter_number=5,
            min_plants=2,
            required_plant_ids=[],
        )
    ]
    plants = [
        ForeshadowPlantContext(
            plant_id=uuid.uuid4(),
            twist_id=twist.twist_id,
            chapter_id=plant_ch,
            chapter_number=4,
        )
    ]
    issues = run_craft_checks(
        chapter_id=payoff_ch,
        chapter_number=5,
        prose="Payoff",
        genre_profile=GenreProfile.mystery,
        pack_json=mystery_fair_play_v1(),
        payoffs=payoffs,
        plants=plants,
        all_twists=[twist],
    )
    codes = {i.code for i in issues}
    assert "craft_mystery_insufficient_plants" in codes
