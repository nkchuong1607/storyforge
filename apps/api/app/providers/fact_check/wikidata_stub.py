"""Wikidata stub provider — fixture JSON unless live mode enabled."""

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

_FIXTURES_DIR = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "wikidata"


class WikidataStubProvider:
    provider_id = "wikidata_stub"

    async def verify(self, claim: ClaimDraft, context: ProviderContext) -> ProviderResult:
        settings = get_settings()
        if settings.fact_check_live_wiki:
            return await self._live_lookup(claim)

        fixture = self._load_fixture(claim)
        if fixture is None:
            return ProviderResult(
                status="inconclusive",
                severity="warn",
                confidence=0.25,
                summary="No wikidata stub fixture",
                proposed_correction=None,
                citations=[],
                provider_id=self.provider_id,
            )
        now = datetime.now(UTC)
        citation = CitationDraft(
            provider_id=self.provider_id,
            url=fixture.get("url", "https://www.wikidata.org/wiki/Q0"),
            title=fixture.get("title", claim.text),
            snippet=fixture.get("snippet", ""),
            retrieved_at=now,
            snapshot_json=fixture,
        )
        return ProviderResult(
            status=fixture.get("status", "verified"),
            severity=fixture.get("severity", "pass"),
            confidence=float(fixture.get("confidence", 0.7)),
            summary=fixture.get("summary", "Wikidata stub match"),
            proposed_correction=fixture.get("correction"),
            citations=[citation],
            provider_id=self.provider_id,
        )

    def _load_fixture(self, claim: ClaimDraft) -> dict | None:
        slug = (claim.normalized_text or claim.text).lower().replace(" ", "-")
        path = _FIXTURES_DIR / f"{slug}.json"
        if not path.exists():
            path = _FIXTURES_DIR / f"{claim.category}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    async def _live_lookup(self, claim: ClaimDraft) -> ProviderResult:
        return ProviderResult(
            status="inconclusive",
            severity="warn",
            confidence=0.0,
            summary="Live wikidata not configured in stub",
            proposed_correction=None,
            citations=[],
            provider_id=self.provider_id,
        )
