"""Genre rule pack merge unit tests."""

import pytest

from app.models.enums import GenreProfile
from app.services.genre_defaults import deep_merge, default_genre_rule_pack, merged_genre_pack


@pytest.mark.unit
def test_mystery_defaults_stricter_foreshadow() -> None:
    pack = default_genre_rule_pack(GenreProfile.mystery)
    assert pack["modules"]["power_system"]["enabled"] is False
    assert pack["thresholds"]["foreshadow_min_plants_default"] == 2
    assert pack["thresholds"]["foreshadow_payoff_without_plants"] == "fail"


@pytest.mark.unit
def test_xianxia_enables_power_module() -> None:
    pack = default_genre_rule_pack(GenreProfile.xianxia)
    assert pack["modules"]["power_system"]["enabled"] is True
    assert pack["strictness"]["power"] == "strict"


@pytest.mark.unit
def test_deep_merge_partial_patch() -> None:
    base = {"modules": {"power_system": {"enabled": True}}, "thresholds": {"a": 1}}
    patch = {"thresholds": {"b": 2}}
    merged = deep_merge(base, patch)
    assert merged["modules"]["power_system"]["enabled"] is True
    assert merged["thresholds"]["a"] == 1
    assert merged["thresholds"]["b"] == 2


@pytest.mark.unit
def test_literary_and_romance_defaults() -> None:
    literary = default_genre_rule_pack(GenreProfile.literary)
    assert literary["display_name"] == "Văn học"
    romance = default_genre_rule_pack(GenreProfile.romance)
    assert romance["tone"]["romance_subplot"] == "primary"


@pytest.mark.unit
def test_merged_genre_pack_overrides() -> None:
    stored = {"thresholds": {"foreshadow_min_plants_default": 3}}
    pack = merged_genre_pack(stored, GenreProfile.mystery)
    assert pack["thresholds"]["foreshadow_min_plants_default"] == 3
