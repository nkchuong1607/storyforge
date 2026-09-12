"""Context pack routes."""

from fastapi import APIRouter

from app.deps import DbSession, ProjectAccess
from app.schemas.character import CharacterContextPackRequest, CharacterContextPackResponse
from app.schemas.psychology import PsychContextPackRequest, PsychContextPackResponse
from app.schemas.twist import TwistContextPackRequest, TwistContextPackResponse
from app.services.context_pack import CharacterContextPackService
from app.services.psych_context_pack import PsychContextPackService
from app.services.twist_context_pack import TwistContextPackService

router = APIRouter(prefix="/projects/{project_id}/context-packs", tags=["Context"])


@router.post("/characters", response_model=CharacterContextPackResponse)
async def build_character_context_pack(
    payload: CharacterContextPackRequest,
    project: ProjectAccess,
    session: DbSession,
) -> CharacterContextPackResponse:
    service = CharacterContextPackService(session)
    return await service.build_context_pack(project, payload)


@router.post("/twists", response_model=TwistContextPackResponse)
async def build_twist_context_pack(
    payload: TwistContextPackRequest,
    project: ProjectAccess,
    session: DbSession,
) -> TwistContextPackResponse:
    service = TwistContextPackService(session)
    return await service.build_context_pack(project, payload)


@router.post("/psych", response_model=PsychContextPackResponse)
async def build_psych_context_pack(
    payload: PsychContextPackRequest,
    project: ProjectAccess,
    session: DbSession,
) -> PsychContextPackResponse:
    service = PsychContextPackService(session)
    return await service.build_context_pack(project, payload)
