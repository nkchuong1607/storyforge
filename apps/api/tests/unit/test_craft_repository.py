"""Unit tests for CraftPackRepository."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.craft_pack import ProjectCraftPack
from app.repositories.craft_pack import CraftPackRepository


@pytest.mark.asyncio
async def test_create_binding_flushes() -> None:
    session = AsyncMock()
    repo = CraftPackRepository(session)
    binding = ProjectCraftPack(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        craft_pack_id="mystery.fair_play.v1",
        active=True,
    )
    result = await repo.create_binding(binding)
    session.add.assert_called_once_with(binding)
    session.flush.assert_awaited_once()
    assert result is binding


@pytest.mark.asyncio
async def test_deactivate_all_executes_update() -> None:
    session = AsyncMock()
    repo = CraftPackRepository(session)
    session.execute = AsyncMock()
    await repo.deactivate_all(uuid.uuid4())
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_catalog_scalars() -> None:
    session = AsyncMock()
    repo = CraftPackRepository(session)
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    session.scalars = AsyncMock(return_value=mock_scalars)
    rows = await repo.list_catalog()
    assert rows == []
