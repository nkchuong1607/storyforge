"""Phase 10 claim extractor unit tests."""

import pytest

from app.models.enums import RealityAnchorsMode
from app.services.fact_check.extractor import extract_claims, normalize_date


@pytest.mark.unit
def test_normalize_date_full() -> None:
    assert normalize_date("9 November 1985") == "1985-11-09"


@pytest.mark.unit
def test_normalize_date_month_year() -> None:
    assert normalize_date("March 1945") == "1945-03"


@pytest.mark.unit
def test_extract_strict_mode_dates() -> None:
    prose = "The wall fell on 9 November 1985 in Berlin."
    claims = extract_claims(
        prose=prose,
        reality_mode=RealityAnchorsMode.strict.value,
        enabled_categories=[],
    )
    date_claims = [c for c in claims if c.category == "date"]
    assert len(date_claims) >= 1
    assert date_claims[0].normalized_text == "1985-11-09"


@pytest.mark.unit
def test_extract_soft_anchor_only() -> None:
    prose = "Plain text. [[anchor]]9 November 1985[[/anchor]] more text."
    claims = extract_claims(
        prose=prose,
        reality_mode=RealityAnchorsMode.soft.value,
        enabled_categories=["date"],
    )
    assert any(c.source_type == "anchor_marker" for c in claims)


@pytest.mark.unit
def test_extract_off_returns_empty() -> None:
    claims = extract_claims(
        prose="9 November 1985",
        reality_mode=RealityAnchorsMode.off.value,
        enabled_categories=[],
    )
    assert claims == []
