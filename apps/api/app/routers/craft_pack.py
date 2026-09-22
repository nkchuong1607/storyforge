"""CraftPack catalog and project binding routes."""

from fastapi import APIRouter

from app.deps import DbSession, ProjectAccess
from app.schemas.craft_pack import (
    CraftPackDetail,
    CraftPackListResponse,
    ProjectCraftPackBinding,
    ProjectCraftPackResponse,
)
from app.services.craft_pack import CraftPackService

router = APIRouter(tags=["CraftPacks"])


@router.get("/craft-packs", response_model=CraftPackListResponse)
async def list_craft_packs(session: DbSession) -> CraftPackListResponse:
    return await CraftPackService(session).list_catalog()


@router.get("/craft-packs/{craft_pack_id}", response_model=CraftPackDetail)
async def get_craft_pack(craft_pack_id: str, session: DbSession) -> CraftPackDetail:
    return await CraftPackService(session).get_catalog_pack(craft_pack_id)


project_router = APIRouter(prefix="/projects/{project_id}/craft-packs", tags=["CraftPacks"])


@project_router.get("", response_model=ProjectCraftPackResponse)
async def get_project_craft_packs(
    project: ProjectAccess,
    session: DbSession,
) -> ProjectCraftPackResponse:
    return await CraftPackService(session).get_project_bindings(project)


@project_router.post("/{craft_pack_id}/install", response_model=ProjectCraftPackBinding)
async def install_craft_pack(
    craft_pack_id: str,
    project: ProjectAccess,
    session: DbSession,
) -> ProjectCraftPackBinding:
    return await CraftPackService(session).install(project, craft_pack_id)


@project_router.post("/{craft_pack_id}/activate", response_model=ProjectCraftPackBinding)
async def activate_craft_pack(
    craft_pack_id: str,
    project: ProjectAccess,
    session: DbSession,
) -> ProjectCraftPackBinding:
    return await CraftPackService(session).activate(project, craft_pack_id)


@project_router.post("/{craft_pack_id}/deactivate", response_model=ProjectCraftPackBinding)
async def deactivate_craft_pack(
    craft_pack_id: str,
    project: ProjectAccess,
    session: DbSession,
) -> ProjectCraftPackBinding:
    return await CraftPackService(session).deactivate(project, craft_pack_id)
