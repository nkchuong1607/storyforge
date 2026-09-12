"""Repository unit tests with mocked SQLAlchemy session."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.chapter import Chapter
from app.models.enums import LedgerEntityType, LedgerEventType
from app.models.ledger_event import LedgerEvent
from app.models.power_system import PowerRank
from app.models.prompt_edit import PromptEditSession, PromptEditTurn
from app.models.prose_version import ProseVersion
from app.models.scene_beat import SceneBeat
from app.repositories.beat import BeatRepository
from app.repositories.chapter import ChapterRepository
from app.repositories.ledger import LedgerRepository
from app.repositories.power import PowerRepository
from app.repositories.prompt_edit import PromptEditRepository
from app.repositories.prose import ProseRepository
from app.utils.pagination import PageParams


@pytest.mark.unit
async def test_beat_repository_crud() -> None:
    session = AsyncMock()
    repo = BeatRepository(session)
    beat = SceneBeat(
        project_id=uuid.uuid4(),
        chapter_id=uuid.uuid4(),
        beat_key="1.1",
        summary="s",
        sort_order=1,
    )
    await repo.create(beat)
    session.add.assert_called_once()
    session.scalar = AsyncMock(return_value=uuid.uuid4())
    assert await repo.beat_key_exists(beat.chapter_id, "1.1") is True
    await repo.delete(beat)
    session.delete.assert_called_once()


@pytest.mark.unit
async def test_chapter_repository_get_and_create() -> None:
    session = AsyncMock()
    repo = ChapterRepository(session)
    chapter = Chapter(project_id=uuid.uuid4(), number=1, title="T")
    chapter.id = uuid.uuid4()
    await repo.create(chapter)
    session.scalar = AsyncMock(return_value=chapter.id)
    assert await repo.chapter_number_exists(chapter.project_id, 1) is True

    session.scalar = AsyncMock(return_value=chapter)
    found = await repo.get(chapter.project_id, chapter.id)
    assert found is chapter


@pytest.mark.unit
async def test_prose_repository_operations() -> None:
    session = AsyncMock()
    repo = ProseRepository(session)
    session.scalar = AsyncMock(return_value=3)
    assert await repo.get_max_version(uuid.uuid4()) == 3
    prose = ProseVersion(
        project_id=uuid.uuid4(),
        chapter_id=uuid.uuid4(),
        version=1,
        content="c",
        word_count=1,
        created_by=uuid.uuid4(),
    )
    await repo.create(prose)
    session.scalars = AsyncMock(return_value=MagicMock(all=lambda: []))
    session.scalar = AsyncMock(return_value=0)
    items, total = await repo.list_for_chapter(uuid.uuid4(), PageParams(page=1, page_size=20))
    assert items == []
    assert total == 0


@pytest.mark.unit
async def test_ledger_repository_operations() -> None:
    session = AsyncMock()
    repo = LedgerRepository(session)
    event = LedgerEvent(
        project_id=uuid.uuid4(),
        entity_type=LedgerEntityType.character,
        entity_id=uuid.uuid4(),
        event_type=LedgerEventType.status_change,
        payload={},
        chapter_id=uuid.uuid4(),
        chapter_number=1,
        prose_version=1,
    )
    await repo.create(event)
    session.scalar = AsyncMock(return_value=0)
    assert await repo.count_for_chapter(event.chapter_id) == 0


@pytest.mark.unit
async def test_power_repository_operations() -> None:
    session = AsyncMock()
    repo = PowerRepository(session)
    project_id = uuid.uuid4()
    session.get = AsyncMock(return_value=None)
    settings = await repo.ensure_settings(project_id)
    assert settings.project_id == project_id
    session.add.assert_called()

    rank = PowerRank(project_id=project_id, rank_key="qi", display_name="Luyện Khí", sort_order=0)
    rank.id = uuid.uuid4()
    await repo.create_rank(rank)
    session.scalar = AsyncMock(return_value=2)
    assert await repo.max_sort_order(project_id) == 2
    session.scalar = AsyncMock(return_value=1)
    assert await repo.count_techniques_for_rank(project_id, rank.id) == 1


@pytest.mark.unit
async def test_prompt_edit_repository_operations() -> None:
    session = AsyncMock()
    repo = PromptEditRepository(session)
    session_row = PromptEditSession(
        project_id=uuid.uuid4(),
        chapter_id=uuid.uuid4(),
        base_prose_version=1,
        status="active",
        created_by=uuid.uuid4(),
    )
    await repo.create_session(session_row)
    session.add.assert_called()
    turn = PromptEditTurn(
        project_id=session_row.project_id,
        session_id=uuid.uuid4(),
        turn_index=1,
        instruction="x",
        model="fake-llm",
        provider="fake",
        token_usage={},
    )
    await repo.create_turn(turn)
    session.scalar = AsyncMock(return_value=2)
    assert await repo.max_turn_index(turn.session_id) == 2
    session.scalar = AsyncMock(return_value=uuid.uuid4())
    assert await repo.prose_version_exists_for_turn(turn.id) is True
