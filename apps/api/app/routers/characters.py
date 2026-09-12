"""Character routes."""

from fastapi import APIRouter, Query

from app.deps import DbSession, ProjectAccess
from app.schemas.character import CharacterListResponse
from app.services.character import CharacterService
from app.utils.pagination import clamp_page_params

router = APIRouter(prefix="/projects/{project_id}/characters", tags=["Characters"])


@router.get("", response_model=CharacterListResponse)
async def list_characters(
    project: ProjectAccess,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> CharacterListResponse:
    service = CharacterService(session)
    page_params = clamp_page_params(page, page_size)
    return await service.list_characters(project, page_params)
