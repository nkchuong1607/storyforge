"""CraftPack catalog and project binding business logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import CraftPackGenreIncompatibleError, NotFoundError
from app.models.craft_pack import ProjectCraftPack
from app.models.project import Project
from app.repositories.craft_pack import CraftPackRepository
from app.schemas.craft_pack import (
    CraftPackDetail,
    CraftPackListResponse,
    CraftPackSummary,
    ProjectCraftPackBinding,
    ProjectCraftPackResponse,
)
from app.services.craft_defaults import is_genre_compatible, pack_display_name


class CraftPackService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CraftPackRepository(session)

    async def list_catalog(self) -> CraftPackListResponse:
        rows = await self.repo.list_catalog()
        items = [
            CraftPackSummary(
                id=row.id,
                display_name=pack_display_name(row.pack_json),
                genre_tags=list(row.pack_json.get("genre_tags") or []),
                schema_version=row.schema_version,
            )
            for row in rows
        ]
        return CraftPackListResponse(items=items)

    async def get_catalog_pack(self, craft_pack_id: str) -> CraftPackDetail:
        row = await self.repo.get_catalog_pack(craft_pack_id)
        if row is None:
            raise NotFoundError(message="Craft pack not found")
        return CraftPackDetail(id=row.id, pack=row.pack_json)

    def _binding_schema(
        self, binding: ProjectCraftPack, pack_json: dict
    ) -> ProjectCraftPackBinding:
        return ProjectCraftPackBinding(
            craft_pack_id=binding.craft_pack_id,
            active=binding.active,
            bound_at=binding.bound_at,
            display_name=pack_display_name(pack_json),
        )

    async def get_project_bindings(self, project: Project) -> ProjectCraftPackResponse:
        bindings = await self.repo.list_bindings(project.id)
        items: list[ProjectCraftPackBinding] = []
        active_pack_id: str | None = None
        for binding in bindings:
            catalog = await self.repo.get_catalog_pack(binding.craft_pack_id)
            pack_json = catalog.pack_json if catalog else {}
            items.append(self._binding_schema(binding, pack_json))
            if binding.active:
                active_pack_id = binding.craft_pack_id
        return ProjectCraftPackResponse(
            project_id=project.id,
            active_pack_id=active_pack_id,
            bindings=items,
        )

    async def _ensure_compatible(self, project: Project, craft_pack_id: str) -> dict:
        catalog = await self.repo.get_catalog_pack(craft_pack_id)
        if catalog is None:
            raise NotFoundError(message="Craft pack not found")
        profile = project.genre_profile.value if project.genre_profile else "custom"
        if not is_genre_compatible(catalog.pack_json, profile):
            raise CraftPackGenreIncompatibleError(craft_pack_id, profile)
        return catalog.pack_json

    async def install(self, project: Project, craft_pack_id: str) -> ProjectCraftPackBinding:
        await self._ensure_compatible(project, craft_pack_id)
        existing = await self.repo.get_binding(project.id, craft_pack_id)
        catalog = await self.repo.get_catalog_pack(craft_pack_id)
        assert catalog is not None
        if existing is not None:
            return self._binding_schema(existing, catalog.pack_json)
        binding = ProjectCraftPack(
            project_id=project.id,
            craft_pack_id=craft_pack_id,
            active=False,
            bound_at=datetime.now(UTC),
        )
        created = await self.repo.create_binding(binding)
        await self.session.refresh(created)
        return self._binding_schema(created, catalog.pack_json)

    async def activate(self, project: Project, craft_pack_id: str) -> ProjectCraftPackBinding:
        await self._ensure_compatible(project, craft_pack_id)
        binding = await self.repo.get_binding(project.id, craft_pack_id)
        catalog = await self.repo.get_catalog_pack(craft_pack_id)
        if catalog is None:
            raise NotFoundError(message="Craft pack not found")
        if binding is None:
            binding = ProjectCraftPack(
                project_id=project.id,
                craft_pack_id=craft_pack_id,
                active=True,
                bound_at=datetime.now(UTC),
            )
            created = await self.repo.create_binding(binding)
            await self.repo.deactivate_all(project.id)
            created.active = True
            await self.session.flush()
            await self.session.refresh(created)
            return self._binding_schema(created, catalog.pack_json)
        await self.repo.deactivate_all(project.id)
        binding.active = True
        binding.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(binding)
        return self._binding_schema(binding, catalog.pack_json)

    async def deactivate(self, project: Project, craft_pack_id: str) -> ProjectCraftPackBinding:
        binding = await self.repo.get_binding(project.id, craft_pack_id)
        catalog = await self.repo.get_catalog_pack(craft_pack_id)
        if binding is None or catalog is None:
            raise NotFoundError(message="Craft pack binding not found")
        binding.active = False
        binding.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(binding)
        return self._binding_schema(binding, catalog.pack_json)

    async def get_active_pack_json(self, project_id: uuid.UUID) -> dict | None:
        binding = await self.repo.get_active_binding(project_id)
        if binding is None:
            return None
        catalog = await self.repo.get_catalog_pack(binding.craft_pack_id)
        return catalog.pack_json if catalog else None
