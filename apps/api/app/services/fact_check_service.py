"""Fact-check run and claim action business logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.exceptions import (
    ClaimAlreadyPromotedError,
    ClaimNoCitationsError,
    ClaimNoProposedCorrectionError,
    FactCheckRunPendingError,
    NotFoundError,
    ValidationAppError,
)
from app.models.enums import (
    FactCheckRunStatus,
    FactClaimCategory,
    FactClaimDisposition,
    FactClaimSeverity,
    RealityAnchorsMode,
    ResearchNoteStatus,
)
from app.models.fact_check import FactCheckRun, FactClaim
from app.models.project import Project
from app.models.prose_version import ProseVersion
from app.models.research import ResearchNote
from app.repositories.fact_check import FactCheckRepository
from app.repositories.prose import ProseRepository
from app.repositories.reality_settings import RealitySettingsRepository
from app.repositories.research import ResearchRepository
from app.schemas.fact_check import (
    FactCheckRun as FactCheckRunSchema,
)
from app.schemas.fact_check import (
    FactCheckRunCreateRequest,
    FactCheckRunDetail,
    FactCheckRunSummary,
    FactClaimAcceptFixRequest,
    FactClaimAcceptFixResponse,
    FactClaimDispositionRequest,
    FactClaimPromoteEvidenceRequest,
    FactClaimPromoteEvidenceResponse,
    FactClaimSpan,
)
from app.schemas.fact_check import (
    FactCitation as FactCitationSchema,
)
from app.schemas.fact_check import (
    FactClaim as FactClaimSchema,
)
from app.services.fact_check.queue import get_fact_check_queue
from app.services.fact_check_processor import process_fact_check_run
from app.utils.pagination import PageParams, paginated


class FactCheckService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.fact_check = FactCheckRepository(session)
        self.prose = ProseRepository(session)
        self.reality = RealitySettingsRepository(session)
        self.research = ResearchRepository(session)
        self.settings = get_settings()

    def _claim_schema(self, claim: FactClaim, citations: list) -> FactClaimSchema:
        span = None
        if claim.span_start is not None and claim.span_end is not None:
            span = FactClaimSpan(
                start=claim.span_start,
                end=claim.span_end,
                excerpt=claim.span_excerpt,
            )
        return FactClaimSchema(
            id=claim.id,
            run_id=claim.run_id,
            project_id=claim.project_id,
            category=FactClaimCategory(claim.category),
            text=claim.text,
            normalized_text=claim.normalized_text,
            span=span,
            source_type=claim.source_type,
            source_research_note_id=claim.source_research_note_id,
            severity=FactClaimSeverity(claim.severity),
            confidence=claim.confidence,
            summary=claim.summary,
            proposed_correction=claim.proposed_correction,
            author_disposition=FactClaimDisposition(claim.author_disposition),
            disposition_at=claim.disposition_at,
            promoted_research_note_id=claim.promoted_research_note_id,
            citations=[FactCitationSchema.model_validate(c) for c in citations],
            created_at=claim.created_at,
        )

    def _run_schema(
        self, run: FactCheckRun, claims: list[FactClaimSchema] | None = None
    ) -> FactCheckRunDetail:
        summary = None
        if run.summary_json:
            summary = FactCheckRunSummary.model_validate(run.summary_json)
        detail = FactCheckRunDetail(
            id=run.id,
            project_id=run.project_id,
            chapter_id=run.chapter_id,
            prose_version_id=run.prose_version_id,
            requested_by_user_id=run.requested_by_user_id,
            status=FactCheckRunStatus(run.status),
            skipped_reason=run.skipped_reason,
            error_message=run.error_message,
            summary=summary,
            started_at=run.started_at,
            finished_at=run.finished_at,
            created_at=run.created_at,
            claims=claims or [],
        )
        return detail

    async def _load_run_detail(
        self, project_id: uuid.UUID, run: FactCheckRun
    ) -> FactCheckRunDetail:
        claims = await self.fact_check.list_claims_for_run(run.id)
        claim_ids = [c.id for c in claims]
        citations = await self.fact_check.list_citations_for_claims(claim_ids)
        citations_by_claim: dict[uuid.UUID, list] = {}
        for citation in citations:
            citations_by_claim.setdefault(citation.claim_id, []).append(citation)
        claim_schemas = [self._claim_schema(c, citations_by_claim.get(c.id, [])) for c in claims]
        return self._run_schema(run, claim_schemas)

    async def enqueue_run(
        self,
        project: Project,
        chapter_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: FactCheckRunCreateRequest | None,
    ) -> FactCheckRunDetail:
        request = payload or FactCheckRunCreateRequest()
        prose_row = None
        if request.prose_version_id:
            prose_row = await self.session.get(ProseVersion, request.prose_version_id)
            if (
                prose_row is None
                or prose_row.project_id != project.id
                or prose_row.chapter_id != chapter_id
            ):
                raise NotFoundError()
        else:
            prose_row = await self.prose.get_latest(chapter_id)
            if prose_row is None:
                raise NotFoundError(message="No prose version for chapter")

        pending = await self.fact_check.pending_run_for_prose(project.id, prose_row.id)
        if pending is not None:
            raise FactCheckRunPendingError()

        reality = await self.reality.ensure_settings(project.id)
        options = {
            "force_refresh": request.force_refresh,
            "categories": [c.value for c in request.categories] if request.categories else None,
        }

        run = FactCheckRun(
            project_id=project.id,
            chapter_id=chapter_id,
            prose_version_id=prose_row.id,
            requested_by_user_id=user_id,
            status=FactCheckRunStatus.pending.value,
            options_json=options,
        )
        created = await self.fact_check.create_run(run)
        await self.session.flush()

        if reality.reality_anchors == RealityAnchorsMode.off.value:
            created.status = FactCheckRunStatus.done.value
            created.skipped_reason = "reality_off"
            created.summary_json = {
                "total_claims": 0,
                "pass": 0,
                "warn": 0,
                "fail": 0,
                "skipped": 0,
            }
            created.finished_at = datetime.now(UTC)
            await self.session.flush()
            return self._run_schema(created, [])

        if self.settings.fact_check_sync:
            await process_fact_check_run(self.session, created.id)
        else:
            queue = get_fact_check_queue()
            queue.enqueue(created.id, project.id, chapter_id)

        await self.session.refresh(created)
        return await self._load_run_detail(project.id, created)

    async def list_runs(self, project: Project, chapter_id: uuid.UUID, page: PageParams):
        items, total = await self.fact_check.list_runs(project.id, chapter_id, page)
        schemas = [
            FactCheckRunSchema(
                id=r.id,
                project_id=r.project_id,
                chapter_id=r.chapter_id,
                prose_version_id=r.prose_version_id,
                requested_by_user_id=r.requested_by_user_id,
                status=FactCheckRunStatus(r.status),
                skipped_reason=r.skipped_reason,
                error_message=r.error_message,
                summary=FactCheckRunSummary.model_validate(r.summary_json)
                if r.summary_json
                else None,
                started_at=r.started_at,
                finished_at=r.finished_at,
                created_at=r.created_at,
            )
            for r in items
        ]
        return paginated(schemas, page.page, page.page_size, total)

    async def get_run(self, project: Project, run_id: uuid.UUID) -> FactCheckRunDetail:
        run = await self.fact_check.get_run(project.id, run_id)
        if run is None:
            raise NotFoundError()
        return await self._load_run_detail(project.id, run)

    async def set_disposition(
        self,
        project: Project,
        user_id: uuid.UUID,
        claim_id: uuid.UUID,
        payload: FactClaimDispositionRequest,
    ) -> FactClaimSchema:
        allowed = {
            FactClaimDisposition.open,
            FactClaimDisposition.intentional_fiction,
            FactClaimDisposition.dismissed,
        }
        if payload.disposition not in allowed:
            raise ValidationAppError(message="Invalid disposition for this endpoint")
        claim = await self.fact_check.get_claim(project.id, claim_id)
        if claim is None:
            raise NotFoundError()
        claim.author_disposition = payload.disposition.value
        claim.disposition_at = datetime.now(UTC)
        claim.disposition_by_user_id = user_id
        await self.session.flush()
        citations = await self.fact_check.list_citations_for_claims([claim.id])
        return self._claim_schema(claim, citations)

    async def accept_fix(
        self,
        project: Project,
        user_id: uuid.UUID,
        claim_id: uuid.UUID,
        payload: FactClaimAcceptFixRequest | None,
    ) -> FactClaimAcceptFixResponse:
        request = payload or FactClaimAcceptFixRequest()
        claim = await self.fact_check.get_claim(project.id, claim_id)
        if claim is None:
            raise NotFoundError()
        correction = request.correction_override or claim.proposed_correction
        if not correction:
            raise ClaimNoProposedCorrectionError()

        run = await self.fact_check.get_run(project.id, claim.run_id)
        if run is None:
            raise NotFoundError()

        handoff_payload = {
            "chapter_id": str(run.chapter_id),
            "prose_version_id": str(run.prose_version_id),
            "span": {"start": claim.span_start, "end": claim.span_end},
            "original_text": claim.text,
            "suggested_replacement": correction,
            "prompt_edit_prefill": (
                f"Replace the date with the historically accurate {correction}."
                if claim.category == FactClaimCategory.date.value
                else f"Apply suggested correction: {correction}"
            ),
        }
        claim.author_disposition = FactClaimDisposition.accepted_fix.value
        claim.disposition_at = datetime.now(UTC)
        claim.disposition_by_user_id = user_id
        await self.session.flush()
        return FactClaimAcceptFixResponse(
            claim_id=claim.id,
            handoff_target=request.handoff_target,
            handoff_payload=handoff_payload,
        )

    async def promote_evidence(
        self,
        project: Project,
        user_id: uuid.UUID,
        claim_id: uuid.UUID,
        payload: FactClaimPromoteEvidenceRequest | None,
    ) -> FactClaimPromoteEvidenceResponse:
        request = payload or FactClaimPromoteEvidenceRequest()
        claim = await self.fact_check.get_claim(project.id, claim_id)
        if claim is None:
            raise NotFoundError()
        if claim.promoted_research_note_id:
            note = await self.research.get_note(project.id, claim.promoted_research_note_id)
            if note:
                raise ClaimAlreadyPromotedError()
        citations = await self.fact_check.list_citations_for_claims([claim.id])
        if not citations:
            raise ClaimNoCitationsError()
        primary = citations[0]
        if request.citation_id:
            matched = next((c for c in citations if c.id == request.citation_id), None)
            if matched:
                primary = matched

        tags = list(request.tags or [])
        if "fact-check" not in tags:
            tags.append("fact-check")
        title = request.note_title or primary.title or claim.text
        body_md = f"**{primary.title}**\n\n{primary.snippet}\n\nSource: {primary.url}"
        if claim.span_excerpt:
            body_md += f"\n\nClaim excerpt: {claim.span_excerpt}"

        note = ResearchNote(
            project_id=project.id,
            title=title,
            body_md=body_md,
            source_url=primary.url,
            tags=tags,
            status=ResearchNoteStatus.active.value,
        )
        created = await self.research.create_note(note)
        claim.author_disposition = FactClaimDisposition.evidence_promoted.value
        claim.promoted_research_note_id = created.id
        claim.disposition_at = datetime.now(UTC)
        claim.disposition_by_user_id = user_id
        await self.session.flush()
        await self.session.refresh(created)
        return FactClaimPromoteEvidenceResponse(
            claim_id=claim.id,
            research_note_id=created.id,
            research_note={
                "id": str(created.id),
                "title": created.title,
                "body_md": created.body_md,
                "source_url": created.source_url,
                "tags": list(created.tags or []),
                "status": created.status,
            },
        )
