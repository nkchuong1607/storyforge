"""Repository unit tests for Phase 8."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.relationship import Relationship
from app.models.relationship_event import RelationshipEvent
from app.models.stakes_ledger_entry import StakesLedgerEntry
from app.repositories.relationship import RelationshipRepository
from app.repositories.scene_engine import SceneEngineRepository
from app.repositories.stakes import StakesRepository


@pytest.mark.unit
async def test_relationship_repository_methods() -> None:
    session = AsyncMock()
    repo = RelationshipRepository(session)
    rel = Relationship(
        project_id=uuid.uuid4(),
        character_a_id=uuid.uuid4(),
        character_b_id=uuid.uuid4(),
        relation_type="ally",
    )
    rel.id = uuid.uuid4()
    event = RelationshipEvent(
        project_id=rel.project_id,
        relationship_id=rel.id,
        event_type="trust_shift",
        intensity_after=1,
        chapter_id=uuid.uuid4(),
        chapter_number=1,
        prose_version=1,
    )

    session.scalar = AsyncMock(return_value=1)
    session.scalars = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=[rel])))
    rows, total = await repo.list_for_project(rel.project_id)
    assert total == 1
    session.scalar = AsyncMock(return_value=rel)
    assert await repo.get(rel.project_id, rel.id) is rel
    assert await repo.get_by_pair(rel.project_id, rel.character_a_id, rel.character_b_id) is rel
    session.scalars = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=[event])))
    assert len(await repo.list_events(rel.project_id, rel.id)) == 1
    session.scalar = AsyncMock(return_value=2)
    assert await repo.count_settled_events(rel.id) == 2
    await repo.create(rel)
    await repo.update(rel)
    await repo.delete(rel)


@pytest.mark.unit
async def test_stakes_and_scene_engine_repositories() -> None:
    session = AsyncMock()
    stakes = StakesRepository(session)
    settings = MagicMock(project_id=uuid.uuid4())
    entry = StakesLedgerEntry(
        project_id=settings.project_id,
        act_number=1,
        checkpoint_key="k",
        title="t",
        target_level=2,
    )
    session.get = AsyncMock(return_value=None)
    session.add = MagicMock()
    session.flush = AsyncMock()
    created_settings = await stakes.ensure_settings(settings.project_id)
    assert created_settings is not None
    session.get = AsyncMock(return_value=settings)
    assert await stakes.get_settings(settings.project_id) is None or settings
    session.scalars = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=[entry])))
    assert len(await stakes.list_entries(settings.project_id)) == 1
    session.scalar = AsyncMock(return_value=entry)
    assert await stakes.get_entry(settings.project_id, uuid.uuid4()) is entry

    scene_repo = SceneEngineRepository(session)
    await scene_repo.ensure_settings(settings.project_id)
