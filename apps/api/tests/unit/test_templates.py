"""Template seed unit tests."""

import pytest

from app.models.enums import ProjectTemplate
from app.templates.seeds import get_template_seed


@pytest.mark.unit
def test_blank_template_has_no_seeds() -> None:
    seed = get_template_seed(ProjectTemplate.blank)
    snapshot = seed.build_snapshot_json(ProjectTemplate.blank)
    assert snapshot["version"] == 0
    assert snapshot["entries"] == []
    assert seed.chapters == []
    assert seed.characters == []


@pytest.mark.unit
def test_xianxia_template_has_entries_and_characters() -> None:
    seed = get_template_seed(ProjectTemplate.xianxia_starter)
    snapshot = seed.build_snapshot_json(ProjectTemplate.xianxia_starter)
    assert snapshot["generated_from_template"] == "xianxia_starter"
    assert len(snapshot["entries"]) >= 5
    assert seed.characters[0].display_name == "Lý Phong"
    assert seed.chapters[0].number == 1


@pytest.mark.unit
def test_mystery_template_has_detective_seed() -> None:
    seed = get_template_seed(ProjectTemplate.mystery_starter)
    assert any(entry.section.value == "timeline" for entry in seed.bible_entries)
    assert seed.characters[0].display_name == "Trần Hạo"
