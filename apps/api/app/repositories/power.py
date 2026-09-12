"""Power system data access."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.power_system import PowerRank, PowerSystemSettings, PowerTechnique


class PowerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_settings(self, project_id: uuid.UUID) -> PowerSystemSettings | None:
        return await self.session.get(PowerSystemSettings, project_id)

    async def ensure_settings(self, project_id: uuid.UUID) -> PowerSystemSettings:
        row = await self.get_settings(project_id)
        if row is not None:
            return row
        row = PowerSystemSettings(project_id=project_id)
        self.session.add(row)
        await self.session.flush()
        return row

    async def list_ranks(self, project_id: uuid.UUID) -> list[PowerRank]:
        rows = await self.session.scalars(
            select(PowerRank)
            .where(PowerRank.project_id == project_id)
            .order_by(PowerRank.sort_order.asc())
        )
        return list(rows.all())

    async def get_rank(self, project_id: uuid.UUID, rank_id: uuid.UUID) -> PowerRank | None:
        return await self.session.scalar(
            select(PowerRank).where(
                PowerRank.project_id == project_id,
                PowerRank.id == rank_id,
            )
        )

    async def create_rank(self, rank: PowerRank) -> PowerRank:
        self.session.add(rank)
        await self.session.flush()
        return rank

    async def delete_rank(self, rank: PowerRank) -> None:
        await self.session.delete(rank)
        await self.session.flush()

    async def count_techniques_for_rank(self, project_id: uuid.UUID, rank_id: uuid.UUID) -> int:
        result = await self.session.scalar(
            select(func.count())
            .select_from(PowerTechnique)
            .where(
                PowerTechnique.project_id == project_id,
                PowerTechnique.min_rank_id == rank_id,
            )
        )
        return int(result or 0)

    async def list_techniques(self, project_id: uuid.UUID) -> list[PowerTechnique]:
        rows = await self.session.scalars(
            select(PowerTechnique)
            .where(PowerTechnique.project_id == project_id)
            .order_by(PowerTechnique.display_name.asc())
        )
        return list(rows.all())

    async def get_technique(
        self, project_id: uuid.UUID, technique_id: uuid.UUID
    ) -> PowerTechnique | None:
        return await self.session.scalar(
            select(PowerTechnique).where(
                PowerTechnique.project_id == project_id,
                PowerTechnique.id == technique_id,
            )
        )

    async def create_technique(self, technique: PowerTechnique) -> PowerTechnique:
        self.session.add(technique)
        await self.session.flush()
        return technique

    async def delete_technique(self, technique: PowerTechnique) -> None:
        await self.session.delete(technique)
        await self.session.flush()

    async def max_sort_order(self, project_id: uuid.UUID) -> int:
        result = await self.session.scalar(
            select(func.max(PowerRank.sort_order)).where(PowerRank.project_id == project_id)
        )
        return int(result) if result is not None else -1
