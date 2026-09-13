"""Stakes ledger routes."""

import uuid

from fastapi import APIRouter, Response, status

from app.deps import DbSession, ProjectAccess
from app.schemas.stakes import (
    ActStructureSettings,
    ActStructureSettingsUpdateRequest,
    StakesBoardResponse,
    StakesEntryCreateRequest,
    StakesEntryListResponse,
    StakesEntryUpdateRequest,
    StakesLedgerEntry,
)
from app.services.stakes import StakesService

router = APIRouter(prefix="/projects/{project_id}/stakes", tags=["Stakes"])


@router.get("/settings", response_model=ActStructureSettings)
async def get_stakes_settings(
    project: ProjectAccess,
    session: DbSession,
) -> ActStructureSettings:
    return await StakesService(session).get_settings(project)


@router.patch("/settings", response_model=ActStructureSettings)
async def update_stakes_settings(
    payload: ActStructureSettingsUpdateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> ActStructureSettings:
    return await StakesService(session).update_settings(project, payload)


@router.get("/entries", response_model=StakesEntryListResponse)
async def list_stakes_entries(
    project: ProjectAccess,
    session: DbSession,
) -> StakesEntryListResponse:
    return await StakesService(session).list_entries(project)


@router.post("/entries", response_model=StakesLedgerEntry, status_code=status.HTTP_201_CREATED)
async def create_stakes_entry(
    payload: StakesEntryCreateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> StakesLedgerEntry:
    return await StakesService(session).create_entry(project, payload)


@router.get("/entries/{entry_id}", response_model=StakesLedgerEntry)
async def get_stakes_entry(
    entry_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> StakesLedgerEntry:
    return await StakesService(session).get_entry(project, entry_id)


@router.patch("/entries/{entry_id}", response_model=StakesLedgerEntry)
async def update_stakes_entry(
    entry_id: uuid.UUID,
    payload: StakesEntryUpdateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> StakesLedgerEntry:
    return await StakesService(session).update_entry(project, entry_id, payload)


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stakes_entry(
    entry_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> Response:
    await StakesService(session).delete_entry(project, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/board", response_model=StakesBoardResponse)
async def get_stakes_board(
    project: ProjectAccess,
    session: DbSession,
) -> StakesBoardResponse:
    return await StakesService(session).get_board(project)
