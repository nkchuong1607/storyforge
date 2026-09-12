"""Slug utility unit tests."""

import pytest

from app.utils.slug import next_slug_candidate, slugify_title


@pytest.mark.unit
def test_slugify_title_strips_diacritics() -> None:
    assert slugify_title("Kiếm Lai") == "kiem-lai"


@pytest.mark.unit
def test_slugify_title_fallback_for_empty() -> None:
    assert slugify_title("!!!") == "project"


@pytest.mark.unit
def test_next_slug_candidate_suffix() -> None:
    assert next_slug_candidate("kiem-lai", 1) == "kiem-lai"
    assert next_slug_candidate("kiem-lai", 2) == "kiem-lai-2"
