"""Twist service unit tests with mocked repositories."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import PayoffAlreadyExistsError, TwistPaidOffImmutableError
from app.models.enums import (
    ContextAudience,
    GenreProfile,
    PlantSalience,
    TwistPlanKind,
    TwistPlanStatus,
)
from app.models.project import Project
from app.models.twist import TwistPayoff, TwistPlan, TwistPlant
from app.schemas.twist import (
    TwistPayoffCreateRequest,
    TwistPlanCreateRequest,
    TwistPlantCreateRequest,
    TwistTransitionRequest,
)
from app.services.twist import TwistService


def _project(**kwargs) -> Project:
    defaults = {
        "id": uuid.uuid4(),
        "slug": "test",
        "title": "Test",
        "created_by": uuid.uuid4(),
        "genre_profile": GenreProfile.xianxia,
    }
    defaults.update(kwargs)
    project = Project(**{k: v for k, v in defaults.items() if k != "genre_profile"})
    project.genre_profile = defaults["genre_profile"]
    return project


def _twist_model(project_id: uuid.UUID, **kwargs) -> TwistPlan:
    now = datetime.now(UTC)
    defaults = {
        "id": uuid.uuid4(),
        "project_id": project_id,
        "title": "Twist",
        "secret_truth": "Secret",
        "status": TwistPlanStatus.seeded,
        "kind": TwistPlanKind.twist,
        "misdirection": None,
        "constraints_json": {},
        "genre_strictness": None,
        "created_by": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return TwistPlan(**defaults)


@pytest.mark.unit
async def test_create_twist_seeded_status() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    created_twist = _twist_model(project.id, title="T", secret_truth="S")
    service.twists.create_plan = AsyncMock(return_value=created_twist)
    service.twists.count_plants = AsyncMock(return_value=0)
    service.twists.get_payoff = AsyncMock(return_value=None)
    session.refresh = AsyncMock()
    result = await service.create_twist(
        project,
        uuid.uuid4(),
        TwistPlanCreateRequest(title="T", secret_truth="S"),
    )
    assert result.status == TwistPlanStatus.seeded
    assert result.secret_truth == "S"


@pytest.mark.unit
async def test_writer_audience_strips_on_get() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id, misdirection="trail")
    service.twists.get_plan = AsyncMock(return_value=twist)
    service.twists.count_plants = AsyncMock(return_value=0)
    service.twists.get_payoff = AsyncMock(return_value=None)

    result = await service.get_twist(project, twist.id, audience=ContextAudience.writer)
    assert result.secret_truth is None
    assert result.misdirection is None


@pytest.mark.unit
async def test_abandon_paid_off_raises() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id, status=TwistPlanStatus.paid_off)
    service.twists.get_plan = AsyncMock(return_value=twist)
    with pytest.raises(TwistPaidOffImmutableError):
        await service.abandon_twist(project, twist.id)


@pytest.mark.unit
async def test_create_payoff_duplicate_raises() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id)
    service.twists.get_plan = AsyncMock(return_value=twist)
    service.twists.get_payoff = AsyncMock(return_value=MagicMock())
    with pytest.raises(PayoffAlreadyExistsError):
        await service.create_payoff(
            project,
            twist.id,
            TwistPayoffCreateRequest(target_chapter_id=uuid.uuid4()),
        )


@pytest.mark.unit
async def test_transition_twist_abandoned() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id, status=TwistPlanStatus.planted)
    service.twists.get_plan = AsyncMock(return_value=twist)
    service.twists.update_plan = AsyncMock(return_value=twist)
    service.twists.count_plants = AsyncMock(return_value=1)
    service.twists.get_payoff = AsyncMock(return_value=None)
    session.refresh = AsyncMock()

    result = await service.transition_twist(
        project,
        twist.id,
        TwistTransitionRequest(status=TwistPlanStatus.abandoned),
    )
    assert result.status == TwistPlanStatus.abandoned


@pytest.mark.unit
async def test_board_columns_structure() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id, status=TwistPlanStatus.seeded)
    plant = TwistPlant(
        id=uuid.uuid4(),
        project_id=project.id,
        twist_id=twist.id,
        chapter_id=uuid.uuid4(),
        salience="soft",
        snippet="hint",
        sort_order=0,
    )
    service.twists.list_all_plans = AsyncMock(return_value=[twist])
    service.twists.list_plants_for_project = AsyncMock(return_value=[plant])
    service.chapters.get_by_id = AsyncMock(return_value=MagicMock(number=1))
    service.twists.get_payoff = AsyncMock(return_value=None)

    board = await service.get_board(project)
    assert len(board.columns) == 4
    assert board.columns[0].id == "secrets"
    assert board.columns[0].cards[0].card_type == "twist"


@pytest.mark.unit
async def test_create_plant_updates_status() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id, status=TwistPlanStatus.seeded)
    chapter_id = uuid.uuid4()
    now = datetime.now(UTC)
    plant = TwistPlant(
        id=uuid.uuid4(),
        project_id=project.id,
        twist_id=twist.id,
        chapter_id=chapter_id,
        salience=PlantSalience.hard,
        snippet="x",
        sort_order=0,
        created_at=now,
        updated_at=now,
    )
    service.twists.get_plan = AsyncMock(return_value=twist)
    service.chapters.get = AsyncMock(return_value=MagicMock(status="drafting"))
    service.chapters.get_by_id = AsyncMock(return_value=MagicMock(number=1))
    service.twists.create_plant = AsyncMock(return_value=plant)
    service.twists.update_plan = AsyncMock(return_value=twist)
    session.refresh = AsyncMock()

    result = await service.create_plant(
        project,
        twist.id,
        TwistPlantCreateRequest(chapter_id=chapter_id, salience="hard", snippet="x"),
    )
    assert result.chapter_number == 1
    assert twist.status == TwistPlanStatus.planted


@pytest.mark.unit
async def test_create_payoff_arms_twist() -> None:
    session = AsyncMock()
    service = TwistService(session)
    project = _project()
    twist = _twist_model(project.id, status=TwistPlanStatus.planted)
    target_id = uuid.uuid4()
    now = datetime.now(UTC)
    payoff = TwistPayoff(
        id=uuid.uuid4(),
        project_id=project.id,
        twist_id=twist.id,
        target_chapter_id=target_id,
        required_plant_ids=[],
        min_plants=1,
        created_at=now,
        updated_at=now,
    )
    service.twists.get_plan = AsyncMock(return_value=twist)
    service.twists.get_payoff = AsyncMock(return_value=None)
    service.chapters.get = AsyncMock(return_value=MagicMock(status="drafting"))
    service.chapters.get_by_id = AsyncMock(return_value=MagicMock(number=5))
    service.twists.create_payoff = AsyncMock(return_value=payoff)
    service.twists.update_plan = AsyncMock(return_value=twist)
    session.refresh = AsyncMock()

    await service.create_payoff(
        project,
        twist.id,
        TwistPayoffCreateRequest(target_chapter_id=target_id),
    )
    assert twist.status == TwistPlanStatus.armed
