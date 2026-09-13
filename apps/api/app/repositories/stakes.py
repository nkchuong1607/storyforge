"""Stakes ledger data access."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.act_structure_settings import ActStructureSettings
from app.models.stakes_ledger_entry import StakesLedgerEntry


class StakesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_settings(self, project_id: uuid.UUID) -> ActStructureSettings | None:
        return await self.session.get(ActStructureSettings, project_id)

    async def ensure_settings(self, project_id: uuid.UUID) -> ActStructureSettings:
        row = await self.get_settings(project_id)
        if row is not None:
            return row
        row = ActStructureSettings(project_id=project_id)
        self.session.add(row)
        await self.session.flush()
        return row

    async def list_entries(self, project_id: uuid.UUID) -> list[StakesLedgerEntry]:
        rows = await self.session.scalars(
            select(StakesLedgerEntry)
            .where(StakesLedgerEntry.project_id == project_id)
            .order_by(
                StakesLedgerEntry.act_number.asc(),
                StakesLedgerEntry.sort_order.asc(),
            )
        )
        return list(rows.all())

    async def list_entries_for_act(
        self, project_id: uuid.UUID, act_number: int
    ) -> list[StakesLedgerEntry]:
        rows = await self.session.scalars(
            select(StakesLedgerEntry)
            .where(
                StakesLedgerEntry.project_id == project_id,
                StakesLedgerEntry.act_number == act_number,
            )
            .order_by(StakesLedgerEntry.sort_order.asc())
        )
        return list(rows.all())

    async def get_entry(
        self, project_id: uuid.UUID, entry_id: uuid.UUID
    ) -> StakesLedgerEntry | None:
        return await self.session.scalar(
            select(StakesLedgerEntry).where(
                StakesLedgerEntry.project_id == project_id,
                StakesLedgerEntry.id == entry_id,
            )
        )

    async def get_by_checkpoint(
        self, project_id: uuid.UUID, act_number: int, checkpoint_key: str
    ) -> StakesLedgerEntry | None:
        return await self.session.scalar(
            select(StakesLedgerEntry).where(
                StakesLedgerEntry.project_id == project_id,
                StakesLedgerEntry.act_number == act_number,
                StakesLedgerEntry.checkpoint_key == checkpoint_key,
            )
        )

    async def create_entry(self, entry: StakesLedgerEntry) -> StakesLedgerEntry:
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def update_entry(self, entry: StakesLedgerEntry) -> StakesLedgerEntry:
        await self.session.flush()
        return entry

    async def delete_entry(self, entry: StakesLedgerEntry) -> None:
        await self.session.delete(entry)
        await self.session.flush()
