"""Series routes."""

import uuid

from fastapi import APIRouter, Query, Response, status

from app.deps import CurrentUserId, DbSession, ProjectAccess
from app.schemas.series import (
    ProjectInheritedSliceResponse,
    SeriesAttachProjectRequest,
    SeriesBibleSlice,
    SeriesCreateRequest,
    SeriesDetail,
    SeriesListResponse,
    SeriesOverrideCreateRequest,
    SeriesOverrideStagingEntry,
    SeriesProjectLink,
    SeriesUpdateRequest,
)
from app.services.series import SeriesService
from app.utils.pagination import PageParams

router = APIRouter(tags=["Series"])


@router.get("/series", response_model=SeriesListResponse)
async def list_series(
    user_id: CurrentUserId,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> SeriesListResponse:
    params = PageParams(page=page, page_size=page_size)
    return await SeriesService(session).list_series(user_id, params)


@router.post("/series", response_model=SeriesDetail, status_code=status.HTTP_201_CREATED)
async def create_series(
    payload: SeriesCreateRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> SeriesDetail:
    return await SeriesService(session).create_series(user_id, payload)


@router.get("/series/{series_id}", response_model=SeriesDetail)
async def get_series(
    series_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> SeriesDetail:
    return await SeriesService(session).get_series(user_id, series_id)


@router.patch("/series/{series_id}", response_model=SeriesDetail)
async def update_series(
    series_id: uuid.UUID,
    payload: SeriesUpdateRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> SeriesDetail:
    return await SeriesService(session).update_series(user_id, series_id, payload)


@router.get("/series/{series_id}/bible-slice", response_model=SeriesBibleSlice)
async def get_series_bible_slice(
    series_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> SeriesBibleSlice:
    return await SeriesService(session).get_bible_slice(user_id, series_id)


@router.post(
    "/series/{series_id}/projects",
    response_model=SeriesProjectLink,
    status_code=status.HTTP_201_CREATED,
)
async def attach_series_project(
    series_id: uuid.UUID,
    payload: SeriesAttachProjectRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> SeriesProjectLink:
    return await SeriesService(session).attach_project(user_id, series_id, payload)


@router.delete(
    "/series/{series_id}/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def detach_series_project(
    series_id: uuid.UUID,
    project_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> Response:
    await SeriesService(session).detach_project(user_id, series_id, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/projects/{project_id}/series/inherited-slice",
    response_model=ProjectInheritedSliceResponse,
)
async def get_project_inherited_slice(
    project: ProjectAccess,
    session: DbSession,
) -> ProjectInheritedSliceResponse:
    return await SeriesService(session).get_inherited_slice(project)


@router.post(
    "/projects/{project_id}/series/overrides",
    response_model=SeriesOverrideStagingEntry,
    status_code=status.HTTP_201_CREATED,
)
async def create_series_override(
    payload: SeriesOverrideCreateRequest,
    project: ProjectAccess,
    user_id: CurrentUserId,
    session: DbSession,
) -> SeriesOverrideStagingEntry:
    return await SeriesService(session).create_override(project, user_id, payload)
