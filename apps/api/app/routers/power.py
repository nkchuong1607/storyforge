"""Power system routes."""

import uuid

from fastapi import APIRouter, Response, status

from app.deps import DbSession, ProjectAccess
from app.schemas.power import (
    PowerRank,
    PowerRankCreateRequest,
    PowerRankListResponse,
    PowerRankReorderRequest,
    PowerRankUpdateRequest,
    PowerSystemSettings,
    PowerSystemSettingsUpdate,
    PowerTechnique,
    PowerTechniqueCreateRequest,
    PowerTechniqueListResponse,
    PowerTechniqueUpdateRequest,
)
from app.services.power import PowerService

router = APIRouter(prefix="/projects/{project_id}/power-system", tags=["PowerSystem"])


@router.get("/settings", response_model=PowerSystemSettings)
async def get_power_system_settings(
    project: ProjectAccess,
    session: DbSession,
) -> PowerSystemSettings:
    return await PowerService(session).get_settings(project)


@router.patch("/settings", response_model=PowerSystemSettings)
async def update_power_system_settings(
    payload: PowerSystemSettingsUpdate,
    project: ProjectAccess,
    session: DbSession,
) -> PowerSystemSettings:
    return await PowerService(session).update_settings(project, payload)


@router.get("/ranks", response_model=PowerRankListResponse)
async def list_power_ranks(
    project: ProjectAccess,
    session: DbSession,
) -> PowerRankListResponse:
    return await PowerService(session).list_ranks(project)


@router.post("/ranks", response_model=PowerRank, status_code=status.HTTP_201_CREATED)
async def create_power_rank(
    payload: PowerRankCreateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> PowerRank:
    return await PowerService(session).create_rank(project, payload)


@router.put("/ranks/reorder", response_model=PowerRankListResponse)
async def reorder_power_ranks(
    payload: PowerRankReorderRequest,
    project: ProjectAccess,
    session: DbSession,
) -> PowerRankListResponse:
    return await PowerService(session).reorder_ranks(project, payload)


@router.patch("/ranks/{rank_id}", response_model=PowerRank)
async def update_power_rank(
    payload: PowerRankUpdateRequest,
    project: ProjectAccess,
    session: DbSession,
    rank_id: uuid.UUID,
) -> PowerRank:
    return await PowerService(session).update_rank(project, rank_id, payload)


@router.delete("/ranks/{rank_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_power_rank(
    project: ProjectAccess,
    session: DbSession,
    rank_id: uuid.UUID,
) -> Response:
    await PowerService(session).delete_rank(project, rank_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/techniques", response_model=PowerTechniqueListResponse)
async def list_power_techniques(
    project: ProjectAccess,
    session: DbSession,
) -> PowerTechniqueListResponse:
    return await PowerService(session).list_techniques(project)


@router.post("/techniques", response_model=PowerTechnique, status_code=status.HTTP_201_CREATED)
async def create_power_technique(
    payload: PowerTechniqueCreateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> PowerTechnique:
    return await PowerService(session).create_technique(project, payload)


@router.patch("/techniques/{technique_id}", response_model=PowerTechnique)
async def update_power_technique(
    payload: PowerTechniqueUpdateRequest,
    project: ProjectAccess,
    session: DbSession,
    technique_id: uuid.UUID,
) -> PowerTechnique:
    return await PowerService(session).update_technique(project, technique_id, payload)


@router.delete("/techniques/{technique_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_power_technique(
    project: ProjectAccess,
    session: DbSession,
    technique_id: uuid.UUID,
) -> Response:
    await PowerService(session).delete_technique(project, technique_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
