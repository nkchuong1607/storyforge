"""Project routes."""

from fastapi import APIRouter, Query, Response, status

from app.deps import CurrentUserId, DbSession, ProjectAccess
from app.models.enums import ProjectStatus
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectDetail,
    ProjectListResponse,
    ProjectUpdateRequest,
)
from app.services.project import ProjectService
from app.utils.pagination import clamp_page_params

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    session: DbSession,
    user_id: CurrentUserId,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: ProjectStatus | None = Query(default=ProjectStatus.active, alias="status"),
    q: str | None = Query(default=None),
) -> ProjectListResponse:
    service = ProjectService(session)
    page_params = clamp_page_params(page, page_size)
    return await service.list_projects(user_id, status=status_filter, query=q, page=page_params)


@router.post("", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreateRequest,
    session: DbSession,
    user_id: CurrentUserId,
) -> ProjectDetail:
    service = ProjectService(session)
    return await service.create_with_conflict_check(user_id, payload)


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(project: ProjectAccess, session: DbSession) -> ProjectDetail:
    service = ProjectService(session)
    return await service.get_project(project)


@router.patch("/{project_id}", response_model=ProjectDetail)
async def update_project(
    payload: ProjectUpdateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> ProjectDetail:
    service = ProjectService(session)
    return await service.update_project(project, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_project(project: ProjectAccess, session: DbSession) -> Response:
    service = ProjectService(session)
    await service.archive_project(project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
