"""Fact-check worker edge-case coverage."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.fact_check import FactCheckRun
from app.workers.fact_check_worker import FactCheckWorker


@pytest.mark.unit
@pytest.mark.asyncio
async def test_worker_skips_missing_run() -> None:
    session = AsyncMock()
    session_factory = MagicMock()
    session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
    session_factory.return_value.__aexit__ = AsyncMock(return_value=None)
    session.get = AsyncMock(return_value=None)
    worker = FactCheckWorker(session_factory)
    await worker.process_run(uuid.uuid4())


@pytest.mark.unit
@pytest.mark.asyncio
async def test_worker_handles_process_failure() -> None:
    session = AsyncMock()
    session_factory = MagicMock()
    session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
    session_factory.return_value.__aexit__ = AsyncMock(return_value=None)
    run = FactCheckRun(
        project_id=uuid.uuid4(),
        chapter_id=uuid.uuid4(),
        prose_version_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        status="pending",
    )
    run.id = uuid.uuid4()
    session.get = AsyncMock(return_value=run)
    session.commit = AsyncMock()
    worker = FactCheckWorker(session_factory)
    with patch(
        "app.workers.fact_check_worker.process_fact_check_run",
        AsyncMock(side_effect=RuntimeError("boom")),
    ):
        await worker.process_run(run.id)
    assert run.status == "failed"
