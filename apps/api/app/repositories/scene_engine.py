"""Scene engine settings data access."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scene_engine_settings import SceneEngineSettings


class SceneEngineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_settings(self, project_id: uuid.UUID) -> SceneEngineSettings | None:
        return await self.session.get(SceneEngineSettings, project_id)

    async def ensure_settings(self, project_id: uuid.UUID) -> SceneEngineSettings:
        row = await self.get_settings(project_id)
        if row is not None:
            return row
        row = SceneEngineSettings(project_id=project_id)
        self.session.add(row)
        await self.session.flush()
        return row
