"""Chapter routes."""

from fastapi import APIRouter, Query, status

from app.deps import DbSession, ProjectAccess
from app.schemas.chapter import Chapter, ChapterCreateRequest, ChapterListResponse
from app.services.chapter import ChapterService
from app.utils.pagination import clamp_page_params

router = APIRouter(prefix="/projects/{project_id}/chapters", tags=["Chapters"])


@router.get("", response_model=ChapterListResponse)
async def list_chapters(
    project: ProjectAccess,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ChapterListResponse:
    service = ChapterService(session)
    page_params = clamp_page_params(page, page_size)
    return await service.list_chapters(project, page_params)


@router.post("", response_model=Chapter, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    payload: ChapterCreateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> Chapter:
    service = ChapterService(session)
    return await service.create_chapter(project, payload)
