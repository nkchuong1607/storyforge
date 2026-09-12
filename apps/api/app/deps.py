"""FastAPI dependencies for auth and project ACL."""

import uuid
from typing import Annotated

from fastapi import Depends, Header, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.exceptions import NotFoundError, UnauthorizedError
from app.models.chapter import Chapter
from app.models.project import Project, ProjectMember
from app.models.twist import TwistPlan

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user_id(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
) -> uuid.UUID:
    if not x_user_id:
        raise UnauthorizedError()
    try:
        return uuid.UUID(x_user_id)
    except ValueError as exc:
        raise UnauthorizedError(message="X-User-Id must be a valid UUID") from exc


CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]


async def require_project_access(
    project_id: Annotated[uuid.UUID, Path(alias="project_id")],
    user_id: CurrentUserId,
    session: DbSession,
) -> Project:
    membership = await session.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    if membership is None:
        raise NotFoundError()
    project = await session.get(Project, project_id)
    if project is None:
        raise NotFoundError()
    return project


ProjectAccess = Annotated[Project, Depends(require_project_access)]


async def require_chapter_access(
    project: ProjectAccess,
    chapter_id: Annotated[uuid.UUID, Path(alias="chapter_id")],
    session: DbSession,
) -> Chapter:
    chapter = await session.scalar(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.project_id == project.id,
        )
    )
    if chapter is None:
        raise NotFoundError()
    return chapter


ChapterAccess = Annotated[Chapter, Depends(require_chapter_access)]


async def require_twist_access(
    project: ProjectAccess,
    twist_id: Annotated[uuid.UUID, Path(alias="twist_id")],
    session: DbSession,
) -> TwistPlan:
    twist = await session.scalar(
        select(TwistPlan).where(
            TwistPlan.id == twist_id,
            TwistPlan.project_id == project.id,
        )
    )
    if twist is None:
        raise NotFoundError()
    return twist


TwistAccess = Annotated[TwistPlan, Depends(require_twist_access)]
