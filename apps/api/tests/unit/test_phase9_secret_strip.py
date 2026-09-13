"""Secret strip unit tests."""

import pytest

from app.services.export.secret_strip import strip_secrets_from_snapshot, strip_secrets_from_text


@pytest.mark.unit
def test_strip_secrets_from_snapshot() -> None:
    snapshot = {
        "entries": [{"entry_key": "world.a", "secret_truth": "hidden", "title": "A"}],
        "secret_truth": "top-level",
    }
    cleaned = strip_secrets_from_snapshot(snapshot)
    assert "secret_truth" not in cleaned
    assert "secret_truth" not in cleaned["entries"][0]


@pytest.mark.unit
def test_strip_secrets_from_text() -> None:
    text = "Normal line\nsecret_truth: reveal"
    assert "secret_truth" not in strip_secrets_from_text(text).lower()
