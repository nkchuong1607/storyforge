"""Provider orchestrator — merges results per claim."""

from __future__ import annotations

from app.config import get_settings
from app.providers.fact_check.fake import FakeVerifier
from app.providers.fact_check.research_note import ResearchNoteEvidenceProvider
from app.providers.fact_check.types import ClaimDraft, ProviderContext, ProviderResult

_SEVERITY_ORDER = {"pass": 0, "warn": 1, "fail": 2}


def build_providers(*, http_enabled: bool, include_research: bool) -> list:
    providers: list = []
    if include_research:
        providers.append(ResearchNoteEvidenceProvider())
    if http_enabled:
        from app.providers.fact_check.wikidata_stub import WikidataStubProvider
        from app.providers.fact_check.wikipedia_stub import WikipediaSummaryProvider

        providers.extend([WikidataStubProvider(), WikipediaSummaryProvider()])
    providers.append(FakeVerifier())
    return providers


async def verify_claim(
    claim: ClaimDraft,
    context: ProviderContext,
    *,
    include_research: bool = True,
) -> ProviderResult:
    settings = get_settings()
    providers = build_providers(
        http_enabled=context.http_enabled,
        include_research=include_research,
    )
    merged: ProviderResult | None = None
    all_citations = []
    provider_audit: list[dict] = []

    for provider in providers:
        result = await provider.verify(claim, context)
        provider_audit.append(
            {
                "provider_id": result.provider_id,
                "status": result.status,
                "severity": result.severity,
                "confidence": result.confidence,
            }
        )
        all_citations.extend(result.citations)
        if merged is None or _SEVERITY_ORDER[result.severity] > _SEVERITY_ORDER[merged.severity]:
            merged = result
        elif (
            merged is not None
            and _SEVERITY_ORDER[result.severity] == _SEVERITY_ORDER[merged.severity]
        ):
            if result.confidence > merged.confidence:
                merged = result

    if merged is None:
        merged = ProviderResult(
            status="skipped",
            severity="pass",
            confidence=0.0,
            summary="No providers ran",
            proposed_correction=None,
            citations=[],
            provider_id=settings.fact_check_provider,
        )

    merged.citations = _dedupe_citations(all_citations)
    merged.summary = merged.summary or "Verification complete"
    return merged


def _dedupe_citations(citations: list) -> list:
    seen: set[tuple[str, str]] = set()
    unique = []
    for c in citations:
        key = (c.provider_id, c.url)
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)
    return unique
