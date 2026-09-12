"""TwistPlan persistence."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chapter import Chapter
from app.models.enums import TwistPlanKind, TwistPlanStatus
from app.models.twist import TwistPayoff, TwistPlan, TwistPlant
from app.utils.pagination import PageParams


class TwistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_plan(self, project_id: uuid.UUID, twist_id: uuid.UUID) -> TwistPlan | None:
        return await self.session.scalar(
            select(TwistPlan).where(
                TwistPlan.project_id == project_id,
                TwistPlan.id == twist_id,
            )
        )

    async def list_plans(
        self,
        project_id: uuid.UUID,
        page: PageParams,
        *,
        status: TwistPlanStatus | None = None,
        kind: TwistPlanKind | None = None,
        q: str | None = None,
        exclude_abandoned: bool = False,
    ) -> tuple[list[TwistPlan], int]:
        query = select(TwistPlan).where(TwistPlan.project_id == project_id)
        if status is not None:
            query = query.where(TwistPlan.status == status)
        if kind is not None:
            query = query.where(TwistPlan.kind == kind)
        if q:
            query = query.where(TwistPlan.title.ilike(f"%{q}%"))
        if exclude_abandoned:
            query = query.where(TwistPlan.status != TwistPlanStatus.abandoned)
        total = await self.session.scalar(select(func.count()).select_from(query.subquery()))
        rows = await self.session.scalars(
            query.order_by(TwistPlan.updated_at.desc())
            .offset((page.page - 1) * page.page_size)
            .limit(page.page_size)
        )
        return list(rows.all()), int(total or 0)

    async def list_all_plans(
        self,
        project_id: uuid.UUID,
        *,
        kind: TwistPlanKind | None = None,
        include_abandoned: bool = False,
    ) -> list[TwistPlan]:
        query = select(TwistPlan).where(TwistPlan.project_id == project_id)
        if kind is not None:
            query = query.where(TwistPlan.kind == kind)
        if not include_abandoned:
            query = query.where(TwistPlan.status != TwistPlanStatus.abandoned)
        rows = await self.session.scalars(query.order_by(TwistPlan.updated_at.desc()))
        return list(rows.all())

    async def create_plan(self, twist: TwistPlan) -> TwistPlan:
        self.session.add(twist)
        await self.session.flush()
        return twist

    async def update_plan(self, twist: TwistPlan) -> TwistPlan:
        await self.session.flush()
        return twist

    async def count_plants(self, twist_id: uuid.UUID) -> int:
        count = await self.session.scalar(
            select(func.count()).select_from(TwistPlant).where(TwistPlant.twist_id == twist_id)
        )
        return int(count or 0)

    async def list_plants(self, twist_id: uuid.UUID) -> list[TwistPlant]:
        rows = await self.session.scalars(
            select(TwistPlant)
            .where(TwistPlant.twist_id == twist_id)
            .order_by(TwistPlant.sort_order.asc())
        )
        return list(rows.all())

    async def list_plants_for_project(self, project_id: uuid.UUID) -> list[TwistPlant]:
        rows = await self.session.scalars(
            select(TwistPlant).where(TwistPlant.project_id == project_id)
        )
        return list(rows.all())

    async def get_plant(
        self, project_id: uuid.UUID, twist_id: uuid.UUID, plant_id: uuid.UUID
    ) -> TwistPlant | None:
        return await self.session.scalar(
            select(TwistPlant).where(
                TwistPlant.project_id == project_id,
                TwistPlant.twist_id == twist_id,
                TwistPlant.id == plant_id,
            )
        )

    async def create_plant(self, plant: TwistPlant) -> TwistPlant:
        self.session.add(plant)
        await self.session.flush()
        return plant

    async def delete_plant(self, plant: TwistPlant) -> None:
        await self.session.delete(plant)
        await self.session.flush()

    async def get_payoff(self, project_id: uuid.UUID, twist_id: uuid.UUID) -> TwistPayoff | None:
        return await self.session.scalar(
            select(TwistPayoff).where(
                TwistPayoff.project_id == project_id,
                TwistPayoff.twist_id == twist_id,
            )
        )

    async def get_payoff_by_id(
        self, project_id: uuid.UUID, twist_id: uuid.UUID, payoff_id: uuid.UUID
    ) -> TwistPayoff | None:
        return await self.session.scalar(
            select(TwistPayoff).where(
                TwistPayoff.project_id == project_id,
                TwistPayoff.twist_id == twist_id,
                TwistPayoff.id == payoff_id,
            )
        )

    async def list_payoffs_with_twists_for_chapter(
        self, project_id: uuid.UUID, chapter_id: uuid.UUID
    ) -> list[tuple[TwistPayoff, TwistPlan]]:
        rows = await self.session.execute(
            select(TwistPayoff, TwistPlan)
            .join(TwistPlan, TwistPlan.id == TwistPayoff.twist_id)
            .where(
                TwistPayoff.project_id == project_id,
                TwistPayoff.target_chapter_id == chapter_id,
            )
        )
        return list(rows.all())

    async def create_payoff(self, payoff: TwistPayoff) -> TwistPayoff:
        self.session.add(payoff)
        await self.session.flush()
        return payoff

    async def delete_payoff(self, payoff: TwistPayoff) -> None:
        await self.session.delete(payoff)
        await self.session.flush()

    async def mark_payoffs_revealed_for_chapter(
        self, project_id: uuid.UUID, chapter_id: uuid.UUID, revealed_at
    ) -> int:
        from app.models.enums import TwistPlanStatus

        rows = await self.session.execute(
            select(TwistPayoff, TwistPlan)
            .join(TwistPlan, TwistPlan.id == TwistPayoff.twist_id)
            .where(
                TwistPayoff.project_id == project_id,
                TwistPayoff.target_chapter_id == chapter_id,
                TwistPlan.status == TwistPlanStatus.armed,
            )
        )
        count = 0
        for payoff, twist in rows.all():
            payoff.revealed_at = revealed_at
            twist.status = TwistPlanStatus.paid_off
            count += 1
        if count:
            await self.session.flush()
        return count

    async def list_active_plants_for_context(
        self,
        project_id: uuid.UUID,
        chapter_number: int,
        limit: int,
    ) -> list[tuple[TwistPlant, TwistPlan, Chapter]]:
        """Plants for active twists in chapters <= current chapter number."""
        rows = await self.session.execute(
            select(TwistPlant, TwistPlan, Chapter)
            .join(TwistPlan, TwistPlan.id == TwistPlant.twist_id)
            .join(Chapter, TwistPlant.chapter_id == Chapter.id)
            .where(
                TwistPlant.project_id == project_id,
                TwistPlan.status.in_([TwistPlanStatus.planted, TwistPlanStatus.armed]),
                Chapter.number <= chapter_number,
            )
            .order_by(TwistPlant.sort_order.asc())
            .limit(limit)
        )
        return list(rows.all())
