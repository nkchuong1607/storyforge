"""Project reality settings data access."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_reality_settings import ProjectRealitySettings


class RealitySettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_settings(self, project_id: uuid.UUID) -> ProjectRealitySettings | None:
        return await self.session.get(ProjectRealitySettings, project_id)

    async def ensure_settings(self, project_id: uuid.UUID) -> ProjectRealitySettings:
        row = await self.get_settings(project_id)
        if row is not None:
            return row
        row = ProjectRealitySettings(project_id=project_id)
        self.session.add(row)
        await self.session.flush()
        return row
