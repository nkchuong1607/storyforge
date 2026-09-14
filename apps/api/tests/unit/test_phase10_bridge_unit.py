"""Fact-check continuity bridge unit tests."""

import uuid
from decimal import Decimal

import pytest

from app.models.enums import ContinuityCategory, ContinuitySeverity
from app.models.fact_check import FactClaim
from app.services.continuity.fact_check import run_fact_check_bridge


def _claim(severity: str) -> FactClaim:
    return FactClaim(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        category="date",
        text="9 November 1985",
        normalized_text="1985-11-09",
        span_start=10,
        span_end=26,
        span_excerpt="...9 November 1985...",
        source_type="prose",
        severity=severity,
        confidence=Decimal("0.91"),
        summary="Berlin Wall date mismatch",
        proposed_correction="9 November 1989",
        author_disposition="open",
        provider_results_json=[],
    )


@pytest.mark.unit
def test_bridge_maps_fail_to_warn_category() -> None:
    chapter_id = uuid.uuid4()
    issues = run_fact_check_bridge(claims=[_claim("fail")], chapter_id=chapter_id)
    assert len(issues) == 1
    assert issues[0].severity == ContinuitySeverity.WARN.value
    assert issues[0].category == ContinuityCategory.fact_check.value
    assert issues[0].code == "fact_check_contradiction"
    assert issues[0].evidence["original_severity"] == "fail"


@pytest.mark.unit
def test_bridge_warn_issue_code() -> None:
    issues = run_fact_check_bridge(claims=[_claim("warn")], chapter_id=uuid.uuid4())
    assert issues[0].code == "fact_check_unverified_claim"
