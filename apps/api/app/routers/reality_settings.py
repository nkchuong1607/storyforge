"""Project reality settings routes."""

from fastapi import APIRouter

from app.deps import DbSession, ProjectAccess
from app.schemas.reality_settings import (
    ProjectRealitySettings,
    ProjectRealitySettingsUpdate,
)
from app.services.reality_settings_service import RealitySettingsService

router = APIRouter(prefix="/projects/{project_id}", tags=["RealitySettings"])


@router.get("/reality-settings", response_model=ProjectRealitySettings)
async def get_project_reality_settings(
    project: ProjectAccess,
    session: DbSession,
) -> ProjectRealitySettings:
    return await RealitySettingsService(session).get_settings(project)


@router.patch("/reality-settings", response_model=ProjectRealitySettings)
async def update_project_reality_settings(
    payload: ProjectRealitySettingsUpdate,
    project: ProjectAccess,
    session: DbSession,
) -> ProjectRealitySettings:
    return await RealitySettingsService(session).update_settings(project, payload)
