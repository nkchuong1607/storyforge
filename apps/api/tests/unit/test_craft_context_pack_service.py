"""Craft context pack service unit tests."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import NotFoundError
from app.models.craft_pack import CraftPack, ProjectCraftPack
from app.models.enums import GenreProfile, PlantSalience, TwistPlanKind, TwistPlanStatus
from app.models.twist import TwistPlan, TwistPlant
from app.schemas.craft_pack import CraftContextPackRequest
from app.services.craft_context_pack import CraftContextPackService
from app.services.craft_defaults import MYSTERY_FAIR_PLAY_V1_ID, mystery_fair_play_v1


@pytest.mark.unit
async def test_build_craft_context_pack() -> None:
    session = AsyncMock()
    service = CraftContextPackService(session)
    project_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    project = MagicMock(
        id=project_id,
        genre_profile=GenreProfile.mystery,
        genre_rule_pack_json={},
    )
    chapter = MagicMock(id=chapter_id, number=5)
    service.chapters.get = AsyncMock(return_value=chapter)

    binding = ProjectCraftPack(
        id=uuid.uuid4(),
        project_id=project_id,
        craft_pack_id=MYSTERY_FAIR_PLAY_V1_ID,
        active=True,
        bound_at=datetime.now(UTC),
    )
    catalog = CraftPack(
        id=MYSTERY_FAIR_PLAY_V1_ID,
        schema_version=1,
        pack_json=mystery_fair_play_v1(),
        installed_at=datetime.now(UTC),
    )
    service.craft.get_active_binding = AsyncMock(return_value=binding)
    service.craft.get_catalog_pack = AsyncMock(return_value=catalog)

    now = datetime.now(UTC)
    twist = TwistPlan(
        id=uuid.uuid4(),
        project_id=project_id,
        title="Killer",
        secret_truth="hidden",
        status=TwistPlanStatus.planted,
        kind=TwistPlanKind.twist,
        constraints_json={},
        genre_strictness=None,
        misdirection="False trail",
        created_by=uuid.uuid4(),
        created_at=now,
        updated_at=now,
    )
    plant = TwistPlant(
        id=uuid.uuid4(),
        project_id=project_id,
        twist_id=twist.id,
        chapter_id=chapter_id,
        salience=PlantSalience.hard,
        snippet="clue",
        sort_order=0,
        created_at=now,
        updated_at=now,
    )
    service.twists.list_plants_for_project = AsyncMock(return_value=[plant])
    service.twists.list_all_plans = AsyncMock(return_value=[twist])
    service.twists.list_payoffs_with_twists_for_chapter = AsyncMock(return_value=[])
    service.twists.list_active_plants_for_context = AsyncMock(
        return_value=[(plant, twist, chapter)]
    )

    from app.repositories.prose import ProseRepository

    prose_repo = ProseRepository(session)
    prose_row = MagicMock(content="red herring prose")
    prose_repo.get_latest = AsyncMock(return_value=prose_row)
    session.scalar = AsyncMock(return_value=prose_row)

    result = await service.build_context_pack(
        project,
        CraftContextPackRequest(chapter_id=chapter_id, chapter_number=5),
    )
    assert result.craft_pack_id == MYSTERY_FAIR_PLAY_V1_ID
    assert len(result.craft_beats) >= 1
    assert result.meta["canon_secrets_stripped"] is True
    assert "secret_truth" not in result.model_dump_json()


@pytest.mark.unit
async def test_build_craft_context_pack_chapter_mismatch() -> None:
    service = CraftContextPackService(AsyncMock())
    project = MagicMock(id=uuid.uuid4())
    chapter = MagicMock(number=9)
    service.chapters.get = AsyncMock(return_value=chapter)
    with pytest.raises(NotFoundError):
        await service.build_context_pack(
            project,
            CraftContextPackRequest(chapter_id=uuid.uuid4(), chapter_number=1),
        )


@pytest.mark.unit
async def test_build_craft_context_pack_no_active_binding() -> None:
    service = CraftContextPackService(AsyncMock())
    project = MagicMock(id=uuid.uuid4())
    chapter = MagicMock(number=1)
    service.chapters.get = AsyncMock(return_value=chapter)
    service.craft.get_active_binding = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.build_context_pack(
            project,
            CraftContextPackRequest(chapter_id=uuid.uuid4(), chapter_number=1),
        )
