"""Phase 8 scene structure continuity rules S1–S7."""

from __future__ import annotations

import uuid
from typing import Any

from app.models.character import Character
from app.models.enums import ContinuityCategory, ContinuitySeverity, SceneType
from app.models.scene_beat import SceneBeat
from app.models.scene_engine_settings import SceneEngineSettings
from app.services.continuity.engine import ContinuityIssue


def _scene_fingerprint(beat_id: uuid.UUID, code_suffix: str) -> str:
    return f"scene_structure:{beat_id}:{code_suffix}"


def _effective_strictness(settings: SceneEngineSettings, genre_pack: dict[str, Any]) -> str:
    pack_strict = (genre_pack.get("strictness") or {}).get("scene_structure")
    if pack_strict in ("relaxed", "standard", "strict"):
        return pack_strict
    return settings.strictness


def run_scene_structure_checks(
    *,
    beats: list[SceneBeat],
    chapter_number: int,
    settings: SceneEngineSettings,
    characters: list[Character],
    genre_pack: dict[str, Any],
    stakes_entries: list[Any] | None = None,
    relationship_event_proposals: list[dict] | None = None,
) -> list[ContinuityIssue]:
    if not settings.enabled:
        return []

    issues: list[ContinuityIssue] = []
    strictness = _effective_strictness(settings, genre_pack)
    character_ids = {c.id for c in characters}

    sort_orders = [b.sort_order for b in beats]
    beat_keys = [b.beat_key for b in beats]
    if len(sort_orders) != len(set(sort_orders)) or len(beat_keys) != len(set(beat_keys)):
        issues.append(
            ContinuityIssue(
                fingerprint=f"scene_structure:chapter:{chapter_number}:beat_order_invalid",
                severity=ContinuitySeverity.FAIL.value,
                category=ContinuityCategory.scene_structure.value,
                code="scene_beat_order_invalid",
                message=f"Beat order hoặc beat_key trùng lặp ở chương {chapter_number}",
                chapter_refs=[chapter_number],
                entity_ids=[],
                evidence={"sort_orders": sort_orders, "beat_keys": beat_keys},
            )
        )
    elif sort_orders:
        expected = list(range(min(sort_orders), min(sort_orders) + len(sort_orders)))
        if sorted(sort_orders) != expected:
            issues.append(
                ContinuityIssue(
                    fingerprint=f"scene_structure:chapter:{chapter_number}:beat_order_invalid",
                    severity=ContinuitySeverity.FAIL.value,
                    category=ContinuityCategory.scene_structure.value,
                    code="scene_beat_order_invalid",
                    message=f"sort_order không liên tục ở chương {chapter_number}",
                    chapter_refs=[chapter_number],
                    entity_ids=[],
                    evidence={"sort_orders": sort_orders},
                )
            )

    for beat in beats:
        active = beat.completed or bool(beat.summary.strip())
        goal = (beat.goal or "").strip()
        conflict = (beat.conflict or "").strip()
        outcome = (beat.outcome or "").strip()

        if active and not goal:
            sev = (
                ContinuitySeverity.FAIL.value
                if strictness == "strict"
                else ContinuitySeverity.WARN.value
            )
            issues.append(
                ContinuityIssue(
                    fingerprint=_scene_fingerprint(beat.id, "missing_goal"),
                    severity=sev,
                    category=ContinuityCategory.scene_structure.value,
                    code="scene_missing_goal",
                    message=f"Beat {beat.beat_key} thiếu goal",
                    chapter_refs=[chapter_number],
                    entity_ids=[str(beat.id)],
                    evidence={"beat_key": beat.beat_key, "sort_order": beat.sort_order},
                )
            )

        if (
            beat.completed
            and beat.scene_type in (SceneType.scene.value, SceneType.sequel.value)
            and not conflict
        ):
            sev = ContinuitySeverity.WARN.value
            if settings.require_conflict and strictness == "strict":
                sev = ContinuitySeverity.FAIL.value
            issues.append(
                ContinuityIssue(
                    fingerprint=_scene_fingerprint(beat.id, "missing_conflict"),
                    severity=sev,
                    category=ContinuityCategory.scene_structure.value,
                    code="scene_missing_conflict",
                    message=f"Beat {beat.beat_key} thiếu xung đột",
                    chapter_refs=[chapter_number],
                    entity_ids=[str(beat.id)],
                    evidence={"beat_key": beat.beat_key},
                )
            )

        if beat.completed and settings.require_outcome_on_complete and not outcome:
            issues.append(
                ContinuityIssue(
                    fingerprint=_scene_fingerprint(beat.id, "missing_outcome"),
                    severity=ContinuitySeverity.FAIL.value,
                    category=ContinuityCategory.scene_structure.value,
                    code="scene_missing_outcome",
                    message=f"Beat {beat.beat_key} đánh dấu hoàn thành nhưng thiếu outcome",
                    chapter_refs=[chapter_number],
                    entity_ids=[str(beat.id)],
                    evidence={"beat_key": beat.beat_key},
                )
            )

        if goal and len(goal) < settings.min_goal_length:
            issues.append(
                ContinuityIssue(
                    fingerprint=_scene_fingerprint(beat.id, "goal_too_short"),
                    severity=ContinuitySeverity.WARN.value,
                    category=ContinuityCategory.scene_structure.value,
                    code="scene_goal_too_short",
                    message=f"Beat {beat.beat_key} goal quá ngắn",
                    chapter_refs=[chapter_number],
                    entity_ids=[str(beat.id)],
                    evidence={
                        "goal_length": len(goal),
                        "min_goal_length": settings.min_goal_length,
                    },
                )
            )

        if beat.pov_character_id and beat.pov_character_id not in character_ids:
            issues.append(
                ContinuityIssue(
                    fingerprint=_scene_fingerprint(beat.id, "pov_unknown"),
                    severity=ContinuitySeverity.WARN.value,
                    category=ContinuityCategory.scene_structure.value,
                    code="scene_pov_unknown_character",
                    message=f"Beat {beat.beat_key} POV không thuộc cast",
                    chapter_refs=[chapter_number],
                    entity_ids=[str(beat.id)],
                    evidence={"pov_character_id": str(beat.pov_character_id)},
                )
            )

        if beat.stakes_level is not None and stakes_entries:
            act_targets = [
                e.target_level
                for e in stakes_entries
                if getattr(e, "status", "planned") not in ("abandoned",)
            ]
            if act_targets:
                nearest = min(act_targets, key=lambda t: abs(t - beat.stakes_level))
                if beat.stakes_level > nearest + 2:
                    has_escalation = any(
                        p.get("entity_type") == "stakes"
                        for p in (relationship_event_proposals or [])
                    )
                    if not has_escalation:
                        issues.append(
                            ContinuityIssue(
                                fingerprint=_scene_fingerprint(beat.id, "stakes_drift"),
                                severity=ContinuitySeverity.WARN.value,
                                category=ContinuityCategory.scene_structure.value,
                                code="scene_stakes_level_drift",
                                message=f"Beat {beat.beat_key} stakes_level vượt checkpoint act",
                                chapter_refs=[chapter_number],
                                entity_ids=[str(beat.id)],
                                evidence={
                                    "stakes_level": beat.stakes_level,
                                    "nearest_checkpoint": nearest,
                                },
                            )
                        )

    return issues


def build_scene_structure_summary(beats: list[SceneBeat]) -> dict[str, Any]:
    completed_with_outcome = sum(1 for b in beats if b.completed and (b.outcome or "").strip())
    stakes_levels = [b.stakes_level for b in beats if b.stakes_level is not None]
    avg_stakes = round(sum(stakes_levels) / len(stakes_levels), 1) if stakes_levels else 0.0
    return {
        "beats_with_outcome": completed_with_outcome,
        "avg_stakes_level": avg_stakes,
    }
