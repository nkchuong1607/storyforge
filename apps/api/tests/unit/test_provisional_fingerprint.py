"""Unit tests for provisional fingerprint."""

import uuid

import pytest

from app.utils.provisional_fingerprint import compute_mention_fingerprint


@pytest.mark.unit
def test_fingerprint_is_stable() -> None:
    project_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    chapter_id = uuid.UUID("660e8400-e29b-41d4-a716-446655440001")
    first = compute_mention_fingerprint(project_id, "Hắc Y Nhân", chapter_id)
    second = compute_mention_fingerprint(project_id, "  hắc y nhân ", chapter_id)
    assert first == second
    assert len(first) == 64
