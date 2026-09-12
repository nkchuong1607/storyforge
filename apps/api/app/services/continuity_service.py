"""Continuity check, reports, and overrides."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    ChapterLockedError,
    NotFoundError,
    ValidationAppError,
)
from app.models.chapter import Chapter
from app.models.continuity import ContinuityOverride, ContinuityReport
from app.models.enums import ChapterStatus, ContinuitySeverity
from app.models.project import Project
from app.repositories.beat import BeatRepository
from app.repositories.bible import BibleRepository
from app.repositories.chapter import ChapterRepository
from app.repositories.character import CharacterRepository
from app.repositories.continuity import ContinuityRepository
from app.repositories.ledger import LedgerRepository
from app.repositories.prose import ProseRepository
from app.repositories.twist import TwistRepository
from app.schemas.continuity import (
    ContinuityCheckRequest,
    ContinuityIssue,
    ContinuityOverrideCreateRequest,
    StateDiff,
)
from app.schemas.continuity import (
    ContinuityOverride as ContinuityOverrideSchema,
)
from app.schemas.continuity import (
    ContinuityReport as ContinuityReportSchema,
)
from app.services.chapter_status import is_chapter_locked
from app.services.continuity.engine import RULE_PACK_VERSION, run_continuity_checks
from app.services.continuity.foreshadow import (
    ForeshadowPayoffContext,
    ForeshadowPlantContext,
    ForeshadowTwistContext,
    run_foreshadow_checks,
)


class ContinuityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.continuity = ContinuityRepository(session)
        self.prose = ProseRepository(session)
        self.chapters = ChapterRepository(session)
        self.beats = BeatRepository(session)
        self.bible = BibleRepository(session)
        self.characters = CharacterRepository(session)
        self.ledger = LedgerRepository(session)
        self.twists = TwistRepository(session)

    def _report_schema(self, report: ContinuityReport) -> ContinuityReportSchema:
        return ContinuityReportSchema(
            report_id=report.id,
            chapter_id=report.chapter_id,
            prose_version=report.prose_version,
            result=report.result,
            stats=report.stats_json,
            issues=[ContinuityIssue.model_validate(i) for i in report.issues_json],
            state_diff=StateDiff.model_validate(report.state_diff_json),
            created_at=report.created_at,
        )

    async def _ledger_tail(self, project_id: uuid.UUID) -> list[dict]:
        events = await self.ledger.list_settled_for_project(project_id)
        return [
            {
                "entity_id": str(e.entity_id),
                "entity_type": e.entity_type.value,
                "event_type": e.event_type.value,
                "payload": e.payload,
            }
            for e in events
        ]

    async def _resolve_prose(self, chapter: Chapter, prose_version: int | None):
        if prose_version is not None:
            row = await self.prose.get_version(chapter.id, prose_version)
        else:
            row = await self.prose.get_latest(chapter.id)
        if row is None:
            raise NotFoundError(message="Prose version not found")
        return row

    async def run_check(
        self,
        project: Project,
        chapter: Chapter,
        user_id: uuid.UUID,
        payload: ContinuityCheckRequest | None = None,
    ) -> ContinuityReportSchema:
        if is_chapter_locked(chapter.status):
            raise ChapterLockedError()

        prose_version = payload.prose_version if payload else None
        prose_row = await self._resolve_prose(chapter, prose_version)

        bible_version = chapter.bible_version_at_draft
        if bible_version is None:
            bible_version = project.bible_version_current
        bible_row = await self.bible.get_version(project.id, bible_version)
        snapshot = bible_row.snapshot_json if bible_row else {"entries": []}

        characters = await self.characters.list_all_for_project(project.id)
        staging = await self.bible.list_all_staging(project.id)
        beat_rows = await self.beats.list_for_chapter(chapter.id)
        beats = [{"summary": b.summary, "beat_key": b.beat_key} for b in beat_rows]
        overrides = await self.continuity.active_override_fingerprints(chapter.id)

        payoff_rows = await self.twists.list_payoffs_with_twists_for_chapter(project.id, chapter.id)
        all_plants = await self.twists.list_plants_for_project(project.id)
        all_twists = await self.twists.list_all_plans(project.id, include_abandoned=True)

        chapter_numbers: dict[uuid.UUID, int] = {}
        for plant in all_plants:
            if plant.chapter_id not in chapter_numbers:
                ch = await self.chapters.get(project.id, plant.chapter_id)
                if ch:
                    chapter_numbers[plant.chapter_id] = ch.number

        foreshadow_plants = [
            ForeshadowPlantContext(
                plant_id=p.id,
                twist_id=p.twist_id,
                chapter_id=p.chapter_id,
                chapter_number=chapter_numbers.get(p.chapter_id, 999),
            )
            for p in all_plants
        ]
        foreshadow_payoffs: list[ForeshadowPayoffContext] = []
        for payoff, twist in payoff_rows:
            target_ch = await self.chapters.get(project.id, payoff.target_chapter_id)
            if target_ch is None:
                continue
            foreshadow_payoffs.append(
                ForeshadowPayoffContext(
                    payoff_id=payoff.id,
                    twist=ForeshadowTwistContext(
                        twist_id=twist.id,
                        title=twist.title,
                        secret_truth=twist.secret_truth,
                        status=twist.status,
                        constraints_json=dict(twist.constraints_json or {}),
                        genre_strictness=twist.genre_strictness,
                    ),
                    target_chapter_id=payoff.target_chapter_id,
                    target_chapter_number=target_ch.number,
                    min_plants=payoff.min_plants,
                    required_plant_ids=list(payoff.required_plant_ids or []),
                )
            )
        foreshadow_twists = [
            ForeshadowTwistContext(
                twist_id=t.id,
                title=t.title,
                secret_truth=t.secret_truth,
                status=t.status,
                constraints_json=dict(t.constraints_json or {}),
                genre_strictness=t.genre_strictness,
            )
            for t in all_twists
        ]
        foreshadow_raw = run_foreshadow_checks(
            chapter_id=chapter.id,
            chapter_number=chapter.number,
            prose=prose_row.content,
            genre_profile=project.genre_profile,
            payoffs=foreshadow_payoffs,
            plants=foreshadow_plants,
            all_twists=foreshadow_twists,
        )

        issues, state_diff, stats, result = run_continuity_checks(
            prose=prose_row.content,
            chapter_number=chapter.number,
            chapter_id=chapter.id,
            characters=characters,
            ledger_tail=await self._ledger_tail(project.id),
            staging_rows=staging,
            snapshot_json=snapshot,
            bible_version_current=project.bible_version_current,
            beats=beats,
            active_override_fingerprints=overrides,
            foreshadow_issues=foreshadow_raw,
        )

        report = ContinuityReport(
            project_id=project.id,
            chapter_id=chapter.id,
            prose_version=prose_row.version,
            result=result,
            issues_json=issues,
            state_diff_json=state_diff,
            stats_json=stats,
            rule_pack_version=RULE_PACK_VERSION,
            created_by=user_id,
        )
        created = await self.continuity.create_report(report)
        if chapter.status == ChapterStatus.drafting:
            chapter.status = ChapterStatus.reviewing
        await self.session.flush()
        await self.session.refresh(created)
        return self._report_schema(created)

    async def get_latest_report(self, chapter: Chapter) -> ContinuityReportSchema:
        report = await self.continuity.get_latest_report(chapter.id)
        if report is None:
            raise NotFoundError(message="No continuity report found")
        return self._report_schema(report)

    async def get_report(self, chapter: Chapter, report_id: uuid.UUID) -> ContinuityReportSchema:
        report = await self.continuity.get_report(chapter.id, report_id)
        if report is None:
            raise NotFoundError()
        return self._report_schema(report)

    async def create_override(
        self,
        project: Project,
        chapter: Chapter,
        user_id: uuid.UUID,
        payload: ContinuityOverrideCreateRequest,
    ) -> ContinuityOverrideSchema:
        report = await self.continuity.get_latest_report(chapter.id)
        if report is None:
            raise NotFoundError(message="No continuity report found")
        fingerprints = {i.get("fingerprint") for i in report.issues_json}
        if payload.issue_fingerprint not in fingerprints:
            raise ValidationAppError(message="Fingerprint not found in latest continuity report")
        issue = next(
            i for i in report.issues_json if i.get("fingerprint") == payload.issue_fingerprint
        )
        severity = ContinuitySeverity(issue.get("severity", "warn"))
        override = ContinuityOverride(
            project_id=project.id,
            chapter_id=chapter.id,
            issue_fingerprint=payload.issue_fingerprint,
            severity_at_override=severity,
            reason=payload.reason,
            report_id=report.id,
            created_by=user_id,
        )
        created = await self.continuity.create_override(override)
        await self.session.refresh(created)
        return ContinuityOverrideSchema.model_validate(created)

    async def get_state_diff(self, chapter: Chapter, prose_version: int | None = None) -> StateDiff:
        report = await self.continuity.get_latest_report(chapter.id)
        if report is not None:
            if prose_version is None or report.prose_version == prose_version:
                return StateDiff.model_validate(report.state_diff_json)
        if prose_version is not None:
            prose_row = await self.prose.get_version(chapter.id, prose_version)
        else:
            prose_row = await self.prose.get_latest(chapter.id)
        if prose_row is None:
            return StateDiff()
        beats = await self.beats.list_for_chapter(chapter.id)
        from app.services.continuity.engine import build_state_diff_stub

        characters = await self.characters.list_all_for_project(chapter.project_id)
        diff = build_state_diff_stub(
            prose=prose_row.content,
            characters=characters,
            beats=[{"summary": b.summary} for b in beats],
        )
        return StateDiff.model_validate(diff)
