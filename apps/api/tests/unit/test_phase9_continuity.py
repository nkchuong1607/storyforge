"""Phase 9 continuity WARN-only unit tests."""

import uuid

import pytest

from app.models.enums import ContinuityCategory, ContinuitySeverity
from app.models.project import Project
from app.models.research import ResearchNoteLink
from app.services.continuity.research import run_research_checks
from app.services.continuity.series_rules import run_series_checks


@pytest.mark.unit
def test_research_orphan_character_warn() -> None:
    char_id = uuid.uuid4()
    link = ResearchNoteLink(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        note_id=uuid.uuid4(),
        link_type="character",
        character_id=char_id,
    )
    issues = run_research_checks(links=[link], characters=[], snapshot_json={"entries": []})
    assert len(issues) == 1
    assert issues[0].severity == ContinuitySeverity.WARN.value
    assert issues[0].category == ContinuityCategory.research.value
    assert issues[0].code == "research_link_orphan_character"


@pytest.mark.unit
def test_series_parent_slice_updated_warn() -> None:
    project = Project(
        id=uuid.uuid4(),
        slug="book-2",
        title="Book 2",
        created_by=uuid.uuid4(),
        series_id=uuid.uuid4(),
        last_seen_series_slice_version=1,
    )
    issues = run_series_checks(
        project=project,
        slice_version=3,
        staging_rows=[],
        inherited_keys=set(),
    )
    assert any(i.code == "series_parent_slice_updated" for i in issues)
    assert all(i.severity == ContinuitySeverity.WARN.value for i in issues)
