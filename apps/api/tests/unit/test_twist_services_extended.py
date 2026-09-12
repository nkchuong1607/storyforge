"""Extended twist service unit tests for coverage."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import InvalidPlantReferenceError, NotFoundError
from app.models.enums import PlantSalience, TwistPlanStatus
from app.models.twist import TwistPayoff, TwistPlant
from app.schemas.twist import (
    TwistPayoffUpdateRequest,
    TwistPlantUpdateRequest,
    TwistPlanUpdateRequest,
)
from app.services.twist import TwistService
from tests.unit.test_twist_services import _project, _twist_model


@pytest.mark.unit
async def test_list_twists_with_audience() -> None:
    service = TwistService(AsyncMock())
    project = _project()
    twist = _twist_model(project.id)
    service.twists.list_plans = AsyncMock(return_value=([twist], 1))
    service.twists.count_plants = AsyncMock(return_value=0)
    service.twists.get_payoff = AsyncMock(return_value=None)
    from app.utils.pagination import PageParams

    result = await service.list_twists(project, PageParams(page=1, page_size=20))
    assert len(result.items) == 1


@pytest.mark.unit
async def test_update_twist_metadata() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id)
    service.twists.get_plan = AsyncMock(return_value=twist)
    service.twists.update_plan = AsyncMock(return_value=twist)
    service.twists.count_plants = AsyncMock(return_value=0)
    service.twists.get_payoff = AsyncMock(return_value=None)
    session.refresh = AsyncMock()

    result = await service.update_twist(
        project,
        twist.id,
        TwistPlanUpdateRequest(title="New title", secret_truth="New secret"),
    )
    assert result.title == "New title"


@pytest.mark.unit
async def test_update_plant_and_delete() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id, status=TwistPlanStatus.planted)
    chapter_id = uuid.uuid4()
    now = datetime.now(UTC)
    plant = TwistPlant(
        id=uuid.uuid4(),
        project_id=project.id,
        twist_id=twist.id,
        chapter_id=chapter_id,
        salience=PlantSalience.soft,
        snippet="old",
        sort_order=0,
        created_at=now,
        updated_at=now,
    )
    service.twists.get_plan = AsyncMock(return_value=twist)
    service.twists.get_plant = AsyncMock(return_value=plant)
    service.chapters.get = AsyncMock(return_value=MagicMock(status="drafting"))
    service.chapters.get_by_id = AsyncMock(return_value=MagicMock(number=2))
    session.refresh = AsyncMock()
    session.flush = AsyncMock()

    updated = await service.update_plant(
        project,
        twist.id,
        plant.id,
        TwistPlantUpdateRequest(snippet="new snippet"),
    )
    assert updated.snippet == "new snippet"

    service.twists.delete_plant = AsyncMock()
    await service.delete_plant(project, twist.id, plant.id)
    service.twists.delete_plant.assert_awaited_once()


@pytest.mark.unit
async def test_update_payoff_invalid_plant_ref() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id, status=TwistPlanStatus.armed)
    now = datetime.now(UTC)
    payoff = TwistPayoff(
        id=uuid.uuid4(),
        project_id=project.id,
        twist_id=twist.id,
        target_chapter_id=uuid.uuid4(),
        required_plant_ids=[],
        min_plants=1,
        created_at=now,
        updated_at=now,
    )
    service.twists.get_plan = AsyncMock(return_value=twist)
    service.twists.get_payoff_by_id = AsyncMock(return_value=payoff)
    service.twists.list_plants = AsyncMock(return_value=[])
    with pytest.raises(InvalidPlantReferenceError):
        await service.update_payoff(
            project,
            twist.id,
            payoff.id,
            TwistPayoffUpdateRequest(required_plant_ids=[uuid.uuid4()]),
        )


@pytest.mark.unit
async def test_get_payoff_not_found() -> None:
    service = TwistService(AsyncMock())
    project = _project()
    twist = _twist_model(project.id)
    service.twists.get_plan = AsyncMock(return_value=twist)
    service.twists.get_payoff = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.get_payoff(project, twist.id)


@pytest.mark.unit
async def test_board_armed_payoff_fairness() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id, status=TwistPlanStatus.armed)
    target_id = uuid.uuid4()
    now = datetime.now(UTC)
    payoff = TwistPayoff(
        id=uuid.uuid4(),
        project_id=project.id,
        twist_id=twist.id,
        target_chapter_id=target_id,
        required_plant_ids=[],
        min_plants=2,
        created_at=now,
        updated_at=now,
    )
    service.twists.list_all_plans = AsyncMock(return_value=[twist])
    service.twists.list_plants_for_project = AsyncMock(return_value=[])
    service.twists.get_payoff = AsyncMock(return_value=payoff)
    service.chapters.get_by_id = AsyncMock(return_value=MagicMock(number=10))

    board = await service.get_board(project)
    payoff_col = next(c for c in board.columns if c.id == "payoffs")
    assert payoff_col.cards[0].fairness is not None
    assert payoff_col.cards[0].fairness.state in {"fail", "warn"}


@pytest.mark.unit
async def test_delete_payoff() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id, status=TwistPlanStatus.armed)
    now = datetime.now(UTC)
    payoff = TwistPayoff(
        id=uuid.uuid4(),
        project_id=project.id,
        twist_id=twist.id,
        target_chapter_id=uuid.uuid4(),
        required_plant_ids=[],
        min_plants=1,
        created_at=now,
        updated_at=now,
    )
    service.twists.get_plan = AsyncMock(return_value=twist)
    service.twists.get_payoff_by_id = AsyncMock(return_value=payoff)
    service.twists.delete_payoff = AsyncMock()
    await service.delete_payoff(project, twist.id, payoff.id)
    service.twists.delete_payoff.assert_awaited_once()
