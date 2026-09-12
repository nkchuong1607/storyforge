"""Unit tests for character alias helpers."""

import pytest

from app.utils.character_aliases import (
    alias_present,
    append_alias_if_distinct,
    display_name_matches,
    normalize_name,
)


@pytest.mark.unit
def test_normalize_name_casefolds() -> None:
    assert normalize_name("  Phong  ") == "phong"


@pytest.mark.unit
def test_display_name_matches_case_insensitive() -> None:
    assert display_name_matches("Lý Phong", "lý phong")


@pytest.mark.unit
def test_append_alias_skips_duplicate_and_display_name() -> None:
    aliases = ["Phong"]
    assert append_alias_if_distinct(aliases, "Phong", "Lý Phong") == ["Phong"]
    assert append_alias_if_distinct(aliases, "Lý Phong", "Lý Phong") == ["Phong"]
    updated = append_alias_if_distinct(aliases, "Kiếm Thánh", "Lý Phong")
    assert updated == ["Phong", "Kiếm Thánh"]


@pytest.mark.unit
def test_alias_present() -> None:
    assert alias_present(["Phong", "Lý đại ca"], "phong")
