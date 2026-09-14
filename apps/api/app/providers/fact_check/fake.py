"""Deterministic FakeVerifier — default provider for tests and local dev."""

from __future__ import annotations

from datetime import UTC, datetime

from app.providers.fact_check.types import (
    CitationDraft,
    ClaimDraft,
    ProviderContext,
    ProviderResult,
)

_FAKE_FIXTURES: dict[tuple[str, str], dict] = {
    ("date", "1945-03"): {
        "status": "verified",
        "severity": "pass",
        "confidence": 0.95,
        "summary": "Date verified",
        "correction": None,
        "url_slug": "1945-03",
        "snippet": "March 1945 confirmed",
    },
    ("date", "1985-11-09"): {
        "status": "contradiction",
        "severity": "fail",
        "confidence": 0.91,
        "summary": "Berlin Wall fell in 1989, not 1985",
        "correction": "9 November 1989",
        "url_slug": "berlin-wall",
        "snippet": "Opened: 9 November 1989",
    },
    ("place", "berlin"): {
        "status": "verified",
        "severity": "pass",
        "confidence": 0.88,
        "summary": "Place verified",
        "correction": None,
        "url_slug": "berlin",
        "snippet": "Capital city of Germany",
    },
    ("place", "mount fakepeak"): {
        "status": "inconclusive",
        "severity": "warn",
        "confidence": 0.4,
        "summary": "Place not found in reference data",
        "correction": None,
        "url_slug": "mount-fakepeak",
        "snippet": "",
    },
}


class FakeVerifier:
    provider_id = "fake"

    async def verify(self, claim: ClaimDraft, context: ProviderContext) -> ProviderResult:
        key = (claim.category, (claim.normalized_text or claim.text).lower())
        fixture = _FAKE_FIXTURES.get(key)
        now = datetime.now(UTC)
        if fixture is None:
            return ProviderResult(
                status="inconclusive",
                severity="warn",
                confidence=0.3,
                summary="No deterministic fixture for claim",
                proposed_correction=None,
                citations=[],
                provider_id=self.provider_id,
            )
        citation = CitationDraft(
            provider_id=self.provider_id,
            url=f"https://fake.storyforge.test/{fixture['url_slug']}",
            title=claim.text,
            snippet=fixture["snippet"],
            retrieved_at=now,
            snapshot_json={"fixture_key": list(key), **fixture},
        )
        return ProviderResult(
            status=fixture["status"],
            severity=fixture["severity"],
            confidence=fixture["confidence"],
            summary=fixture["summary"],
            proposed_correction=fixture.get("correction"),
            citations=[citation],
            provider_id=self.provider_id,
        )
