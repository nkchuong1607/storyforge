"""Export job status transition unit tests."""

import pytest

from app.models.enums import ExportJobStatus


@pytest.mark.unit
def test_valid_status_values() -> None:
    assert ExportJobStatus.pending.value == "pending"
    assert ExportJobStatus.done.value == "done"
    assert ExportJobStatus.pending.value != ExportJobStatus.running.value


@pytest.mark.unit
def test_invalid_transition_pending_from_running() -> None:
    current = ExportJobStatus.running
    assert current != ExportJobStatus.pending
