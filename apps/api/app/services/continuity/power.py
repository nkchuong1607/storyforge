"""Phase 6 power system continuity rules P1–P5."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from app.models.character import Character
from app.models.enums import ContinuityCategory, ContinuitySeverity
from app.models.power_system import PowerRank, PowerSystemSettings, PowerTechnique
from app.services.continuity.engine import ContinuityIssue


@dataclass(frozen=True)
class PowerRankContext:
    id: uuid.UUID
    rank_key: str
    display_name: str
    sort_order: int


@dataclass(frozen=True)
class PowerTechniqueContext:
    id: uuid.UUID
    technique_key: str
    display_name: str
    min_rank_id: uuid.UUID
    min_rank_sort_order: int
    sect_requirement: str | None


def _rank_map(ranks: list[PowerRankContext]) -> dict[uuid.UUID, PowerRankContext]:
    return {r.id: r for r in ranks}


def _character_rank_from_ledger(
    character_id: uuid.UUID,
    ledger_tail: list[dict],
    rank_by_id: dict[uuid.UUID, PowerRankContext],
) -> PowerRankContext | None:
    latest_rank_id: uuid.UUID | None = None
    for event in reversed(ledger_tail):
        if event.get("entity_id") != str(character_id):
            continue
        if event.get("event_type") != "cultivation_change":
            continue
        payload = event.get("payload", {})
        if isinstance(payload, dict) and payload.get("to_rank_id"):
            try:
                latest_rank_id = uuid.UUID(str(payload["to_rank_id"]))
            except ValueError:
                continue
            break
    if latest_rank_id is None:
        return None
    return rank_by_id.get(latest_rank_id)


def _claimed_rank_in_prose(prose: str, ranks: list[PowerRankContext]) -> PowerRankContext | None:
    """Highest rank label mentioned in prose (keyword stub)."""
    found: PowerRankContext | None = None
    for rank in ranks:
        if rank.display_name in prose or rank.rank_key.replace("_", " ") in prose.lower():
            if found is None or rank.sort_order > found.sort_order:
                found = rank
    return found


def _has_breakthrough_proposal(
    character_id: uuid.UUID,
    from_rank_id: uuid.UUID,
    to_rank_id: uuid.UUID,
    ledger_proposals: list[dict],
) -> bool:
    for proposal in ledger_proposals:
        if proposal.get("entity_id") != str(character_id):
            continue
        if proposal.get("event_type") != "cultivation_change":
            continue
        payload = proposal.get("payload", {})
        if not isinstance(payload, dict):
            continue
        if payload.get("breakthrough") and payload.get("to_rank_id") == str(to_rank_id):
            return True
        if payload.get("from_rank_id") == str(from_rank_id) and payload.get("to_rank_id") == str(
            to_rank_id
        ):
            if payload.get("breakthrough"):
                return True
    return False


def _technique_learned(
    character_id: uuid.UUID, technique_id: uuid.UUID, ledger_tail: list[dict]
) -> bool:
    for event in ledger_tail:
        if event.get("entity_id") != str(character_id):
            continue
        if event.get("event_type") != "technique_learned":
            continue
        payload = event.get("payload", {})
        if isinstance(payload, dict) and payload.get("technique_id") == str(technique_id):
            return True
    return False


def is_power_module_enabled(
    settings: PowerSystemSettings | None,
    genre_pack: dict[str, Any],
) -> bool:
    if settings is not None and not settings.enabled:
        return False
    modules = genre_pack.get("modules") or {}
    power_mod = modules.get("power_system") or {}
    return bool(power_mod.get("enabled", False))


def build_cultivation_proposals(
    *,
    prose: str,
    characters: list[Character],
    ranks: list[PowerRankContext],
    ledger_tail: list[dict],
) -> list[dict]:
    proposals: list[dict] = []
    rank_by_id = _rank_map(ranks)
    for character in characters:
        if character.display_name not in prose:
            continue
        claimed = _claimed_rank_in_prose(prose, ranks)
        if claimed is None:
            continue
        settled = _character_rank_from_ledger(character.id, ledger_tail, rank_by_id)
        from_rank = settled or ranks[0] if ranks else None
        if from_rank is None or claimed.id == from_rank.id:
            continue
        if claimed.sort_order <= from_rank.sort_order:
            continue
        proposals.append(
            {
                "entity_type": "character",
                "entity_id": str(character.id),
                "event_type": "cultivation_change",
                "payload": {
                    "from_rank_id": str(from_rank.id),
                    "to_rank_id": str(claimed.id),
                    "breakthrough": claimed.sort_order - from_rank.sort_order == 1,
                    "method": "extract_stub",
                },
                "confidence": "extract_stub",
            }
        )
    return proposals


def run_power_checks(
    *,
    prose: str,
    chapter_number: int,
    characters: list[Character],
    ranks: list[PowerRankContext],
    techniques: list[PowerTechniqueContext],
    settings: PowerSystemSettings,
    genre_pack: dict[str, Any],
    ledger_tail: list[dict],
    ledger_proposals: list[dict],
) -> list[ContinuityIssue]:
    if not is_power_module_enabled(settings, genre_pack):
        return []

    issues: list[ContinuityIssue] = []
    rank_by_id = _rank_map(ranks)
    strictness = (genre_pack.get("strictness") or {}).get("power", "strict")
    thresholds = genre_pack.get("thresholds") or {}
    threshold_jump = thresholds.get("power_max_rank_jump_per_chapter")
    if not isinstance(threshold_jump, int):
        threshold_jump = settings.max_rank_jump_per_chapter
    max_jump = min(settings.max_rank_jump_per_chapter, threshold_jump)
    priority_gap = settings.priority_gap
    default_upset = "fail" if strictness == "strict" else "warn"
    combat_upset = thresholds.get("power_combat_upset", default_upset)

    scene_chars = [c for c in characters if c.display_name in prose]

    for character in scene_chars:
        settled_rank = _character_rank_from_ledger(character.id, ledger_tail, rank_by_id)
        claimed_rank = _claimed_rank_in_prose(prose, ranks)

        if settled_rank and claimed_rank and claimed_rank.sort_order < settled_rank.sort_order:
            issues.append(
                ContinuityIssue(
                    fingerprint=(
                        f"power:{character.id}:regression:{settled_rank.id}:{claimed_rank.id}"
                    ),
                    severity=ContinuitySeverity.FAIL.value,
                    category=ContinuityCategory.power_system.value,
                    code="power_rank_regression",
                    message=(
                        f"{character.display_name} hồi lui cảnh giới "
                        f"{settled_rank.display_name} → {claimed_rank.display_name}"
                    ),
                    chapter_refs=[chapter_number],
                    entity_ids=[str(character.id)],
                    evidence={
                        "from_rank_id": str(settled_rank.id),
                        "to_rank_id": str(claimed_rank.id),
                    },
                )
            )

        if settled_rank and claimed_rank:
            jump = claimed_rank.sort_order - settled_rank.sort_order
            if jump > max_jump:
                has_breakthrough = _has_breakthrough_proposal(
                    character.id, settled_rank.id, claimed_rank.id, ledger_proposals
                )
                if settings.require_breakthrough_event and not has_breakthrough:
                    issues.append(
                        ContinuityIssue(
                            fingerprint=(
                                f"power:{character.id}:rank_jump:"
                                f"{settled_rank.id}:{claimed_rank.id}:ch{chapter_number}"
                            ),
                            severity=ContinuitySeverity.FAIL.value,
                            category=ContinuityCategory.power_system.value,
                            code="power_rank_jump_without_breakthrough",
                            message=(
                                f"{character.display_name} nhảy cảnh giới "
                                f"{settled_rank.display_name} → {claimed_rank.display_name} "
                                f"không có breakthrough (max {max_jump}/chương)"
                            ),
                            chapter_refs=[chapter_number],
                            entity_ids=[str(character.id)],
                            evidence={
                                "from_rank_id": str(settled_rank.id),
                                "to_rank_id": str(claimed_rank.id),
                                "max_jump": max_jump,
                            },
                        )
                    )

        effective_rank = settled_rank or (ranks[0] if ranks else None)
        for technique in techniques:
            if technique.display_name not in prose and technique.technique_key not in prose.lower():
                continue
            if effective_rank is None:
                continue
            if _technique_learned(character.id, technique.id, ledger_tail):
                continue
            if effective_rank.sort_order < technique.min_rank_sort_order:
                issues.append(
                    ContinuityIssue(
                        fingerprint=f"power:{character.id}:technique:{technique.id}",
                        severity=ContinuitySeverity.FAIL.value,
                        category=ContinuityCategory.power_system.value,
                        code="power_technique_ineligible",
                        message=(
                            f"{character.display_name} dùng {technique.display_name} "
                            f"chưa đủ cảnh giới"
                        ),
                        chapter_refs=[chapter_number],
                        entity_ids=[str(character.id)],
                        evidence={
                            "technique_id": str(technique.id),
                            "min_rank_id": str(technique.min_rank_id),
                        },
                    )
                )
            if technique.sect_requirement:
                sect_severity = (
                    ContinuitySeverity.FAIL.value
                    if strictness == "strict"
                    else ContinuitySeverity.WARN.value
                )
                if technique.sect_requirement not in prose:
                    issues.append(
                        ContinuityIssue(
                            fingerprint=(f"power:{character.id}:sect:{technique.id}"),
                            severity=sect_severity,
                            category=ContinuityCategory.power_system.value,
                            code="power_technique_sect_mismatch",
                            message=(
                                f"{character.display_name} — sect gate "
                                f"{technique.sect_requirement} chưa xác minh"
                            ),
                            chapter_refs=[chapter_number],
                            entity_ids=[str(character.id)],
                            evidence={"technique_id": str(technique.id)},
                        )
                    )

    combat_keywords = ("đánh bại", "hạ gục", "thua", "defeat")
    if any(kw in prose.lower() for kw in combat_keywords) and len(scene_chars) >= 2:
        winner = scene_chars[0]
        loser = scene_chars[1]
        w_rank = _character_rank_from_ledger(winner.id, ledger_tail, rank_by_id) or (
            ranks[0] if ranks else None
        )
        l_rank = _character_rank_from_ledger(loser.id, ledger_tail, rank_by_id) or (
            ranks[0] if ranks else None
        )
        if w_rank and l_rank and l_rank.sort_order - w_rank.sort_order > priority_gap:
            upset_severity = (
                ContinuitySeverity.FAIL.value
                if combat_upset == "fail"
                else ContinuitySeverity.WARN.value
            )
            issues.append(
                ContinuityIssue(
                    fingerprint=f"power:combat:{winner.id}:{loser.id}",
                    severity=upset_severity,
                    category=ContinuityCategory.power_system.value,
                    code="power_upset_without_justification",
                    message=(
                        f"{winner.display_name} đánh bại {loser.display_name} "
                        f"vượt priority_gap ({priority_gap})"
                    ),
                    chapter_refs=[chapter_number],
                    entity_ids=[str(winner.id), str(loser.id)],
                    evidence={"priority_gap": priority_gap},
                )
            )

    cultivation_terms = ("cảnh giới", "tu luyện", "đột phá", "breakthrough")
    if any(term in prose.lower() for term in cultivation_terms):
        known_labels = {r.display_name for r in ranks} | {r.rank_key for r in ranks}
        for term in cultivation_terms:
            labels_missing = ranks and not any(label in prose for label in known_labels)
            if term in prose.lower() and labels_missing:
                issues.append(
                    ContinuityIssue(
                        fingerprint=f"power:unknown_label:ch{chapter_number}",
                        severity=ContinuitySeverity.WARN.value,
                        category=ContinuityCategory.power_system.value,
                        code="power_unknown_rank_label",
                        message="Prose có thuật ngữ tu luyện nhưng không khớp thang cảnh giới",
                        chapter_refs=[chapter_number],
                        entity_ids=[],
                        evidence={"term": term},
                    )
                )
                break

    return issues


def ranks_to_context(ranks: list[PowerRank]) -> list[PowerRankContext]:
    return [
        PowerRankContext(
            id=r.id,
            rank_key=r.rank_key,
            display_name=r.display_name,
            sort_order=r.sort_order,
        )
        for r in ranks
    ]


def techniques_to_context(
    techniques: list[PowerTechnique], ranks: list[PowerRank]
) -> list[PowerTechniqueContext]:
    sort_by_id = {r.id: r.sort_order for r in ranks}
    return [
        PowerTechniqueContext(
            id=t.id,
            technique_key=t.technique_key,
            display_name=t.display_name,
            min_rank_id=t.min_rank_id,
            min_rank_sort_order=sort_by_id.get(t.min_rank_id, 0),
            sect_requirement=t.sect_requirement,
        )
        for t in techniques
    ]


def build_power_snapshot(
    settings: PowerSystemSettings,
    ranks: list[PowerRank],
    techniques: list[PowerTechnique],
) -> dict[str, Any]:
    return {
        "enabled": settings.enabled,
        "priority_gap": settings.priority_gap,
        "max_rank_jump_per_chapter": settings.max_rank_jump_per_chapter,
        "ranks": [
            {
                "id": str(r.id),
                "rank_key": r.rank_key,
                "display_name": r.display_name,
                "sort_order": r.sort_order,
                "sub_stages": r.sub_stages or [],
            }
            for r in ranks
        ],
        "techniques": [
            {
                "id": str(t.id),
                "technique_key": t.technique_key,
                "display_name": t.display_name,
                "min_rank_id": str(t.min_rank_id),
                "resource_cost": t.resource_cost or {},
            }
            for t in techniques
        ],
    }
