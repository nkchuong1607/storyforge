"""Phase 10 fact-check continuity bridge — WARN-only in Gate."""

from __future__ import annotations

import uuid

from app.models.enums import ContinuityCategory, ContinuitySeverity, FactClaimSeverity
from app.models.fact_check import FactClaim
from app.services.continuity.engine import ContinuityIssue


def run_fact_check_bridge(
    *,
    claims: list[FactClaim],
    chapter_id: uuid.UUID,
) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []
    for claim in claims:
        code = (
            "fact_check_contradiction"
            if claim.severity == FactClaimSeverity.fail.value
            else "fact_check_unverified_claim"
        )
        span = {}
        if claim.span_start is not None and claim.span_end is not None:
            span = {"start": claim.span_start, "end": claim.span_end}
        issues.append(
            ContinuityIssue(
                fingerprint=f"fact_check:{claim.id}:{code}",
                severity=ContinuitySeverity.WARN.value,
                category=ContinuityCategory.fact_check.value,
                code=code,
                message=claim.summary or f"Real-world fact-check: {claim.text}",
                chapter_refs=[],
                entity_ids=[str(claim.id)],
                evidence={
                    "bridge": True,
                    "original_severity": claim.severity,
                    "chapter_id": str(chapter_id),
                    "span": span,
                    "fact_claim_id": str(claim.id),
                },
            )
        )
    return issues
