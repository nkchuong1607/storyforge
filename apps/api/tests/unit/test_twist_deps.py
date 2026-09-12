"""Twist access dependency unit tests."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.deps import require_twist_access
from app.exceptions import NotFoundError
from app.models.twist import TwistPlan


@pytest.mark.unit
async def test_require_twist_access_not_found() -> None:
    session = AsyncMock()
    session.scalar = AsyncMock(return_value=None)
    project = MagicMock(id=uuid.uuid4())
    with pytest.raises(NotFoundError):
        await require_twist_access(project, uuid.uuid4(), session)


@pytest.mark.unit
async def test_require_twist_access_granted() -> None:
    session = AsyncMock()
    twist_id = uuid.uuid4()
    twist = MagicMock(spec=TwistPlan, id=twist_id)
    session.scalar = AsyncMock(return_value=twist)
    project = MagicMock(id=uuid.uuid4())
    result = await require_twist_access(project, twist_id, session)
    assert result.id == twist_id
