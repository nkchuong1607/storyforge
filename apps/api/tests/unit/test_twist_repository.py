"""Twist repository unit tests with mocked session."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.enums import TwistPlanStatus
from app.models.twist import TwistPayoff, TwistPlan
from app.repositories.twist import TwistRepository
from app.utils.pagination import PageParams


@pytest.mark.unit
async def test_get_plan_returns_none() -> None:
    session = AsyncMock()
    session.scalar = AsyncMock(return_value=None)
    repo = TwistRepository(session)
    result = await repo.get_plan(uuid.uuid4(), uuid.uuid4())
    assert result is None


@pytest.mark.unit
async def test_count_plants() -> None:
    session = AsyncMock()
    session.scalar = AsyncMock(return_value=3)
    repo = TwistRepository(session)
    assert await repo.count_plants(uuid.uuid4()) == 3


@pytest.mark.unit
async def test_mark_payoffs_revealed() -> None:
    session = AsyncMock()
    payoff = MagicMock(spec=TwistPayoff)
    twist = MagicMock(spec=TwistPlan)
    twist.status = TwistPlanStatus.armed
    result_mock = MagicMock()
    result_mock.all.return_value = [(payoff, twist)]
    session.execute = AsyncMock(return_value=result_mock)
    session.flush = AsyncMock()
    repo = TwistRepository(session)
    count = await repo.mark_payoffs_revealed_for_chapter(uuid.uuid4(), uuid.uuid4(), MagicMock())
    assert count == 1
    assert twist.status == TwistPlanStatus.paid_off


@pytest.mark.unit
async def test_list_plans_pagination() -> None:
    session = AsyncMock()
    session.scalar = AsyncMock(return_value=1)
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    session.scalars = AsyncMock(return_value=scalars_mock)
    repo = TwistRepository(session)
    items, total = await repo.list_plans(uuid.uuid4(), PageParams(page=1, page_size=10))
    assert items == []
    assert total == 1
