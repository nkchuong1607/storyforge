"""Unit tests for FakeLLM craft skills."""

from app.services.craft_defaults import mystery_fair_play_v1
from app.services.llm.craft_skills import (
    mystery_clue_plant,
    mystery_red_herring,
    mystery_reveal_align,
    run_craft_skill,
    run_pack_craft_skills,
)


def test_mystery_clue_plant_deterministic() -> None:
    result = mystery_clue_plant(prose="A clue was found.", twist_title="Killer")
    assert result.skill == "mystery_clue_plant"
    assert "Killer" in result.suggestion
    assert result.severity == "warn"


def test_mystery_reveal_align_lists_codes() -> None:
    result = mystery_reveal_align(
        prose="Reveal", open_checklist_codes=["craft_mystery_insufficient_plants"]
    )
    assert "craft_mystery_insufficient_plants" in result.suggestion


def test_mystery_red_herring_unlabeled() -> None:
    result = mystery_red_herring(prose="red herring here", has_misdirection_label=False)
    assert result.severity == "warn"
    labeled = mystery_red_herring(prose="red herring", has_misdirection_label=True)
    assert labeled.severity == "pass"


def test_run_craft_skill_dispatch() -> None:
    result = run_craft_skill("mystery_clue_plant", prose="x", twist_title="T")
    assert result.skill == "mystery_clue_plant"
    unknown = run_craft_skill("unknown_skill", prose="x")
    assert unknown.severity == "warn"


def test_run_pack_craft_skills_all_hooks() -> None:
    results = run_pack_craft_skills(
        mystery_fair_play_v1(),
        prose="red herring",
        twist_title="Killer",
        open_checklist_codes=["craft_mystery_clue_after_reveal"],
        has_misdirection_label=False,
    )
    assert len(results) == 3
    assert {r.skill for r in results} == {
        "mystery_clue_plant",
        "mystery_reveal_align",
        "mystery_red_herring",
    }
