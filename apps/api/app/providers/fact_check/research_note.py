"""Research note evidence provider — reads author-supplied notes only."""

from __future__ import annotations

from datetime import UTC, datetime

from app.providers.fact_check.types import (
    CitationDraft,
    ClaimDraft,
    ProviderContext,
    ProviderResult,
)


class ResearchNoteEvidenceProvider:
    provider_id = "research_note"

    async def verify(self, claim: ClaimDraft, context: ProviderContext) -> ProviderResult:
        if not context.research_notes:
            return ProviderResult(
                status="skipped",
                severity="pass",
                confidence=0.0,
                summary="No linked research notes",
                proposed_correction=None,
                citations=[],
                provider_id=self.provider_id,
            )

        claim_tokens = set((claim.normalized_text or claim.text).lower().split())
        best_note = None
        best_overlap = 0
        for note in context.research_notes:
            body_tokens = set(note.body_md.lower().split())
            overlap = len(claim_tokens & body_tokens)
            if overlap > best_overlap:
                best_overlap = overlap
                best_note = note

        if best_note is None or best_overlap == 0:
            return ProviderResult(
                status="inconclusive",
                severity="warn",
                confidence=0.35,
                summary="No research note keyword overlap",
                proposed_correction=None,
                citations=[],
                provider_id=self.provider_id,
            )

        now = datetime.now(UTC)
        citation = CitationDraft(
            provider_id=self.provider_id,
            url=best_note.source_url or f"research://note/{best_note.id}",
            title=best_note.title,
            snippet=best_note.body_md[:200],
            retrieved_at=best_note.updated_at or now,
            snapshot_json={"note_id": str(best_note.id)},
            research_note_id=best_note.id,
        )
        return ProviderResult(
            status="verified",
            severity="pass",
            confidence=min(0.85, 0.5 + best_overlap * 0.05),
            summary=f"Matched research note: {best_note.title}",
            proposed_correction=None,
            citations=[citation],
            provider_id=self.provider_id,
        )
