"""Series continuity rules unit tests."""

import uuid

import pytest

from app.models.bible import BibleEntryStaging
from app.models.enums import BibleSection
from app.models.project import Project
from app.services.continuity.series_rules import inherited_keys_from_slice, run_series_checks


@pytest.mark.unit
def test_inherited_keys_from_slice() -> None:
    slice_json = {
        "world": {"rules": {"cultivation_realms": {"title": "Realms", "content_md": "..."}}}
    }
    keys = inherited_keys_from_slice(slice_json)
    assert "world.rules.cultivation_realms" in keys


@pytest.mark.unit
def test_series_override_without_reason_warn() -> None:
    project = Project(
        id=uuid.uuid4(),
        slug="b",
        title="B",
        created_by=uuid.uuid4(),
        series_id=uuid.uuid4(),
        last_seen_series_slice_version=1,
    )
    staging = BibleEntryStaging(
        project_id=project.id,
        entry_key="world.custom",
        section=BibleSection.world_rules,
        title="Override",
        content_md="x",
        metadata_={"series_override": True},
        base_bible_version=0,
        created_by=uuid.uuid4(),
    )
    staging.id = uuid.uuid4()
    issues = run_series_checks(
        project=project,
        slice_version=1,
        staging_rows=[staging],
        inherited_keys=set(),
    )
    assert any(i.code == "series_override_without_reason" for i in issues)


@pytest.mark.unit
def test_series_inherited_key_conflict_warn() -> None:
    project = Project(
        id=uuid.uuid4(),
        slug="b",
        title="B",
        created_by=uuid.uuid4(),
        series_id=uuid.uuid4(),
        last_seen_series_slice_version=1,
    )
    staging = BibleEntryStaging(
        project_id=project.id,
        entry_key="world.rules.realms",
        section=BibleSection.world_rules,
        title="Edit",
        content_md="x",
        metadata_={},
        base_bible_version=0,
        created_by=uuid.uuid4(),
    )
    staging.id = uuid.uuid4()
    issues = run_series_checks(
        project=project,
        slice_version=1,
        staging_rows=[staging],
        inherited_keys={"world.rules.realms"},
    )
    assert any(i.code == "series_inherited_key_conflict" for i in issues)
