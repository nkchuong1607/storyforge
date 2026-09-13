"""Phase 9 bible section mapping unit tests."""

import pytest

from app.models.enums import BibleSection, Phase9BibleSection
from app.utils.phase9_bible import (
    build_entry_key,
    phase9_section_to_bible_section,
    snapshot_to_slice_json,
    validate_bible_key,
)


@pytest.mark.unit
def test_phase9_section_mapping() -> None:
    assert phase9_section_to_bible_section(Phase9BibleSection.world) == BibleSection.world_rules
    assert phase9_section_to_bible_section(Phase9BibleSection.glossary) == BibleSection.glossary


@pytest.mark.unit
def test_build_entry_key() -> None:
    key = build_entry_key(Phase9BibleSection.world, "Huyết Đan Rules")
    assert key.startswith("world.")


@pytest.mark.unit
def test_validate_bible_key() -> None:
    assert validate_bible_key("world.locations.inner_hall")
    assert not validate_bible_key("INVALID KEY")


@pytest.mark.unit
def test_snapshot_to_slice_json() -> None:
    snapshot = {
        "entries": [
            {
                "entry_key": "world.rules.cultivation",
                "title": "Cultivation",
                "content_md": "Rules here",
            }
        ]
    }
    result = snapshot_to_slice_json(snapshot, ["world"])
    assert "world" in result
