"""Export queue unit tests."""

import uuid

import pytest

from app.services.export.queue import SyncExportQueue


@pytest.mark.unit
def test_sync_export_queue_enqueue() -> None:
    queue = SyncExportQueue()
    job_id = uuid.uuid4()
    project_id = uuid.uuid4()
    queue.enqueue(job_id, project_id, "epub")
    assert len(queue.pending) == 1
    assert queue.pending[0]["job_id"] == str(job_id)
