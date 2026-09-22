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
from app.models.enums import ChapterStatus, ContinuitySeverity, RealityAnchorsMode
from app.models.project import Project
from app.repositories.beat import BeatRepository
from app.repositories.bible import BibleRepository
from app.repositories.chapter import ChapterRepository
from app.repositories.character import CharacterRepository
from app.repositories.continuity import ContinuityRepository
from app.repositories.craft_pack import CraftPackRepository
from app.repositories.fact_check import FactCheckRepository
from app.repositories.ledger import LedgerRepository
from app.repositories.power import PowerRepository
from app.repositories.prose import ProseRepository
from app.repositories.psych_state import PsychStateRepository
from app.repositories.reality_settings import RealitySettingsRepository
from app.repositories.relationship import RelationshipRepository
from app.repositories.research import ResearchRepository
from app.repositories.scene_engine import SceneEngineRepository
from app.repositories.series import SeriesRepository
from app.repositories.stakes import StakesRepository
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
from app.services.continuity.craft import run_craft_checks
from app.services.continuity.engine import RULE_PACK_VERSION, run_continuity_checks
from app.services.continuity.fact_check import run_fact_check_bridge
from app.services.continuity.foreshadow import (
    ForeshadowPayoffContext,
    ForeshadowPlantContext,
    ForeshadowTwistContext,
    run_foreshadow_checks,
)
from app.services.continuity.power import (
    build_cultivation_proposals,
    is_power_module_enabled,
    ranks_to_context,
    run_power_checks,
    techniques_to_context,
)
from app.services.continuity.psychology import (
    build_psych_state_proposals,
    run_psychology_checks,
)
from app.services.continuity.relationship import (
    build_relationship_event_proposals,
    run_relationship_checks,
)
from app.services.continuity.research import run_research_checks
from app.services.continuity.scene import build_scene_structure_summary, run_scene_structure_checks
from app.services.continuity.series_rules import inherited_keys_from_slice, run_series_checks
from app.services.continuity.stakes import (
    build_stakes_ledger_proposals,
    resolve_act_for_chapter,
    run_stakes_checks,
)
from app.services.genre_defaults import merged_genre_pack


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
        self.psych_states = PsychStateRepository(session)
        self.power = PowerRepository(session)
        self.scene_engine = SceneEngineRepository(session)
        self.relationships = RelationshipRepository(session)
        self.stakes = StakesRepository(session)
        self.research = ResearchRepository(session)
        self.series = SeriesRepository(session)
        self.reality = RealitySettingsRepository(session)
        self.fact_check = FactCheckRepository(session)
        self.craft_packs = CraftPackRepository(session)

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
        beats = [
            {
                "id": str(b.id),
                "summary": b.summary,
                "beat_key": b.beat_key,
                "completed": b.completed,
                "goal": b.goal,
                "conflict": b.conflict,
                "outcome": b.outcome,
                "stakes_level": b.stakes_level,
                "sort_order": b.sort_order,
                "pov_character_id": str(b.pov_character_id) if b.pov_character_id else None,
                "scene_type": b.scene_type,
            }
            for b in beat_rows
        ]
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
                        misdirection=twist.misdirection,
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
                misdirection=t.misdirection,
            )
            for t in all_twists
        ]
        genre_pack = merged_genre_pack(project.genre_rule_pack_json or {}, project.genre_profile)
        foreshadow_raw = run_foreshadow_checks(
            chapter_id=chapter.id,
            chapter_number=chapter.number,
            prose=prose_row.content,
            genre_profile=project.genre_profile,
            payoffs=foreshadow_payoffs,
            plants=foreshadow_plants,
            all_twists=foreshadow_twists,
            genre_pack=genre_pack,
        )

        scene_character_ids = [
            c.id for c in characters if c.display_name in prose_row.content and c.tier >= 2
        ]
        prior_map = await self.psych_states.list_latest_for_characters_before_chapter(
            project.id, scene_character_ids, chapter.number
        )
        prior_states = {cid: row[0] for cid, row in prior_map.items()}
        psych_proposals, psyche_patches = build_psych_state_proposals(
            prose=prose_row.content,
            characters=characters,
            beats=beats,
            chapter_id=chapter.id,
            prior_states=prior_states,
        )
        psychology_raw = run_psychology_checks(
            prose=prose_row.content,
            chapter_number=chapter.number,
            chapter_id=chapter.id,
            characters=characters,
            prior_states=prior_states,
            psych_state_proposals=psych_proposals,
        )

        ledger_tail = await self._ledger_tail(project.id)
        power_settings = await self.power.ensure_settings(project.id)
        power_ranks = await self.power.list_ranks(project.id)
        power_techniques = await self.power.list_techniques(project.id)
        rank_ctx = ranks_to_context(power_ranks)
        technique_ctx = techniques_to_context(power_techniques, power_ranks)
        power_enabled = is_power_module_enabled(power_settings, genre_pack)
        cultivation_proposals = (
            build_cultivation_proposals(
                prose=prose_row.content,
                characters=characters,
                ranks=rank_ctx,
                ledger_tail=ledger_tail,
            )
            if power_enabled
            else []
        )
        power_snapshot_patch = None
        if power_enabled and power_settings.enabled:
            power_snapshot_patch = {
                "action": "sync_staging_to_bible",
                "rank_count": len(power_ranks),
                "technique_count": len(power_techniques),
            }
        power_raw = (
            run_power_checks(
                prose=prose_row.content,
                chapter_number=chapter.number,
                characters=characters,
                ranks=rank_ctx,
                techniques=technique_ctx,
                settings=power_settings,
                genre_pack=genre_pack,
                ledger_tail=ledger_tail,
                ledger_proposals=cultivation_proposals,
            )
            if power_enabled
            else []
        )

        scene_settings = await self.scene_engine.ensure_settings(project.id)
        stakes_settings = await self.stakes.ensure_settings(project.id)
        stakes_entries = await self.stakes.list_entries(project.id)
        act_number, _, _ = resolve_act_for_chapter(chapter.number, stakes_settings)
        act_stakes_entries = [e for e in stakes_entries if e.act_number == act_number]

        all_relationships = await self.relationships.list_all_for_project(project.id)
        settled_rel_events = await self.relationships.list_settled_events_for_project(project.id)
        relationship_proposals = build_relationship_event_proposals(
            prose=prose_row.content,
            relationships=all_relationships,
            characters=characters,
            chapter_id=chapter.id,
        )
        stakes_proposals = build_stakes_ledger_proposals(
            beats=beat_rows,
            entries=act_stakes_entries,
            chapter_id=chapter.id,
            act_number=act_number,
        )

        scene_raw = run_scene_structure_checks(
            beats=beat_rows,
            chapter_number=chapter.number,
            settings=scene_settings,
            characters=characters,
            genre_pack=genre_pack,
            stakes_entries=act_stakes_entries,
            relationship_event_proposals=relationship_proposals,
        )
        relationship_raw = run_relationship_checks(
            prose=prose_row.content,
            chapter_number=chapter.number,
            characters=characters,
            relationships=all_relationships,
            settled_events=settled_rel_events,
            relationship_event_proposals=relationship_proposals,
            beats=beat_rows,
        )
        stakes_raw = run_stakes_checks(
            project_id=project.id,
            chapter_number=chapter.number,
            settings=stakes_settings,
            entries=stakes_entries,
            beats=beat_rows,
            genre_pack=genre_pack,
            stakes_ledger_proposals=stakes_proposals,
        )
        scene_summary = build_scene_structure_summary(beat_rows)

        research_links = await self.research.list_all_links_for_project(project.id)
        research_raw = run_research_checks(
            links=research_links,
            characters=characters,
            snapshot_json=snapshot,
        )

        slice_version = 0
        inherited_keys: set[str] = set()
        if project.series_id:
            latest_slice = await self.series.get_latest_slice(project.series_id)
            if latest_slice:
                slice_version = latest_slice.version
                inherited_keys = inherited_keys_from_slice(latest_slice.slice_json)
        series_raw = run_series_checks(
            project=project,
            slice_version=slice_version,
            staging_rows=staging,
            inherited_keys=inherited_keys,
        )

        fact_check_raw: list = []
        reality_settings = await self.reality.ensure_settings(project.id)
        if reality_settings.reality_anchors == RealityAnchorsMode.strict.value:
            bridge_claims = await self.fact_check.bridge_claims_for_chapter(project.id, chapter.id)
            fact_check_raw = run_fact_check_bridge(
                claims=bridge_claims,
                chapter_id=chapter.id,
            )

        craft_raw: list = []
        active_craft = await self.craft_packs.get_active_binding(project.id)
        if active_craft is not None:
            catalog = await self.craft_packs.get_catalog_pack(active_craft.craft_pack_id)
            if catalog is not None:
                craft_raw = run_craft_checks(
                    chapter_id=chapter.id,
                    chapter_number=chapter.number,
                    prose=prose_row.content,
                    genre_profile=project.genre_profile,
                    pack_json=catalog.pack_json,
                    payoffs=foreshadow_payoffs,
                    plants=foreshadow_plants,
                    all_twists=foreshadow_twists,
                    genre_pack=genre_pack,
                )

        for proposal in relationship_proposals:
            rel_id = proposal.get("relationship_id")
            if rel_id:
                proposal.setdefault(
                    "ledger_proposal",
                    {
                        "entity_type": "relationship",
                        "entity_id": rel_id,
                        "event_type": "relationship_change",
                        "payload": {
                            "intensity_delta": proposal.get("intensity_delta", 0),
                            "intensity_after": proposal.get("intensity_after"),
                            "relation_type_after": proposal.get("relation_type_after"),
                            "event_type": proposal.get("event_type"),
                        },
                    },
                )

        issues, state_diff, stats, result = run_continuity_checks(
            prose=prose_row.content,
            chapter_number=chapter.number,
            chapter_id=chapter.id,
            characters=characters,
            ledger_tail=ledger_tail,
            staging_rows=staging,
            snapshot_json=snapshot,
            bible_version_current=project.bible_version_current,
            beats=beats,
            active_override_fingerprints=overrides,
            foreshadow_issues=foreshadow_raw,
            psychology_issues=psychology_raw,
            psych_state_proposals=psych_proposals,
            psyche_card_patches=psyche_patches,
            power_issues=power_raw,
            cultivation_proposals=cultivation_proposals,
            power_snapshot_patch=power_snapshot_patch,
            power_module_enabled=power_enabled,
            scene_issues=scene_raw,
            relationship_issues=relationship_raw,
            stakes_issues=stakes_raw,
            relationship_event_proposals=relationship_proposals,
            stakes_ledger_proposals=stakes_proposals,
            scene_structure_summary=scene_summary,
            research_issues=research_raw,
            series_issues=series_raw,
            fact_check_issues=fact_check_raw,
            craft_issues=craft_raw,
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
        beat_payload = [
            {"id": str(b.id), "summary": b.summary, "beat_key": b.beat_key} for b in beats
        ]
        scene_character_ids = [
            c.id for c in characters if c.display_name in prose_row.content and c.tier >= 2
        ]
        prior_map = await self.psych_states.list_latest_for_characters_before_chapter(
            chapter.project_id, scene_character_ids, chapter.number
        )
        prior_states = {cid: row[0] for cid, row in prior_map.items()}
        psych_proposals, psyche_patches = build_psych_state_proposals(
            prose=prose_row.content,
            characters=characters,
            beats=beat_payload,
            chapter_id=chapter.id,
            prior_states=prior_states,
        )
        diff = build_state_diff_stub(
            prose=prose_row.content,
            characters=characters,
            beats=beat_payload,
            chapter_id=chapter.id,
            psych_state_proposals=psych_proposals,
            psyche_card_patches=psyche_patches,
        )
        return StateDiff.model_validate(diff)
