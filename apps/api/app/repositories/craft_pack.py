"""CraftPack persistence."""

from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.craft_pack import CraftPack, ProjectCraftPack


class CraftPackRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_catalog(self) -> list[CraftPack]:
        rows = await self.session.scalars(select(CraftPack).order_by(CraftPack.id))
        return list(rows.all())

    async def get_catalog_pack(self, craft_pack_id: str) -> CraftPack | None:
        return await self.session.scalar(select(CraftPack).where(CraftPack.id == craft_pack_id))

    async def list_bindings(self, project_id: uuid.UUID) -> list[ProjectCraftPack]:
        rows = await self.session.scalars(
            select(ProjectCraftPack)
            .where(ProjectCraftPack.project_id == project_id)
            .order_by(ProjectCraftPack.bound_at.desc())
        )
        return list(rows.all())

    async def get_binding(
        self, project_id: uuid.UUID, craft_pack_id: str
    ) -> ProjectCraftPack | None:
        return await self.session.scalar(
            select(ProjectCraftPack).where(
                ProjectCraftPack.project_id == project_id,
                ProjectCraftPack.craft_pack_id == craft_pack_id,
            )
        )

    async def get_active_binding(self, project_id: uuid.UUID) -> ProjectCraftPack | None:
        return await self.session.scalar(
            select(ProjectCraftPack).where(
                ProjectCraftPack.project_id == project_id,
                ProjectCraftPack.active.is_(True),
            )
        )

    async def create_binding(self, binding: ProjectCraftPack) -> ProjectCraftPack:
        self.session.add(binding)
        await self.session.flush()
        return binding

    async def deactivate_all(self, project_id: uuid.UUID) -> None:
        await self.session.execute(
            update(ProjectCraftPack)
            .where(ProjectCraftPack.project_id == project_id)
            .values(active=False)
        )
