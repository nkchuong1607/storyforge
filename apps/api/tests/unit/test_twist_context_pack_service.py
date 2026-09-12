"""Twist context pack service unit tests."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import NotFoundError
from app.models.enums import PlantSalience, TwistPlanKind, TwistPlanStatus
from app.models.twist import TwistPlan, TwistPlant
from app.schemas.twist import TwistContextPackRequest
from app.services.twist_context_pack import TwistContextPackService


@pytest.mark.unit
async def test_build_context_pack_returns_plants_only() -> None:
    session = AsyncMock()
    service = TwistContextPackService(session)
    project_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    project = MagicMock(id=project_id)
    chapter = MagicMock(number=3)
    service.chapters.get = AsyncMock(return_value=chapter)
    now = datetime.now(UTC)
    twist = TwistPlan(
        id=uuid.uuid4(),
        project_id=project_id,
        title="Twist title",
        secret_truth="never exposed",
        status=TwistPlanStatus.planted,
        kind=TwistPlanKind.twist,
        constraints_json={},
        genre_strictness=None,
        created_by=uuid.uuid4(),
        created_at=now,
        updated_at=now,
    )
    plant = TwistPlant(
        id=uuid.uuid4(),
        project_id=project_id,
        twist_id=twist.id,
        chapter_id=chapter_id,
        salience=PlantSalience.soft,
        snippet="hint",
        sort_order=0,
        created_at=now,
        updated_at=now,
    )
    plant_chapter = MagicMock(number=2)
    service.twists.list_active_plants_for_context = AsyncMock(
        return_value=[(plant, twist, plant_chapter)]
    )

    result = await service.build_context_pack(
        project,
        TwistContextPackRequest(chapter_id=chapter_id, chapter_number=3),
    )
    assert len(result.twist_relevant) == 1
    assert result.meta["secret_truth_stripped"] is True
    assert result.twist_relevant[0].twist_title == "Twist title"


@pytest.mark.unit
async def test_build_context_pack_chapter_mismatch() -> None:
    service = TwistContextPackService(AsyncMock())
    project = MagicMock(id=uuid.uuid4())
    chapter = MagicMock(number=5)
    service.chapters.get = AsyncMock(return_value=chapter)
    with pytest.raises(NotFoundError):
        await service.build_context_pack(
            project,
            TwistContextPackRequest(chapter_id=uuid.uuid4(), chapter_number=3),
        )
