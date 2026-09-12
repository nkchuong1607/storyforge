"""Character routes."""

import uuid

from fastapi import APIRouter, Query, status

from app.deps import CurrentUserId, DbSession, ProjectAccess
from app.models.enums import CharacterStatus, ProvisionalStatus
from app.schemas.character import (
    Character,
    CharacterCreateRequest,
    CharacterListResponse,
    CharacterPromoteTierRequest,
    CharacterProvisional,
    CharacterProvisionalListResponse,
    CharacterProvisionalMergeRequest,
    CharacterProvisionalMergeResponse,
    CharacterProvisionalRejectRequest,
    CharacterSearchResponse,
    CharacterUpdateRequest,
)
from app.services.character import CharacterService
from app.services.provisional import ProvisionalService
from app.utils.pagination import clamp_page_params

router = APIRouter(prefix="/projects/{project_id}/characters", tags=["Characters"])


@router.get("", response_model=CharacterListResponse)
async def list_characters(
    project: ProjectAccess,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    tier: int | None = Query(default=None, ge=0, le=3),
    status: CharacterStatus | None = Query(default=None),
    q: str | None = Query(default=None),
) -> CharacterListResponse:
    service = CharacterService(session)
    page_params = clamp_page_params(page, page_size)
    return await service.list_characters(project, page_params, tier=tier, status=status, q=q)


@router.post("", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_character(
    payload: CharacterCreateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> Character:
    service = CharacterService(session)
    return await service.create_character(project, payload)


@router.get("/search", response_model=CharacterSearchResponse)
async def search_characters(
    project: ProjectAccess,
    session: DbSession,
    q: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=50),
    search_mode: str = Query(default="keyword"),
) -> CharacterSearchResponse:
    service = CharacterService(session)
    return await service.search_characters(project, q, limit=limit, search_mode=search_mode)


@router.get("/provisionals", response_model=CharacterProvisionalListResponse)
async def list_provisionals(
    project: ProjectAccess,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: ProvisionalStatus | None = Query(default=ProvisionalStatus.pending),
    chapter_id: uuid.UUID | None = Query(default=None),
) -> CharacterProvisionalListResponse:
    service = ProvisionalService(session)
    page_params = clamp_page_params(page, page_size)
    return await service.list_provisionals(
        project, page_params, status=status, chapter_id=chapter_id
    )


@router.get("/provisionals/{provisional_id}", response_model=CharacterProvisional)
async def get_provisional(
    project: ProjectAccess,
    provisional_id: uuid.UUID,
    session: DbSession,
) -> CharacterProvisional:
    service = ProvisionalService(session)
    return await service.get_provisional(project, provisional_id)


@router.post(
    "/provisionals/{provisional_id}/merge",
    response_model=CharacterProvisionalMergeResponse,
)
async def merge_provisional(
    payload: CharacterProvisionalMergeRequest,
    project: ProjectAccess,
    provisional_id: uuid.UUID,
    session: DbSession,
    user_id: CurrentUserId,
) -> CharacterProvisionalMergeResponse:
    service = ProvisionalService(session)
    return await service.merge_provisional(project, provisional_id, payload, user_id)


@router.post("/provisionals/{provisional_id}/reject", response_model=CharacterProvisional)
async def reject_provisional(
    project: ProjectAccess,
    provisional_id: uuid.UUID,
    session: DbSession,
    user_id: CurrentUserId,
    payload: CharacterProvisionalRejectRequest | None = None,
) -> CharacterProvisional:
    service = ProvisionalService(session)
    return await service.reject_provisional(project, provisional_id, payload, user_id)


@router.get("/{character_id}", response_model=Character)
async def get_character(
    project: ProjectAccess,
    character_id: uuid.UUID,
    session: DbSession,
) -> Character:
    service = CharacterService(session)
    return await service.get_character(project, character_id)


@router.patch("/{character_id}", response_model=Character)
async def update_character(
    payload: CharacterUpdateRequest,
    project: ProjectAccess,
    character_id: uuid.UUID,
    session: DbSession,
) -> Character:
    service = CharacterService(session)
    return await service.update_character(project, character_id, payload)


@router.post("/{character_id}/promote-tier", response_model=Character)
async def promote_character_tier(
    project: ProjectAccess,
    character_id: uuid.UUID,
    session: DbSession,
    payload: CharacterPromoteTierRequest | None = None,
) -> Character:
    service = CharacterService(session)
    return await service.promote_tier(project, character_id, payload)
