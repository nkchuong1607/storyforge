"""Wikipedia summary stub provider."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.config import get_settings
from app.providers.fact_check.types import (
    CitationDraft,
    ClaimDraft,
    ProviderContext,
    ProviderResult,
)

_FIXTURES_DIR = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "wikipedia"


class WikipediaSummaryProvider:
    provider_id = "wikipedia_stub"

    async def verify(self, claim: ClaimDraft, context: ProviderContext) -> ProviderResult:
        settings = get_settings()
        if settings.fact_check_live_wiki:
            return ProviderResult(
                status="inconclusive",
                severity="warn",
                confidence=0.0,
                summary="Live wikipedia opt-in only",
                proposed_correction=None,
                citations=[],
                provider_id=self.provider_id,
            )

        slug = (claim.normalized_text or claim.text).lower().replace(" ", "_")
        path = _FIXTURES_DIR / f"{slug}.json"
        if not path.exists():
            return ProviderResult(
                status="inconclusive",
                severity="warn",
                confidence=0.2,
                summary="No wikipedia stub fixture",
                proposed_correction=None,
                citations=[],
                provider_id=self.provider_id,
            )
        fixture = json.loads(path.read_text())
        now = datetime.now(UTC)
        citation = CitationDraft(
            provider_id=self.provider_id,
            url=fixture.get("url", f"https://en.wikipedia.org/wiki/{slug}"),
            title=fixture.get("title", claim.text),
            snippet=fixture.get("snippet", ""),
            retrieved_at=now,
            snapshot_json=fixture,
        )
        return ProviderResult(
            status=fixture.get("status", "verified"),
            severity=fixture.get("severity", "pass"),
            confidence=float(fixture.get("confidence", 0.65)),
            summary=fixture.get("summary", "Wikipedia stub match"),
            proposed_correction=fixture.get("correction"),
            citations=[citation],
            provider_id=self.provider_id,
        )
