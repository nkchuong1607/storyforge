"""Unit tests for CraftPackService."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import CraftPackGenreIncompatibleError, NotFoundError
from app.models.craft_pack import CraftPack, ProjectCraftPack
from app.models.enums import GenreProfile
from app.models.project import Project
from app.services.craft_defaults import MYSTERY_FAIR_PLAY_V1_ID, mystery_fair_play_v1
from app.services.craft_pack import CraftPackService


def _project(profile: GenreProfile = GenreProfile.mystery) -> Project:
    return Project(
        id=uuid.uuid4(),
        title="Test",
        slug="test",
        genre_profile=profile,
        genre_rule_pack_json={},
    )


def _catalog_row() -> CraftPack:
    pack = mystery_fair_play_v1()
    return CraftPack(
        id=MYSTERY_FAIR_PLAY_V1_ID,
        schema_version=1,
        pack_json=pack,
        installed_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_list_catalog() -> None:
    session = AsyncMock()
    service = CraftPackService(session)
    row = _catalog_row()
    service.repo.list_catalog = AsyncMock(return_value=[row])
    result = await service.list_catalog()
    assert result.items[0].id == MYSTERY_FAIR_PLAY_V1_ID


@pytest.mark.asyncio
async def test_install_rejects_incompatible_genre() -> None:
    session = AsyncMock()
    service = CraftPackService(session)
    service.repo.get_catalog_pack = AsyncMock(return_value=_catalog_row())
    project = _project(GenreProfile.xianxia)
    with pytest.raises(CraftPackGenreIncompatibleError):
        await service.install(project, MYSTERY_FAIR_PLAY_V1_ID)


@pytest.mark.asyncio
async def test_install_idempotent_when_bound() -> None:
    session = AsyncMock()
    service = CraftPackService(session)
    catalog = _catalog_row()
    binding = ProjectCraftPack(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        craft_pack_id=MYSTERY_FAIR_PLAY_V1_ID,
        active=False,
        bound_at=datetime.now(UTC),
    )
    service.repo.get_catalog_pack = AsyncMock(return_value=catalog)
    service.repo.get_binding = AsyncMock(return_value=binding)
    result = await service.install(_project(), MYSTERY_FAIR_PLAY_V1_ID)
    assert result.craft_pack_id == MYSTERY_FAIR_PLAY_V1_ID


@pytest.mark.asyncio
async def test_activate_creates_binding_when_missing() -> None:
    session = AsyncMock()
    service = CraftPackService(session)
    project = _project()
    catalog = _catalog_row()
    service.repo.get_catalog_pack = AsyncMock(return_value=catalog)
    service.repo.get_binding = AsyncMock(return_value=None)
    service.repo.deactivate_all = AsyncMock()

    async def _create(binding: ProjectCraftPack) -> ProjectCraftPack:
        binding.id = uuid.uuid4()
        return binding

    service.repo.create_binding = AsyncMock(side_effect=_create)
    session.refresh = AsyncMock()
    session.flush = AsyncMock()
    result = await service.activate(project, MYSTERY_FAIR_PLAY_V1_ID)
    assert result.active is True


@pytest.mark.asyncio
async def test_deactivate_not_found() -> None:
    session = AsyncMock()
    service = CraftPackService(session)
    service.repo.get_binding = AsyncMock(return_value=None)
    service.repo.get_catalog_pack = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.deactivate(_project(), MYSTERY_FAIR_PLAY_V1_ID)


@pytest.mark.asyncio
async def test_get_catalog_pack_not_found() -> None:
    session = AsyncMock()
    service = CraftPackService(session)
    service.repo.get_catalog_pack = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.get_catalog_pack("missing.v1")


@pytest.mark.asyncio
async def test_get_project_bindings() -> None:
    session = AsyncMock()
    service = CraftPackService(session)
    project = _project()
    binding = ProjectCraftPack(
        id=uuid.uuid4(),
        project_id=project.id,
        craft_pack_id=MYSTERY_FAIR_PLAY_V1_ID,
        active=True,
        bound_at=datetime.now(UTC),
    )
    service.repo.list_bindings = AsyncMock(return_value=[binding])
    service.repo.get_catalog_pack = AsyncMock(return_value=_catalog_row())
    result = await service.get_project_bindings(project)
    assert result.active_pack_id == MYSTERY_FAIR_PLAY_V1_ID


@pytest.mark.asyncio
async def test_install_creates_binding() -> None:
    session = AsyncMock()
    service = CraftPackService(session)
    project = _project()
    catalog = _catalog_row()
    service.repo.get_catalog_pack = AsyncMock(return_value=catalog)
    service.repo.get_binding = AsyncMock(return_value=None)

    async def _create(binding: ProjectCraftPack) -> ProjectCraftPack:
        binding.id = uuid.uuid4()
        return binding

    service.repo.create_binding = AsyncMock(side_effect=_create)
    session.refresh = AsyncMock()
    result = await service.install(project, MYSTERY_FAIR_PLAY_V1_ID)
    assert result.craft_pack_id == MYSTERY_FAIR_PLAY_V1_ID


@pytest.mark.asyncio
async def test_deactivate_success() -> None:
    session = AsyncMock()
    service = CraftPackService(session)
    project = _project()
    binding = ProjectCraftPack(
        id=uuid.uuid4(),
        project_id=project.id,
        craft_pack_id=MYSTERY_FAIR_PLAY_V1_ID,
        active=True,
        bound_at=datetime.now(UTC),
    )
    service.repo.get_binding = AsyncMock(return_value=binding)
    service.repo.get_catalog_pack = AsyncMock(return_value=_catalog_row())
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    result = await service.deactivate(project, MYSTERY_FAIR_PLAY_V1_ID)
    assert result.active is False


@pytest.mark.asyncio
async def test_get_active_pack_json_none() -> None:
    session = AsyncMock()
    service = CraftPackService(session)
    service.repo.get_active_binding = AsyncMock(return_value=None)
    assert await service.get_active_pack_json(uuid.uuid4()) is None


@pytest.mark.asyncio
async def test_get_active_pack_json() -> None:
    session = AsyncMock()
    service = CraftPackService(session)
    project_id = uuid.uuid4()
    binding = MagicMock()
    binding.craft_pack_id = MYSTERY_FAIR_PLAY_V1_ID
    service.repo.get_active_binding = AsyncMock(return_value=binding)
    service.repo.get_catalog_pack = AsyncMock(return_value=_catalog_row())
    pack = await service.get_active_pack_json(project_id)
    assert pack is not None
    assert pack["id"] == MYSTERY_FAIR_PLAY_V1_ID
