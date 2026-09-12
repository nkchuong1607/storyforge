"""Psychology service unit tests."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import InvalidPsycheCardError, NotFoundError, PsychStateImmutableError
from app.models.chapter import Chapter
from app.models.character import Character
from app.models.project import Project
from app.models.psych_state import PsychState
from app.schemas.psychology import PsycheCardUpdateRequest
from app.services.psych_context_pack import PsychContextPackService
from app.services.psychology import PsychologyService
from app.utils.pagination import PageParams


def _project() -> Project:
    project = MagicMock(spec=Project)
    project.id = uuid.uuid4()
    return project


def _character(project_id: uuid.UUID, *, tier: int = 3) -> Character:
    character = MagicMock(spec=Character)
    character.id = uuid.uuid4()
    character.project_id = project_id
    character.display_name = "Lý Phong"
    character.tier = tier
    character.psyche_card = {
        "drive": "Revenge",
        "value_hierarchy": ["family"],
        "moral_boundaries": ["no kill"],
    }
    character.updated_at = datetime.now(UTC)
    return character


@pytest.mark.unit
async def test_get_psyche_card_not_found() -> None:
    service = PsychologyService(AsyncMock())
    service.characters.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.get_psyche_card(_project(), uuid.uuid4())


@pytest.mark.unit
async def test_get_psyche_card_success() -> None:
    project = _project()
    character = _character(project.id)
    service = PsychologyService(AsyncMock())
    service.characters.get_by_id = AsyncMock(return_value=character)
    result = await service.get_psyche_card(project, character.id)
    assert result.character_id == character.id
    assert result.psyche_card.drive == "Revenge"


@pytest.mark.unit
async def test_update_psyche_card_invalid_t3() -> None:
    project = _project()
    character = _character(project.id, tier=3)
    service = PsychologyService(AsyncMock())
    service.characters.get_by_id = AsyncMock(return_value=character)
    with pytest.raises(InvalidPsycheCardError):
        await service.update_psyche_card(
            project,
            character.id,
            PsycheCardUpdateRequest(psyche_card={"moral_boundaries": []}),
        )


@pytest.mark.unit
async def test_list_psych_states() -> None:
    project = _project()
    character = _character(project.id)
    psych = PsychState(
        id=uuid.uuid4(),
        project_id=project.id,
        character_id=character.id,
        chapter_id=uuid.uuid4(),
        stress_level=5,
        dominant_emotion="calm",
        active_goal="train",
        settled_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )
    service = PsychologyService(AsyncMock())
    service.characters.get_by_id = AsyncMock(return_value=character)
    service.psych_states.list_timeline = AsyncMock(return_value=([(psych, 1)], 1))
    result = await service.list_psych_states(
        project, character.id, PageParams(page=1, page_size=50)
    )
    assert len(result.items) == 1
    assert result.items[0].chapter_number == 1


@pytest.mark.unit
async def test_get_psych_state_by_chapter_not_found() -> None:
    project = _project()
    character = _character(project.id)
    service = PsychologyService(AsyncMock())
    service.characters.get_by_id = AsyncMock(return_value=character)
    chapter = Chapter(id=uuid.uuid4(), project_id=project.id, number=1, title="T")
    service.chapters.get = AsyncMock(return_value=chapter)
    service.psych_states.get_by_character_chapter = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.get_psych_state_by_chapter(project, character.id, uuid.uuid4())


@pytest.mark.unit
async def test_attempt_update_psych_state_immutable() -> None:
    project = _project()
    character = _character(project.id)
    psych = PsychState(
        id=uuid.uuid4(),
        project_id=project.id,
        character_id=character.id,
        chapter_id=uuid.uuid4(),
        stress_level=5,
        dominant_emotion="calm",
        active_goal="train",
        settled_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )
    service = PsychologyService(AsyncMock())
    service.characters.get_by_id = AsyncMock(return_value=character)
    service.psych_states.get_by_id = AsyncMock(return_value=psych)
    with pytest.raises(PsychStateImmutableError):
        await service.attempt_update_psych_state(project, character.id, psych.id, stress_level=9)


@pytest.mark.unit
async def test_psych_context_pack_build() -> None:
    project = _project()
    chapter_id = uuid.uuid4()
    character = _character(project.id)
    chapter = Chapter(id=chapter_id, project_id=project.id, number=1, title="Ch1")

    beat = MagicMock()
    beat.id = uuid.uuid4()
    beat.summary = "Lý Phong đi tu"

    psych = PsychState(
        id=uuid.uuid4(),
        project_id=project.id,
        character_id=character.id,
        chapter_id=uuid.uuid4(),
        stress_level=4,
        dominant_emotion="resolve",
        active_goal="train",
        settled_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )

    from app.schemas.psychology import PsychContextPackRequest

    service = PsychContextPackService(AsyncMock())
    service.chapters.get = AsyncMock(return_value=chapter)
    service.beats.list_for_chapter = AsyncMock(return_value=[beat])
    service.characters.find_by_name_or_alias = AsyncMock(return_value=character)
    service.characters.get_by_id = AsyncMock(return_value=character)
    service.psych_states.get_latest_before_chapter = AsyncMock(return_value=(psych, 1))

    result = await service.build_context_pack(
        project,
        PsychContextPackRequest(chapter_id=chapter_id, character_ids=[character.id]),
    )
    assert len(result.entries) == 1
    assert result.entries[0].latest_psych_state is not None


@pytest.mark.unit
async def test_psych_context_pack_chapter_not_found() -> None:
    from app.schemas.psychology import PsychContextPackRequest

    service = PsychContextPackService(AsyncMock())
    service.chapters.get = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.build_context_pack(
            _project(),
            PsychContextPackRequest(chapter_id=uuid.uuid4()),
        )
