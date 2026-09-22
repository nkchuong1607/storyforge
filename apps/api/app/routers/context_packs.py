"""Context pack routes."""

from fastapi import APIRouter

from app.deps import DbSession, ProjectAccess
from app.schemas.character import CharacterContextPackRequest, CharacterContextPackResponse
from app.schemas.craft_pack import CraftContextPackRequest, CraftContextPackResponse
from app.schemas.psychology import PsychContextPackRequest, PsychContextPackResponse
from app.schemas.relationship import (
    RelationshipContextPackRequest,
    RelationshipContextPackResponse,
)
from app.schemas.scene_engine import SceneContextPackRequest, SceneContextPackResponse
from app.schemas.stakes import StakesContextPackRequest, StakesContextPackResponse
from app.schemas.twist import TwistContextPackRequest, TwistContextPackResponse
from app.services.context_pack import CharacterContextPackService
from app.services.craft_context_pack import CraftContextPackService
from app.services.psych_context_pack import PsychContextPackService
from app.services.relationship_context_pack import RelationshipContextPackService
from app.services.scene_context_pack import SceneContextPackService
from app.services.stakes_context_pack import StakesContextPackService
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


@router.post("/scene", response_model=SceneContextPackResponse)
async def build_scene_context_pack(
    payload: SceneContextPackRequest,
    project: ProjectAccess,
    session: DbSession,
) -> SceneContextPackResponse:
    service = SceneContextPackService(session)
    return await service.build_context_pack(project, payload)


@router.post("/relationships", response_model=RelationshipContextPackResponse)
async def build_relationships_context_pack(
    payload: RelationshipContextPackRequest,
    project: ProjectAccess,
    session: DbSession,
) -> RelationshipContextPackResponse:
    service = RelationshipContextPackService(session)
    return await service.build_context_pack(project, payload)


@router.post("/stakes", response_model=StakesContextPackResponse)
async def build_stakes_context_pack(
    payload: StakesContextPackRequest,
    project: ProjectAccess,
    session: DbSession,
) -> StakesContextPackResponse:
    service = StakesContextPackService(session)
    return await service.build_context_pack(project, payload)


@router.post("/craft", response_model=CraftContextPackResponse)
async def build_craft_context_pack(
    payload: CraftContextPackRequest,
    project: ProjectAccess,
    session: DbSession,
) -> CraftContextPackResponse:
    service = CraftContextPackService(session)
    return await service.build_context_pack(project, payload)
