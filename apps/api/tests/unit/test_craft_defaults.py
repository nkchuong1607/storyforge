"""Unit tests for craft pack defaults."""

from app.models.enums import GenreProfile
from app.services.craft_defaults import (
    MYSTERY_FAIR_PLAY_V1_ID,
    catalog_seed_packs,
    is_genre_compatible,
    mystery_fair_play_v1,
    pack_display_name,
)


def test_mystery_pack_id_and_checklist() -> None:
    pack = mystery_fair_play_v1()
    assert pack["id"] == MYSTERY_FAIR_PLAY_V1_ID
    assert len(pack["checklist"]) >= 4
    codes = {item["code"] for item in pack["checklist"]}
    assert "craft_mystery_clue_after_reveal" in codes
    assert "craft_mystery_unlabeled_misdirection" in codes


def test_catalog_seed_packs() -> None:
    seeds = catalog_seed_packs()
    assert len(seeds) == 1
    assert seeds[0]["id"] == MYSTERY_FAIR_PLAY_V1_ID


def test_genre_compatible_mystery_and_custom() -> None:
    pack = mystery_fair_play_v1()
    assert is_genre_compatible(pack, GenreProfile.mystery.value)
    assert is_genre_compatible(pack, GenreProfile.custom.value)
    assert not is_genre_compatible(pack, GenreProfile.xianxia.value)


def test_pack_display_name_fallback() -> None:
    assert pack_display_name(mystery_fair_play_v1()) == "Mystery — Fair Play"
    assert pack_display_name({"id": "x.y.v1"}) == "x.y.v1"
