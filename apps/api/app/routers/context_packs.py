"""Context pack routes."""

from fastapi import APIRouter

from app.deps import DbSession, ProjectAccess
from app.schemas.character import CharacterContextPackRequest, CharacterContextPackResponse
from app.services.context_pack import CharacterContextPackService

router = APIRouter(prefix="/projects/{project_id}/context-packs", tags=["Context"])


@router.post("/characters", response_model=CharacterContextPackResponse)
async def build_character_context_pack(
    payload: CharacterContextPackRequest,
    project: ProjectAccess,
    session: DbSession,
) -> CharacterContextPackResponse:
    service = CharacterContextPackService(session)
    return await service.build_context_pack(project, payload)
