"""Scene engine routes."""

from fastapi import APIRouter

from app.deps import DbSession, ProjectAccess
from app.schemas.scene_engine import (
    SceneEngineSettings,
    SceneEngineSettingsUpdateRequest,
)
from app.services.scene_engine import SceneEngineService

router = APIRouter(prefix="/projects/{project_id}/scene-engine", tags=["SceneEngine"])


@router.get("/settings", response_model=SceneEngineSettings)
async def get_scene_engine_settings(
    project: ProjectAccess,
    session: DbSession,
) -> SceneEngineSettings:
    return await SceneEngineService(session).get_settings(project)


@router.patch("/settings", response_model=SceneEngineSettings)
async def update_scene_engine_settings(
    payload: SceneEngineSettingsUpdateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> SceneEngineSettings:
    return await SceneEngineService(session).update_settings(project, payload)
