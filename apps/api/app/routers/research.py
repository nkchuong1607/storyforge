"""Research notes routes."""

import uuid

from fastapi import APIRouter, Query, Response, status

from app.deps import CurrentUserId, DbSession, ProjectAccess
from app.models.enums import ResearchNoteStatus
from app.schemas.research import (
    ResearchNote,
    ResearchNoteCreateRequest,
    ResearchNoteDetail,
    ResearchNoteLink,
    ResearchNoteLinkCreateRequest,
    ResearchNoteListResponse,
    ResearchNoteSearchResponse,
    ResearchNoteUpdateRequest,
    ResearchPromoteRequest,
    ResearchPromoteResponse,
)
from app.services.research import ResearchService
from app.utils.pagination import PageParams

router = APIRouter(prefix="/projects/{project_id}/research", tags=["Research"])


@router.get("/notes", response_model=ResearchNoteListResponse)
async def list_research_notes(
    project: ProjectAccess,
    session: DbSession,
    status: ResearchNoteStatus | None = None,
    tag: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ResearchNoteListResponse:
    params = PageParams(page=page, page_size=page_size)
    return await ResearchService(session).list_notes(project, status=status, tag=tag, page=params)


@router.post("/notes", response_model=ResearchNote, status_code=status.HTTP_201_CREATED)
async def create_research_note(
    payload: ResearchNoteCreateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> ResearchNote:
    return await ResearchService(session).create_note(project, payload)


@router.get("/notes/search", response_model=ResearchNoteSearchResponse)
async def search_research_notes(
    project: ProjectAccess,
    session: DbSession,
    q: str = Query(min_length=1),
    tag: str | None = None,
    status: ResearchNoteStatus | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ResearchNoteSearchResponse:
    params = PageParams(page=page, page_size=page_size)
    return await ResearchService(session).search_notes(
        project, query=q, status=status, tag=tag, page=params
    )


@router.get("/notes/{note_id}", response_model=ResearchNoteDetail)
async def get_research_note(
    note_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> ResearchNoteDetail:
    return await ResearchService(session).get_note(project, note_id)


@router.patch("/notes/{note_id}", response_model=ResearchNote)
async def update_research_note(
    note_id: uuid.UUID,
    payload: ResearchNoteUpdateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> ResearchNote:
    return await ResearchService(session).update_note(project, note_id, payload)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_research_note(
    note_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> Response:
    await ResearchService(session).archive_note(project, note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/notes/{note_id}/links",
    response_model=ResearchNoteLink,
    status_code=status.HTTP_201_CREATED,
)
async def add_research_note_link(
    note_id: uuid.UUID,
    payload: ResearchNoteLinkCreateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> ResearchNoteLink:
    return await ResearchService(session).add_link(project, note_id, payload)


@router.delete(
    "/notes/{note_id}/links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_research_note_link(
    note_id: uuid.UUID,
    link_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> Response:
    await ResearchService(session).remove_link(project, note_id, link_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/notes/{note_id}/promote", response_model=ResearchPromoteResponse)
async def promote_research_note(
    note_id: uuid.UUID,
    payload: ResearchPromoteRequest,
    project: ProjectAccess,
    user_id: CurrentUserId,
    session: DbSession,
) -> ResearchPromoteResponse:
    return await ResearchService(session).promote_note(project, user_id, note_id, payload)
