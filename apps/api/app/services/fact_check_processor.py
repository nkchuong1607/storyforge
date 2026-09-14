"""Inline fact-check run processing (sync test mode)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.enums import FactCheckRunStatus, FactClaimDisposition, RealityAnchorsMode
from app.models.fact_check import FactCheckRun, FactCitation, FactClaim
from app.models.prose_version import ProseVersion
from app.providers.fact_check.orchestrator import verify_claim
from app.providers.fact_check.types import ProviderContext, ResearchNoteSnapshot
from app.repositories.fact_check import FactCheckRepository
from app.repositories.reality_settings import RealitySettingsRepository
from app.repositories.research import ResearchRepository
from app.services.fact_check.extractor import extract_claims
from app.utils.pagination import PageParams


async def process_fact_check_run(session: AsyncSession, run_id: uuid.UUID) -> None:
    settings = get_settings()
    fact_repo = FactCheckRepository(session)
    reality_repo = RealitySettingsRepository(session)
    research_repo = ResearchRepository(session)

    run = await session.get(FactCheckRun, run_id)
    if run is None:
        return
    if run.status not in (FactCheckRunStatus.pending.value, FactCheckRunStatus.running.value):
        return

    run.status = FactCheckRunStatus.running.value
    run.started_at = datetime.now(UTC)
    await session.flush()

    try:
        reality = await reality_repo.ensure_settings(run.project_id)
        if reality.reality_anchors == RealityAnchorsMode.off.value:
            run.status = FactCheckRunStatus.done.value
            run.skipped_reason = "reality_off"
            run.summary_json = {
                "total_claims": 0,
                "pass": 0,
                "warn": 0,
                "fail": 0,
                "skipped": 0,
            }
            run.finished_at = datetime.now(UTC)
            await fact_repo.update_run(run)
            return

        prose_row = await session.get(ProseVersion, run.prose_version_id)
        if prose_row is None:
            run.status = FactCheckRunStatus.failed.value
            run.error_message = "Prose version not found"
            run.finished_at = datetime.now(UTC)
            await fact_repo.update_run(run)
            return

        options = run.options_json or {}
        force_refresh = bool(options.get("force_refresh", False))
        category_override = options.get("categories")

        research_snapshots: list[ResearchNoteSnapshot] = []
        if reality.include_research_notes:
            notes, _ = await research_repo.list_notes(
                run.project_id, status="active", tag=None, page=PageParams(page=1, page_size=100)
            )
            links = await research_repo.list_all_links_for_project(run.project_id)
            linked_note_ids = {link.note_id for link in links if link.chapter_id == run.chapter_id}
            for note in notes:
                if note.id in linked_note_ids or "fact-check" in (note.tags or []):
                    research_snapshots.append(
                        ResearchNoteSnapshot(
                            id=note.id,
                            title=note.title,
                            body_md=note.body_md,
                            source_url=note.source_url,
                            tags=list(note.tags or []),
                            updated_at=note.updated_at,
                        )
                    )

        drafts = extract_claims(
            prose=prose_row.content,
            reality_mode=reality.reality_anchors,
            enabled_categories=list(reality.enabled_categories or []),
            category_override=category_override,
            research_notes=research_snapshots,
            include_research_notes=reality.include_research_notes,
        )

        context = ProviderContext(
            project_id=run.project_id,
            research_notes=research_snapshots,
            http_enabled=settings.fact_check_http,
            force_refresh=force_refresh,
            cache_enabled=settings.fact_check_cache,
        )

        summary = {"total_claims": 0, "pass": 0, "warn": 0, "fail": 0, "skipped": 0}
        for draft in drafts:
            result = await verify_claim(
                draft,
                context,
                include_research=reality.include_research_notes,
            )
            claim = FactClaim(
                project_id=run.project_id,
                run_id=run.id,
                category=draft.category,
                text=draft.text,
                normalized_text=draft.normalized_text,
                span_start=draft.span_start,
                span_end=draft.span_end,
                span_excerpt=draft.span_excerpt,
                source_type=draft.source_type,
                source_research_note_id=draft.source_research_note_id,
                severity=result.severity,
                confidence=Decimal(str(round(result.confidence, 3))),
                summary=result.summary,
                proposed_correction=result.proposed_correction,
                author_disposition=FactClaimDisposition.open.value,
                provider_results_json=[
                    {"provider_id": result.provider_id, "status": result.status}
                ],
            )
            await fact_repo.create_claim(claim)

            for citation_draft in result.citations:
                citation = FactCitation(
                    project_id=run.project_id,
                    claim_id=claim.id,
                    provider_id=citation_draft.provider_id,
                    url=citation_draft.url,
                    title=citation_draft.title,
                    snippet=citation_draft.snippet,
                    retrieved_at=citation_draft.retrieved_at,
                    snapshot_json=citation_draft.snapshot_json,
                    research_note_id=citation_draft.research_note_id,
                )
                await fact_repo.create_citation(citation)

            summary["total_claims"] += 1
            summary[result.severity] = summary.get(result.severity, 0) + 1

        run.status = FactCheckRunStatus.done.value
        run.summary_json = summary
        run.finished_at = datetime.now(UTC)
        await fact_repo.update_run(run)
    except Exception as exc:
        run.status = FactCheckRunStatus.failed.value
        run.error_message = str(exc)
        run.finished_at = datetime.now(UTC)
        await fact_repo.update_run(run)
        raise
