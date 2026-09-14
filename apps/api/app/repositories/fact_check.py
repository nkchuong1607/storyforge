"""Fact-check data access."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import FactCheckRunStatus, FactClaimDisposition, FactClaimSeverity
from app.models.fact_check import FactCheckRun, FactCitation, FactClaim
from app.utils.pagination import PageParams


class FactCheckRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_run(self, run: FactCheckRun) -> FactCheckRun:
        self.session.add(run)
        await self.session.flush()
        return run

    async def get_run(self, project_id: uuid.UUID, run_id: uuid.UUID) -> FactCheckRun | None:
        return await self.session.scalar(
            select(FactCheckRun).where(
                FactCheckRun.id == run_id,
                FactCheckRun.project_id == project_id,
            )
        )

    async def list_runs(
        self, project_id: uuid.UUID, chapter_id: uuid.UUID, page: PageParams
    ) -> tuple[list[FactCheckRun], int]:
        filters = [
            FactCheckRun.project_id == project_id,
            FactCheckRun.chapter_id == chapter_id,
        ]
        base = select(FactCheckRun).where(*filters).order_by(FactCheckRun.created_at.desc())
        total = int(
            await self.session.scalar(
                select(func.count()).select_from(FactCheckRun).where(*filters)
            )
            or 0
        )
        rows = await self.session.scalars(base.offset(page.offset).limit(page.page_size))
        return list(rows.all()), total

    async def pending_run_for_prose(
        self, project_id: uuid.UUID, prose_version_id: uuid.UUID
    ) -> FactCheckRun | None:
        return await self.session.scalar(
            select(FactCheckRun).where(
                FactCheckRun.project_id == project_id,
                FactCheckRun.prose_version_id == prose_version_id,
                FactCheckRun.status.in_(
                    [FactCheckRunStatus.pending.value, FactCheckRunStatus.running.value]
                ),
            )
        )

    async def latest_done_run_for_chapter(
        self, project_id: uuid.UUID, chapter_id: uuid.UUID
    ) -> FactCheckRun | None:
        return await self.session.scalar(
            select(FactCheckRun)
            .where(
                FactCheckRun.project_id == project_id,
                FactCheckRun.chapter_id == chapter_id,
                FactCheckRun.status == FactCheckRunStatus.done.value,
            )
            .order_by(FactCheckRun.created_at.desc())
            .limit(1)
        )

    async def list_claims_for_run(self, run_id: uuid.UUID) -> list[FactClaim]:
        rows = await self.session.scalars(
            select(FactClaim).where(FactClaim.run_id == run_id).order_by(FactClaim.created_at)
        )
        return list(rows.all())

    async def list_citations_for_claims(self, claim_ids: list[uuid.UUID]) -> list[FactCitation]:
        if not claim_ids:
            return []
        rows = await self.session.scalars(
            select(FactCitation).where(FactCitation.claim_id.in_(claim_ids))
        )
        return list(rows.all())

    async def get_claim(self, project_id: uuid.UUID, claim_id: uuid.UUID) -> FactClaim | None:
        return await self.session.scalar(
            select(FactClaim).where(
                FactClaim.id == claim_id,
                FactClaim.project_id == project_id,
            )
        )

    async def create_claim(self, claim: FactClaim) -> FactClaim:
        self.session.add(claim)
        await self.session.flush()
        return claim

    async def create_citation(self, citation: FactCitation) -> FactCitation:
        self.session.add(citation)
        await self.session.flush()
        return citation

    async def update_run(self, run: FactCheckRun) -> FactCheckRun:
        await self.session.flush()
        return run

    async def open_fail_claims_for_chapter(
        self, project_id: uuid.UUID, chapter_id: uuid.UUID
    ) -> list[FactClaim]:
        run = await self.latest_done_run_for_chapter(project_id, chapter_id)
        if run is None:
            return []
        rows = await self.session.scalars(
            select(FactClaim).where(
                FactClaim.run_id == run.id,
                FactClaim.severity == FactClaimSeverity.fail.value,
                FactClaim.author_disposition == FactClaimDisposition.open.value,
            )
        )
        return list(rows.all())

    async def bridge_claims_for_chapter(
        self, project_id: uuid.UUID, chapter_id: uuid.UUID
    ) -> list[FactClaim]:
        run = await self.latest_done_run_for_chapter(project_id, chapter_id)
        if run is None:
            return []
        excluded = {
            FactClaimDisposition.intentional_fiction.value,
            FactClaimDisposition.dismissed.value,
            FactClaimDisposition.accepted_fix.value,
            FactClaimDisposition.evidence_promoted.value,
        }
        rows = await self.session.scalars(
            select(FactClaim).where(
                FactClaim.run_id == run.id,
                FactClaim.author_disposition.notin_(excluded),
                FactClaim.severity.in_(
                    [FactClaimSeverity.warn.value, FactClaimSeverity.fail.value]
                ),
            )
        )
        return list(rows.all())
