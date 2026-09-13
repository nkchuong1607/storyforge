"""Phase 9 edge-case unit tests."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.project import Project
from app.models.series import SeriesBibleSlice
from app.services.series import SeriesService
from app.workers.export_worker import process_sync_queue


@pytest.mark.unit
async def test_process_sync_queue_non_sync_returns() -> None:
    queue = MagicMock(spec=[])
    with patch("app.services.export.queue.get_export_queue", return_value=queue):
        await process_sync_queue(MagicMock())


@pytest.mark.unit
async def test_series_mark_slice_seen() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = uuid.uuid4()
    project.series_id = uuid.uuid4()
    latest = SeriesBibleSlice(
        series_id=project.series_id,
        version=4,
        slice_json={},
        inherited_sections=["world"],
    )
    service.series.get_latest_slice = AsyncMock(return_value=latest)
    await service.mark_slice_seen(project)
    assert project.last_seen_series_slice_version == 4


@pytest.mark.unit
async def test_series_mark_slice_seen_no_series() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.series_id = None
    await service.mark_slice_seen(project)


@pytest.mark.unit
async def test_series_mark_slice_seen_no_latest() -> None:
    session = AsyncMock()
    service = SeriesService(session)
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.series_id = uuid.uuid4()
    service.series.get_latest_slice = AsyncMock(return_value=None)
    await service.mark_slice_seen(project)
    assert project.last_seen_series_slice_version is None
