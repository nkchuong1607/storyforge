"""Phase 8 stakes continuity rules K1–K5 and act boundary helpers."""

from __future__ import annotations

import math
import uuid
from typing import Any

from app.models.act_structure_settings import ActStructureSettings
from app.models.enums import ContinuityCategory, ContinuitySeverity
from app.models.scene_beat import SceneBeat
from app.models.stakes_ledger_entry import StakesLedgerEntry
from app.services.continuity.engine import ContinuityIssue


def resolve_act_for_chapter(
    chapter_number: int,
    settings: ActStructureSettings,
    total_chapters: int | None = None,
) -> tuple[int, int, int]:
    """Return (act_number, start_chapter, end_chapter) for a chapter."""
    boundaries = settings.chapters_per_act or []
    if boundaries:
        for item in boundaries:
            act_num = int(item.get("act_number", 0))
            start = int(item.get("start_chapter", 0))
            end = int(item.get("end_chapter", 0))
            if start <= chapter_number <= end:
                return act_num, start, end
        if boundaries:
            last = boundaries[-1]
            return (
                int(last.get("act_number", 1)),
                int(last.get("start_chapter", 1)),
                int(last.get("end_chapter", chapter_number)),
            )

    act_count = settings.act_count or 3
    total = total_chapters or max(chapter_number, act_count)
    per_act = max(1, math.ceil(total / act_count))
    act_number = min(act_count, ((chapter_number - 1) // per_act) + 1)
    start = (act_number - 1) * per_act + 1
    end = min(act_number * per_act, total)
    return act_number, start, end


def build_stakes_ledger_proposals(
    *,
    beats: list[SceneBeat],
    entries: list[StakesLedgerEntry],
    chapter_id: uuid.UUID,
    act_number: int,
) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    max_stakes = max((b.stakes_level or 0 for b in beats), default=0)
    for entry in entries:
        if entry.act_number != act_number:
            continue
        if entry.status != "planned":
            continue
        if max_stakes >= entry.target_level - 1:
            proposals.append(
                {
                    "entry_id": str(entry.id),
                    "status": "planted",
                    "plant_chapter_id": str(chapter_id),
                    "target_level": entry.target_level,
                }
            )
    return proposals


def build_stakes_snapshot(entries: list[StakesLedgerEntry], settings: ActStructureSettings) -> dict:
    checkpoints = [
        {
            "id": str(e.id),
            "act_number": e.act_number,
            "checkpoint_key": e.checkpoint_key,
            "title": e.title,
            "target_level": e.target_level,
            "status": e.status,
        }
        for e in entries
        if e.status != "abandoned"
    ]
    peak = max((e.target_level for e in entries if e.status in ("planted", "resolved")), default=0)
    return {
        "act_count": settings.act_count,
        "current_act_peak_level": peak,
        "checkpoints": checkpoints,
    }


def run_stakes_checks(
    *,
    project_id: uuid.UUID,
    chapter_number: int,
    settings: ActStructureSettings,
    entries: list[StakesLedgerEntry],
    beats: list[SceneBeat],
    genre_pack: dict[str, Any],
    stakes_ledger_proposals: list[dict],
    total_chapters: int | None = None,
) -> list[ContinuityIssue]:
    if not settings.enabled:
        return []

    issues: list[ContinuityIssue] = []
    thresholds = genre_pack.get("thresholds") or {}
    strictness = (genre_pack.get("strictness") or {}).get("stakes", "standard")
    act_number, act_start, act_end = resolve_act_for_chapter(
        chapter_number, settings, total_chapters
    )

    act_entries = [e for e in entries if e.act_number == act_number]
    act_len = max(1, act_end - act_start + 1)
    middle_start = act_start + act_len // 4
    middle_end = act_end - act_len // 4
    window = settings.flat_middle_window_chapters

    if middle_start <= chapter_number <= middle_end:
        recent_start = max(middle_start, chapter_number - window + 1)
        escalated = any(
            e.status in ("planted", "resolved")
            for e in act_entries
            if e.plant_chapter_id is not None
        )
        if not escalated and act_entries:
            sev = ContinuitySeverity.WARN.value
            flat_threshold = thresholds.get("stakes_flat_middle", "warn")
            if strictness == "strict" or flat_threshold == "fail":
                sev = ContinuitySeverity.FAIL.value
            issues.append(
                ContinuityIssue(
                    fingerprint=f"stakes:{project_id}:flat_middle:act{act_number}:ch{chapter_number}",
                    severity=sev,
                    category=ContinuityCategory.stakes.value,
                    code="stakes_flat_middle",
                    message=f"Act {act_number} thiếu leo thang stakes ở giữa hồi",
                    chapter_refs=[chapter_number],
                    entity_ids=[],
                    evidence={
                        "act_number": act_number,
                        "window_start": recent_start,
                        "chapter_number": chapter_number,
                    },
                )
            )

    for entry in act_entries:
        if entry.status == "planted" and entry.plant_chapter_id:
            beat_stakes = [b.stakes_level for b in beats if b.stakes_level is not None]
            if beat_stakes and max(beat_stakes) < entry.target_level - 1:
                issues.append(
                    ContinuityIssue(
                        fingerprint=f"stakes:{entry.id}:plant_without_beat",
                        severity=ContinuitySeverity.WARN.value,
                        category=ContinuityCategory.stakes.value,
                        code="stakes_plant_without_beat_stakes",
                        message=f"Checkpoint {entry.checkpoint_key} planted nhưng beat stakes thấp",
                        chapter_refs=[chapter_number],
                        entity_ids=[str(entry.id)],
                        evidence={"target_level": entry.target_level},
                    )
                )

    if act_number > 1:
        prev_entries = [e for e in entries if e.act_number == act_number - 1]
        prev_act_max = max((e.target_level for e in prev_entries), default=0)
        curr_max = max((b.stakes_level or 0 for b in beats), default=0)
        if curr_max < prev_act_max and prev_act_max > 0:
            abandoned = any(e.status == "abandoned" for e in prev_entries)
            if not abandoned:
                issues.append(
                    ContinuityIssue(
                        fingerprint=f"stakes:{project_id}:regression:act{act_number}",
                        severity=ContinuitySeverity.WARN.value,
                        category=ContinuityCategory.stakes.value,
                        code="stakes_escalation_regression",
                        message="Stakes giảm so với act trước mà không có abandoned checkpoint",
                        chapter_refs=[chapter_number],
                        entity_ids=[],
                        evidence={"prev_max": prev_act_max, "curr_max": curr_max},
                    )
                )

    for entry in entries:
        if (
            entry.status == "planted"
            and entry.act_number < act_number
            and not entry.resolve_chapter_id
        ):
            sev = ContinuitySeverity.WARN.value
            unresolved_threshold = thresholds.get("stakes_unresolved_past_act", "warn")
            if strictness == "strict" or unresolved_threshold == "fail":
                sev = ContinuitySeverity.FAIL.value
            issues.append(
                ContinuityIssue(
                    fingerprint=f"stakes:{entry.id}:unresolved_past_act",
                    severity=sev,
                    category=ContinuityCategory.stakes.value,
                    code="stakes_unresolved_past_act",
                    message=f"Checkpoint {entry.checkpoint_key} planted ở act trước chưa resolve",
                    chapter_refs=[chapter_number],
                    entity_ids=[str(entry.id)],
                    evidence={"entry_act": entry.act_number, "current_act": act_number},
                )
            )

    act_target_max = max((e.target_level for e in act_entries), default=0)
    beat_max = max((b.stakes_level or 0 for b in beats), default=0)
    if beat_max > act_target_max + 1:
        has_checkpoint_proposal = any(
            p.get("status") == "planned" or p.get("target_level", 0) >= beat_max
            for p in stakes_ledger_proposals
        )
        if not has_checkpoint_proposal:
            issues.append(
                ContinuityIssue(
                    fingerprint=f"stakes:{project_id}:level_jump:act{act_number}",
                    severity=ContinuitySeverity.WARN.value,
                    category=ContinuityCategory.stakes.value,
                    code="stakes_level_jump_without_checkpoint",
                    message="Beat stakes vượt checkpoint mà không có proposal mới",
                    chapter_refs=[chapter_number],
                    entity_ids=[],
                    evidence={"beat_max": beat_max, "act_target_max": act_target_max},
                )
            )

    return issues
