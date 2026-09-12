"""Bible staging and version routes."""

import uuid

from fastapi import APIRouter, Query, Response, status

from app.deps import CurrentUserId, DbSession, ProjectAccess
from app.models.enums import BibleSection
from app.schemas.bible import (
    BibleEntry,
    BibleEntryCreateRequest,
    BibleEntryListResponse,
    BibleEntryUpdateRequest,
    BibleVersionDetail,
    BibleVersionListResponse,
)
from app.services.bible import BibleService
from app.utils.pagination import clamp_page_params

router = APIRouter(prefix="/projects/{project_id}/bible", tags=["Bible"])


@router.get("/entries", response_model=BibleEntryListResponse)
async def list_bible_entries(
    project: ProjectAccess,
    session: DbSession,
    section: BibleSection | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> BibleEntryListResponse:
    service = BibleService(session)
    page_params = clamp_page_params(page, page_size)
    return await service.list_entries(project, section=section, page=page_params)


@router.post("/entries", response_model=BibleEntry, status_code=status.HTTP_201_CREATED)
async def create_bible_entry(
    payload: BibleEntryCreateRequest,
    project: ProjectAccess,
    session: DbSession,
    user_id: CurrentUserId,
) -> BibleEntry:
    service = BibleService(session)
    return await service.create_entry(project, user_id, payload)


@router.get("/entries/{entry_id}", response_model=BibleEntry)
async def get_bible_entry(
    entry_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> BibleEntry:
    service = BibleService(session)
    return await service.get_entry(project, entry_id)


@router.patch("/entries/{entry_id}", response_model=BibleEntry)
async def update_bible_entry(
    entry_id: uuid.UUID,
    payload: BibleEntryUpdateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> BibleEntry:
    service = BibleService(session)
    return await service.update_entry(project, entry_id, payload)


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bible_entry(
    entry_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> Response:
    service = BibleService(session)
    await service.delete_entry(project, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/versions", response_model=BibleVersionListResponse)
async def list_bible_versions(
    project: ProjectAccess,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> BibleVersionListResponse:
    service = BibleService(session)
    page_params = clamp_page_params(page, page_size)
    return await service.list_versions(project, page_params)


@router.get("/versions/{version}", response_model=BibleVersionDetail)
async def get_bible_version(
    version: int,
    project: ProjectAccess,
    session: DbSession,
) -> BibleVersionDetail:
    service = BibleService(session)
    return await service.get_version(project, version)


@router.post("/settle", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def settle_bible(project: ProjectAccess, session: DbSession) -> None:
    service = BibleService(session)
    await service.settle_stub()
