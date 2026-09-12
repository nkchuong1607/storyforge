"""Dependency unit tests."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user_id, require_project_access
from app.exceptions import NotFoundError, UnauthorizedError
from app.models.enums import ProjectMemberRole, ProjectStatus
from app.models.project import Project, ProjectMember


@pytest.mark.unit
async def test_get_current_user_id_missing() -> None:
    with pytest.raises(UnauthorizedError):
        await get_current_user_id(None)


@pytest.mark.unit
async def test_get_current_user_id_invalid() -> None:
    with pytest.raises(UnauthorizedError):
        await get_current_user_id("not-a-uuid")


@pytest.mark.unit
async def test_get_current_user_id_valid() -> None:
    user_id = uuid.uuid4()
    result = await get_current_user_id(str(user_id))
    assert result == user_id


@pytest.mark.unit
async def test_require_project_access_denied(session: AsyncSession) -> None:
    project = Project(
        slug="test",
        title="Test",
        created_by=uuid.uuid4(),
        status=ProjectStatus.active,
    )
    session.add(project)
    await session.flush()

    with pytest.raises(NotFoundError):
        await require_project_access(project.id, uuid.uuid4(), session)


@pytest.mark.unit
async def test_require_project_access_granted(session: AsyncSession) -> None:
    user_id = uuid.uuid4()
    project = Project(
        slug="allowed",
        title="Allowed",
        created_by=user_id,
        status=ProjectStatus.active,
    )
    session.add(project)
    await session.flush()
    session.add(ProjectMember(project_id=project.id, user_id=user_id, role=ProjectMemberRole.owner))
    await session.flush()

    result = await require_project_access(project.id, user_id, session)
    assert result.id == project.id
