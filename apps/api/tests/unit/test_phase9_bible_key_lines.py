"""Cover remaining phase9_bible branches."""

import pytest

from app.utils.phase9_bible import snapshot_to_slice_json


@pytest.mark.unit
def test_snapshot_to_slice_json_skips_invalid_entries() -> None:
    result = snapshot_to_slice_json({"entries": ["bad", {"no_key": True}]}, ["world"])
    assert result["world"] == {}
