"""Continuity report and override data access."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.continuity import ContinuityOverride, ContinuityReport, SettleIdempotencyKey


class ContinuityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_report(self, report: ContinuityReport) -> ContinuityReport:
        self.session.add(report)
        await self.session.flush()
        return report

    async def get_report(
        self, chapter_id: uuid.UUID, report_id: uuid.UUID
    ) -> ContinuityReport | None:
        return await self.session.scalar(
            select(ContinuityReport).where(
                ContinuityReport.id == report_id,
                ContinuityReport.chapter_id == chapter_id,
            )
        )

    async def get_latest_report(self, chapter_id: uuid.UUID) -> ContinuityReport | None:
        return await self.session.scalar(
            select(ContinuityReport)
            .where(ContinuityReport.chapter_id == chapter_id)
            .order_by(ContinuityReport.created_at.desc())
            .limit(1)
        )

    async def create_override(self, override: ContinuityOverride) -> ContinuityOverride:
        self.session.add(override)
        await self.session.flush()
        return override

    async def active_override_fingerprints(self, chapter_id: uuid.UUID) -> set[str]:
        rows = await self.session.scalars(
            select(ContinuityOverride.issue_fingerprint).where(
                ContinuityOverride.chapter_id == chapter_id,
                ContinuityOverride.revoked_at.is_(None),
            )
        )
        return set(rows.all())

    async def get_idempotency(
        self, chapter_id: uuid.UUID, idempotency_key: uuid.UUID
    ) -> SettleIdempotencyKey | None:
        return await self.session.scalar(
            select(SettleIdempotencyKey).where(
                SettleIdempotencyKey.chapter_id == chapter_id,
                SettleIdempotencyKey.idempotency_key == idempotency_key,
            )
        )

    async def save_idempotency(self, record: SettleIdempotencyKey) -> SettleIdempotencyKey:
        self.session.add(record)
        await self.session.flush()
        return record
