"""Pagination helper unit tests."""

import pytest

from app.utils.pagination import build_pagination, clamp_page_params


@pytest.mark.unit
def test_clamp_page_params_defaults() -> None:
    params = clamp_page_params(0, 200)
    assert params.page == 1
    assert params.page_size == 100


@pytest.mark.unit
def test_build_pagination_total_pages() -> None:
    meta = build_pagination(page=1, page_size=20, total_items=42)
    assert meta.total_pages == 3
