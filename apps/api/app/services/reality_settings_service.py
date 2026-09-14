"""Project reality settings business logic."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InvalidClaimCategoryError, InvalidRealityAnchorsError
from app.models.enums import FactClaimCategory, RealityAnchorsMode
from app.models.project import Project
from app.repositories.reality_settings import RealitySettingsRepository
from app.schemas.reality_settings import (
    ProjectRealitySettings as ProjectRealitySettingsSchema,
)
from app.schemas.reality_settings import ProjectRealitySettingsUpdate


class RealitySettingsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = RealitySettingsRepository(session)

    def _validate_categories(self, categories: list[str]) -> None:
        valid = {c.value for c in FactClaimCategory}
        for cat in categories:
            if cat not in valid:
                raise InvalidClaimCategoryError(f"Unknown category: {cat}")

    async def get_settings(self, project: Project) -> ProjectRealitySettingsSchema:
        row = await self.repo.ensure_settings(project.id)
        return ProjectRealitySettingsSchema.model_validate(row)

    async def update_settings(
        self, project: Project, payload: ProjectRealitySettingsUpdate
    ) -> ProjectRealitySettingsSchema:
        row = await self.repo.ensure_settings(project.id)
        data = payload.model_dump(exclude_unset=True)
        if "reality_anchors" in data and data["reality_anchors"] is not None:
            try:
                RealityAnchorsMode(data["reality_anchors"])
            except ValueError as exc:
                raise InvalidRealityAnchorsError() from exc
        if "enabled_categories" in data and data["enabled_categories"] is not None:
            raw_categories = [
                c.value if hasattr(c, "value") else c for c in data["enabled_categories"]
            ]
            self._validate_categories(raw_categories)
            data["enabled_categories"] = [
                c.value if hasattr(c, "value") else c for c in data["enabled_categories"]
            ]
        for key, value in data.items():
            setattr(row, key, value)
        row.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(row)
        return ProjectRealitySettingsSchema.model_validate(row)
