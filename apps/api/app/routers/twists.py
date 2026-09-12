"""TwistPlan routes."""

import uuid

from fastapi import APIRouter, Query, Response, status

from app.deps import CurrentUserId, DbSession, ProjectAccess, TwistAccess
from app.models.enums import ContextAudience, TwistPlanKind, TwistPlanStatus
from app.schemas.twist import (
    TwistBoardResponse,
    TwistPayoff,
    TwistPayoffCreateRequest,
    TwistPayoffUpdateRequest,
    TwistPlan,
    TwistPlanCreateRequest,
    TwistPlanListResponse,
    TwistPlant,
    TwistPlantCreateRequest,
    TwistPlantListResponse,
    TwistPlantUpdateRequest,
    TwistPlanUpdateRequest,
    TwistTransitionRequest,
)
from app.services.twist import TwistService
from app.utils.pagination import clamp_page_params

router = APIRouter(prefix="/projects/{project_id}/twists", tags=["Twists"])


@router.get("", response_model=TwistPlanListResponse)
async def list_twists(
    project: ProjectAccess,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    audience: ContextAudience = Query(default=ContextAudience.author),
    status: TwistPlanStatus | None = Query(default=None),
    kind: TwistPlanKind | None = Query(default=None),
    q: str | None = Query(default=None),
) -> TwistPlanListResponse:
    service = TwistService(session)
    page_params = clamp_page_params(page, page_size)
    return await service.list_twists(
        project, page_params, status=status, kind=kind, q=q, audience=audience
    )


@router.post("", response_model=TwistPlan, status_code=status.HTTP_201_CREATED)
async def create_twist(
    payload: TwistPlanCreateRequest,
    project: ProjectAccess,
    session: DbSession,
    user_id: CurrentUserId,
) -> TwistPlan:
    service = TwistService(session)
    return await service.create_twist(project, user_id, payload)


@router.get("/board", response_model=TwistBoardResponse)
async def get_twist_board(
    project: ProjectAccess,
    session: DbSession,
    kind: TwistPlanKind | None = Query(default=None),
    include_abandoned: bool = Query(default=False),
) -> TwistBoardResponse:
    service = TwistService(session)
    return await service.get_board(project, kind=kind, include_abandoned=include_abandoned)


@router.get("/{twist_id}", response_model=TwistPlan)
async def get_twist(
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
    audience: ContextAudience = Query(default=ContextAudience.author),
) -> TwistPlan:
    service = TwistService(session)
    return await service.get_twist(project, twist.id, audience=audience)


@router.patch("/{twist_id}", response_model=TwistPlan)
async def update_twist(
    payload: TwistPlanUpdateRequest,
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
) -> TwistPlan:
    service = TwistService(session)
    return await service.update_twist(project, twist.id, payload)


@router.delete("/{twist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def abandon_twist(
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
) -> Response:
    service = TwistService(session)
    await service.abandon_twist(project, twist.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{twist_id}/transition", response_model=TwistPlan)
async def transition_twist(
    payload: TwistTransitionRequest,
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
) -> TwistPlan:
    service = TwistService(session)
    return await service.transition_twist(project, twist.id, payload)


@router.get("/{twist_id}/plants", response_model=TwistPlantListResponse)
async def list_twist_plants(
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
) -> TwistPlantListResponse:
    service = TwistService(session)
    return await service.list_plants(project, twist.id)


@router.post("/{twist_id}/plants", response_model=TwistPlant, status_code=status.HTTP_201_CREATED)
async def create_twist_plant(
    payload: TwistPlantCreateRequest,
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
) -> TwistPlant:
    service = TwistService(session)
    return await service.create_plant(project, twist.id, payload)


@router.patch("/{twist_id}/plants/{plant_id}", response_model=TwistPlant)
async def update_twist_plant(
    payload: TwistPlantUpdateRequest,
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
    plant_id: uuid.UUID,
) -> TwistPlant:
    service = TwistService(session)
    return await service.update_plant(project, twist.id, plant_id, payload)


@router.delete("/{twist_id}/plants/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_twist_plant(
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
    plant_id: uuid.UUID,
) -> Response:
    service = TwistService(session)
    await service.delete_plant(project, twist.id, plant_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{twist_id}/payoffs", response_model=TwistPayoff)
async def get_twist_payoff(
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
) -> TwistPayoff:
    service = TwistService(session)
    return await service.get_payoff(project, twist.id)


@router.post("/{twist_id}/payoffs", response_model=TwistPayoff, status_code=status.HTTP_201_CREATED)
async def create_twist_payoff(
    payload: TwistPayoffCreateRequest,
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
) -> TwistPayoff:
    service = TwistService(session)
    return await service.create_payoff(project, twist.id, payload)


@router.patch("/{twist_id}/payoffs/{payoff_id}", response_model=TwistPayoff)
async def update_twist_payoff(
    payload: TwistPayoffUpdateRequest,
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
    payoff_id: uuid.UUID,
) -> TwistPayoff:
    service = TwistService(session)
    return await service.update_payoff(project, twist.id, payoff_id, payload)


@router.delete("/{twist_id}/payoffs/{payoff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_twist_payoff(
    twist: TwistAccess,
    project: ProjectAccess,
    session: DbSession,
    payoff_id: uuid.UUID,
) -> Response:
    service = TwistService(session)
    await service.delete_payoff(project, twist.id, payoff_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
