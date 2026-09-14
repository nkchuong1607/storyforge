"""Fact-check worker — processes pending runs."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.enums import FactCheckRunStatus
from app.models.fact_check import FactCheckRun
from app.services.fact_check_processor import process_fact_check_run


class FactCheckWorker:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def process_run(self, run_id: uuid.UUID) -> None:
        async with self.session_factory() as session:
            run = await session.get(FactCheckRun, run_id)
            if run is None or run.status not in (
                FactCheckRunStatus.pending.value,
                FactCheckRunStatus.running.value,
            ):
                return
            run.status = FactCheckRunStatus.running.value
            run.started_at = datetime.now(UTC)
            await session.commit()

        try:
            async with self.session_factory() as session:
                await process_fact_check_run(session, run_id)
                await session.commit()
        except Exception:
            async with self.session_factory() as session:
                run = await session.get(FactCheckRun, run_id)
                if run and run.status != FactCheckRunStatus.done.value:
                    run.status = FactCheckRunStatus.failed.value
                    run.finished_at = datetime.now(UTC)
                    await session.commit()


async def process_sync_fact_check_queue(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Process all runs in sync queue (test helper)."""
    from app.services.fact_check.queue import get_fact_check_queue

    queue = get_fact_check_queue()
    if not hasattr(queue, "pending"):
        return
    worker = FactCheckWorker(session_factory)
    for item in list(queue.pending):
        await worker.process_run(uuid.UUID(item["run_id"]))
    queue.pending.clear()
