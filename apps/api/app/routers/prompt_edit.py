"""Prompt edit routes."""

from fastapi import APIRouter, status

from app.deps import ChapterAccess, CurrentUserId, DbSession, ProjectAccess
from app.schemas.prompt_edit import (
    PromptEditApplyRequest,
    PromptEditApplyResponse,
    PromptEditInstructRequest,
    PromptEditInstructResponse,
    PromptEditRegenerateRequest,
    PromptEditSessionListResponse,
)
from app.services.prompt_edit import PromptEditService

router = APIRouter(
    prefix="/projects/{project_id}/chapters/{chapter_id}/prompt-edit",
    tags=["PromptEdit"],
)


@router.post(
    "/instruct",
    response_model=PromptEditInstructResponse,
    status_code=status.HTTP_201_CREATED,
)
async def prompt_edit_instruct(
    payload: PromptEditInstructRequest,
    project: ProjectAccess,
    chapter: ChapterAccess,
    user_id: CurrentUserId,
    session: DbSession,
) -> PromptEditInstructResponse:
    return await PromptEditService(session).instruct(project, chapter, user_id, payload)


@router.post(
    "/regenerate",
    response_model=PromptEditInstructResponse,
    status_code=status.HTTP_201_CREATED,
)
async def prompt_edit_regenerate(
    payload: PromptEditRegenerateRequest,
    project: ProjectAccess,
    chapter: ChapterAccess,
    user_id: CurrentUserId,
    session: DbSession,
) -> PromptEditInstructResponse:
    return await PromptEditService(session).regenerate(project, chapter, user_id, payload)


@router.post("/apply", response_model=PromptEditApplyResponse, status_code=status.HTTP_201_CREATED)
async def prompt_edit_apply(
    payload: PromptEditApplyRequest,
    project: ProjectAccess,
    chapter: ChapterAccess,
    user_id: CurrentUserId,
    session: DbSession,
) -> PromptEditApplyResponse:
    return await PromptEditService(session).apply(project, chapter, user_id, payload)


@router.get("/sessions", response_model=PromptEditSessionListResponse)
async def list_prompt_edit_sessions(
    project: ProjectAccess,
    chapter: ChapterAccess,
    session: DbSession,
) -> PromptEditSessionListResponse:
    return await PromptEditService(session).list_sessions(project, chapter)
