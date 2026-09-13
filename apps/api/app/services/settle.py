"""Atomic chapter settle transaction."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    ContinuityCheckRequiredError,
    ContinuityFailBlocksSettleError,
    InvalidChapterStatusTransitionError,
    NotFoundError,
)
from app.models.bible import BibleVersion
from app.models.continuity import SettleIdempotencyKey
from app.models.enums import (
    ChapterStatus,
    ContinuitySeverity,
    LedgerEntityType,
    LedgerEventType,
)
from app.models.ledger_event import LedgerEvent
from app.models.psych_state import PsychState
from app.models.relationship_event import RelationshipEvent
from app.repositories.bible import BibleRepository
from app.repositories.character import CharacterRepository
from app.repositories.continuity import ContinuityRepository
from app.repositories.ledger import LedgerRepository
from app.repositories.power import PowerRepository
from app.repositories.psych_state import PsychStateRepository
from app.repositories.relationship import RelationshipRepository
from app.repositories.stakes import StakesRepository
from app.repositories.twist import TwistRepository
from app.schemas.continuity import SettleChapterRequest, SettleChapterResponse
from app.services.continuity.engine import _normalize_content, _snapshot_entries_map
from app.services.continuity.power import build_power_snapshot
from app.services.continuity.relationship import compute_intensity
from app.services.continuity.stakes import build_stakes_snapshot
from app.utils.psyche_validation import merge_psyche_card


class SettleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.bible = BibleRepository(session)
        self.continuity = ContinuityRepository(session)
        self.ledger = LedgerRepository(session)
        self.twists = TwistRepository(session)
        self.characters = CharacterRepository(session)
        self.psych_states = PsychStateRepository(session)
        self.power = PowerRepository(session)
        self.relationships = RelationshipRepository(session)
        self.stakes = StakesRepository(session)

    async def _get_cached_response(
        self, chapter_id: uuid.UUID, idempotency_key: uuid.UUID | None
    ) -> SettleChapterResponse | None:
        if idempotency_key is None:
            return None
        cached = await self.continuity.get_idempotency(chapter_id, idempotency_key)
        if cached is None:
            return None
        return SettleChapterResponse.model_validate(cached.response_json)

    async def _save_idempotency(
        self,
        project_id: uuid.UUID,
        chapter_id: uuid.UUID,
        idempotency_key: uuid.UUID,
        response: SettleChapterResponse,
    ) -> None:
        record = SettleIdempotencyKey(
            project_id=project_id,
            chapter_id=chapter_id,
            idempotency_key=idempotency_key,
            response_json=response.model_dump(mode="json"),
        )
        await self.continuity.save_idempotency(record)

    def _merge_staging_into_snapshot(self, snapshot_json: dict, staging_rows: list) -> dict:
        merged = dict(snapshot_json)
        entry_map = _snapshot_entries_map(merged)
        for row in staging_rows:
            entry_map[row.entry_key] = {
                "entry_key": row.entry_key,
                "section": row.section.value,
                "title": row.title,
                "content_md": row.content_md,
                "metadata": row.metadata_ or {},
            }
        merged["entries"] = list(entry_map.values())
        return merged

    async def _reconcile_staging(
        self, project_id: uuid.UUID, new_snapshot: dict, new_version: int
    ) -> None:
        staging_rows = await self.bible.list_all_staging(project_id)
        settled_map = _snapshot_entries_map(new_snapshot)
        for row in staging_rows:
            settled_entry = settled_map.get(row.entry_key)
            if settled_entry is None:
                continue
            if _normalize_content(row.content_md) == _normalize_content(
                settled_entry.get("content_md", "")
            ):
                await self.bible.delete_staging_entry(row)
            elif row.base_bible_version < new_version:
                continue

    async def settle_chapter(
        self,
        project,
        chapter,
        payload: SettleChapterRequest | None,
        idempotency_key: uuid.UUID | None,
    ) -> SettleChapterResponse:
        cached = await self._get_cached_response(chapter.id, idempotency_key)
        if cached is not None:
            return cached

        if chapter.status != ChapterStatus.reviewing:
            raise InvalidChapterStatusTransitionError(
                "Chapter must be in reviewing status to settle"
            )

        request = payload or SettleChapterRequest()
        if not request.approve_state_diff:
            raise ContinuityCheckRequiredError(message="State diff approval required for settle")

        if request.report_id is not None:
            report = await self.continuity.get_report(chapter.id, request.report_id)
        else:
            report = await self.continuity.get_latest_report(chapter.id)
        if report is None:
            raise ContinuityCheckRequiredError()

        overrides = await self.continuity.active_override_fingerprints(chapter.id)
        fail_issues = [
            issue
            for issue in report.issues_json
            if issue.get("severity") == ContinuitySeverity.FAIL.value
            and issue.get("fingerprint") not in overrides
        ]
        if fail_issues:
            raise ContinuityFailBlocksSettleError(
                details=[
                    {"fingerprint": i.get("fingerprint"), "code": i.get("code")}
                    for i in fail_issues
                ]
            )

        bible_before = project.bible_version_current
        current_bible = await self.bible.get_version(project.id, bible_before)
        if current_bible is None:
            raise NotFoundError(message="Current bible version not found")

        state_diff = report.state_diff_json or {}
        staging_rows = await self.bible.list_all_staging(project.id)
        merged_snapshot = self._merge_staging_into_snapshot(
            current_bible.snapshot_json, staging_rows
        )
        power_settings = await self.power.ensure_settings(project.id)
        if bool(getattr(power_settings, "enabled", False)) or state_diff.get(
            "power_system_snapshot_patch"
        ):
            power_ranks = await self.power.list_ranks(project.id)
            power_techniques = await self.power.list_techniques(project.id)
            world = dict(merged_snapshot.get("world") or {})
            world["power_system"] = build_power_snapshot(
                power_settings, power_ranks, power_techniques
            )
            merged_snapshot["world"] = world

        stakes_settings = await self.stakes.ensure_settings(project.id)
        stakes_entries = await self.stakes.list_entries(project.id)
        if stakes_settings.enabled or state_diff.get("stakes_ledger_proposals"):
            world = dict(merged_snapshot.get("world") or {})
            world["stakes"] = build_stakes_snapshot(stakes_entries, stakes_settings)
            merged_snapshot["world"] = world

        for candidate in state_diff.get("bible_patch_candidates", []):
            path = candidate.get("path")
            op = candidate.get("op")
            if path == "world.scene_structure_summary" and op == "merge":
                world = dict(merged_snapshot.get("world") or {})
                existing = dict(world.get("scene_structure_summary") or {})
                value = candidate.get("value") or {}
                if isinstance(value, dict):
                    existing.update(value)
                world["scene_structure_summary"] = existing
                merged_snapshot["world"] = world
            elif candidate.get("path") == "world.stakes" and candidate.get("op") == "replace":
                world = dict(merged_snapshot.get("world") or {})
                world["stakes"] = candidate.get("value") or {}
                merged_snapshot["world"] = world

        bible_after = bible_before + 1
        now = datetime.now(UTC)
        ledger_proposals = state_diff.get("ledger_proposals", [])
        ledger_count = 0
        psych_count = 0
        relationship_count = 0
        stakes_count = 0
        snapshot_includes: list[str] = []
        if merged_snapshot.get("world", {}).get("stakes"):
            snapshot_includes.append("world.stakes")
        if merged_snapshot.get("world", {}).get("scene_structure_summary"):
            snapshot_includes.append("world.scene_structure_summary")

        for proposal in ledger_proposals:
            entity_type = LedgerEntityType(proposal.get("entity_type", "character"))
            raw_event_type = proposal.get("event_type", "status_change")
            try:
                event_type = LedgerEventType(raw_event_type)
            except ValueError:
                continue
            event = LedgerEvent(
                project_id=project.id,
                entity_type=entity_type,
                entity_id=uuid.UUID(proposal["entity_id"]),
                event_type=event_type,
                payload=proposal.get("payload", {}),
                chapter_id=chapter.id,
                chapter_number=chapter.number,
                prose_version=report.prose_version,
                settled_at=now,
            )
            await self.ledger.create(event)
            ledger_count += 1

        for candidate in state_diff.get("bible_patch_candidates", []):
            if candidate.get("action") == "promote_from_staging":
                event = LedgerEvent(
                    project_id=project.id,
                    entity_type=LedgerEntityType.character,
                    entity_id=uuid.uuid4(),
                    event_type=LedgerEventType.bible_promote,
                    payload={
                        "entry_key": candidate.get("entry_key"),
                        "staging_id": candidate.get("staging_id"),
                    },
                    chapter_id=chapter.id,
                    chapter_number=chapter.number,
                    prose_version=report.prose_version,
                    settled_at=now,
                )
                await self.ledger.create(event)
                ledger_count += 1

        for patch_proposal in state_diff.get("psyche_card_patches", []):
            character_id = uuid.UUID(patch_proposal["character_id"])
            character = await self.characters.get_by_id(project.id, character_id)
            if character is None:
                continue
            character.psyche_card = merge_psyche_card(
                character.psyche_card, patch_proposal.get("patch", {})
            )

        for proposal in state_diff.get("psych_state_proposals", []):
            character_id = uuid.UUID(proposal["character_id"])
            proposal_chapter_id = uuid.UUID(proposal.get("chapter_id", chapter.id))
            if proposal_chapter_id != chapter.id:
                continue
            psych_state = PsychState(
                project_id=project.id,
                character_id=character_id,
                chapter_id=chapter.id,
                stress_level=int(proposal.get("stress_level", 0)),
                dominant_emotion=str(proposal.get("dominant_emotion", "")),
                active_goal=str(proposal.get("active_goal", "")),
                belief_updates=list(proposal.get("belief_updates", [])),
                relationship_stance=list(proposal.get("relationship_stance", [])),
                value_pressure=proposal.get("value_pressure"),
                arc_beat=proposal.get("arc_beat"),
                trigger_event_refs=list(proposal.get("trigger_event_refs", [])),
                settled_at=now,
                created_at=now,
            )
            await self.psych_states.create(psych_state)
            psych_count += 1

        for proposal in state_diff.get("relationship_event_proposals", []):
            rel_id = uuid.UUID(proposal["relationship_id"])
            rel = await self.relationships.get(project.id, rel_id)
            if rel is None:
                continue
            settled = [
                e
                for e in await self.relationships.list_events(project.id, rel_id)
                if e.settled_at is not None
            ]
            intensity_after = compute_intensity(
                rel.baseline_intensity,
                settled,
            ) + int(proposal.get("intensity_delta", 0))
            intensity_after = max(-5, min(5, intensity_after))
            rel_event = RelationshipEvent(
                project_id=project.id,
                relationship_id=rel_id,
                event_type=str(proposal.get("event_type", "relationship_change")),
                intensity_delta=int(proposal.get("intensity_delta", 0)),
                intensity_after=intensity_after,
                relation_type_after=proposal.get("relation_type_after"),
                payload=proposal.get("payload") or {},
                chapter_id=chapter.id,
                chapter_number=chapter.number,
                prose_version=report.prose_version,
                settled_at=now,
            )
            await self.relationships.create_event(rel_event)
            relationship_count += 1

            ledger_event = LedgerEvent(
                project_id=project.id,
                entity_type=LedgerEntityType.relationship,
                entity_id=rel_id,
                event_type=LedgerEventType.relationship_change,
                payload={
                    "intensity_delta": proposal.get("intensity_delta", 0),
                    "intensity_after": intensity_after,
                    "relation_type_after": proposal.get("relation_type_after"),
                    "event_type": proposal.get("event_type"),
                },
                chapter_id=chapter.id,
                chapter_number=chapter.number,
                prose_version=report.prose_version,
                settled_at=now,
            )
            await self.ledger.create(ledger_event)
            ledger_count += 1

            if proposal.get("relation_type_after"):
                rel.relation_type = proposal["relation_type_after"]

        for proposal in state_diff.get("stakes_ledger_proposals", []):
            entry_id = uuid.UUID(proposal["entry_id"])
            entry = await self.stakes.get_entry(project.id, entry_id)
            if entry is None:
                continue
            from_level = entry.target_level
            if proposal.get("status"):
                entry.status = proposal["status"]
            if proposal.get("plant_chapter_id"):
                entry.plant_chapter_id = uuid.UUID(proposal["plant_chapter_id"])
            if proposal.get("resolve_chapter_id"):
                entry.resolve_chapter_id = uuid.UUID(proposal["resolve_chapter_id"])
            if proposal.get("target_level") is not None:
                entry.target_level = int(proposal["target_level"])
            entry.updated_at = now
            await self.stakes.update_entry(entry)
            stakes_count += 1

            to_level = int(proposal.get("target_level", entry.target_level))
            ledger_event = LedgerEvent(
                project_id=project.id,
                entity_type=LedgerEntityType.stakes,
                entity_id=entry_id,
                event_type=LedgerEventType.stakes_escalation,
                payload={
                    "act_number": entry.act_number,
                    "from_level": from_level,
                    "to_level": to_level,
                    "checkpoint_key": entry.checkpoint_key,
                },
                chapter_id=chapter.id,
                chapter_number=chapter.number,
                prose_version=report.prose_version,
                settled_at=now,
            )
            await self.ledger.create(ledger_event)
            ledger_count += 1

        await insert_bible_version(
            self.bible,
            project_id=project.id,
            version=bible_after,
            snapshot_json=merged_snapshot,
            settled_from_chapter_id=chapter.id,
        )
        project.bible_version_current = bible_after
        await self._reconcile_staging(project.id, merged_snapshot, bible_after)

        chapter.status = ChapterStatus.locked
        chapter.settled_at = now
        chapter.locked_at = now
        await self.twists.mark_payoffs_revealed_for_chapter(project.id, chapter.id, now)
        await self.session.flush()

        response = SettleChapterResponse(
            chapter_id=chapter.id,
            status=ChapterStatus.locked,
            bible_version_before=bible_before,
            bible_version_after=bible_after,
            ledger_events_appended=ledger_count,
            psych_states_appended=psych_count,
            relationship_events_appended=relationship_count,
            stakes_entries_updated=stakes_count,
            snapshot_includes=snapshot_includes,
            settled_at=now,
        )

        if idempotency_key is not None:
            await self._save_idempotency(project.id, chapter.id, idempotency_key, response)

        return response


async def insert_bible_version(
    bible_repo: BibleRepository,
    *,
    project_id: uuid.UUID,
    version: int,
    snapshot_json: dict,
    settled_from_chapter_id: uuid.UUID,
) -> BibleVersion:
    """Insert bible version — hook point for settle atomicity tests."""
    new_version = BibleVersion(
        project_id=project_id,
        version=version,
        snapshot_json=snapshot_json,
        settled_from_chapter_id=settled_from_chapter_id,
    )
    return await bible_repo.create_version(new_version)
