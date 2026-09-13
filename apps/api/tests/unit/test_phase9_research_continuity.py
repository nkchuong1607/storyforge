"""Research continuity orphan bible key test."""

import uuid

import pytest

from app.models.research import ResearchNoteLink
from app.services.continuity.research import run_research_checks


@pytest.mark.unit
def test_research_orphan_bible_key_warn() -> None:
    link = ResearchNoteLink(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        note_id=uuid.uuid4(),
        link_type="fact",
        bible_key="world.missing.key",
    )
    issues = run_research_checks(links=[link], characters=[], snapshot_json={"entries": []})
    assert issues[0].code == "research_link_orphan_bible_key"


@pytest.mark.unit
def test_research_orphan_archived_character_warn() -> None:
    from app.models.character import Character
    from app.models.enums import CharacterStatus

    char_id = uuid.uuid4()
    char = Character(
        project_id=uuid.uuid4(),
        display_name="X",
        status=CharacterStatus.archived,
    )
    char.id = char_id
    link = ResearchNoteLink(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        note_id=uuid.uuid4(),
        link_type="character",
        character_id=char_id,
    )
    issues = run_research_checks(links=[link], characters=[char], snapshot_json={"entries": []})
    assert issues[0].code == "research_link_orphan_character"
