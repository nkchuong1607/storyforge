"""Phase 11 craft pack checklist rules — deterministic first."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from app.models.enums import ContinuityCategory, ContinuitySeverity, GenreProfile
from app.services.continuity.engine import ContinuityIssue
from app.services.continuity.foreshadow import (
    ForeshadowPayoffContext,
    ForeshadowPlantContext,
    ForeshadowTwistContext,
    _genre_default_min,
    count_eligible_plants,
)

CRAFT_RULE_PACK_SUFFIX = "+craft-v1"

RED_HERRING_MARKERS = (
    "red herring",
    "nghi phạm giả",
    "man nghi",
    "false lead",
    "làm nhiễu",
)


@dataclass(frozen=True)
class CraftChecklistItem:
    item_id: str
    code: str
    continuity_category: str
    severity_default: str
    description: str


def parse_checklist(pack_json: dict[str, Any]) -> list[CraftChecklistItem]:
    raw = pack_json.get("checklist") or []
    items: list[CraftChecklistItem] = []
    if not isinstance(raw, list):
        return items
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        item_id = entry.get("id")
        code = entry.get("code")
        if not isinstance(item_id, str) or not isinstance(code, str):
            continue
        items.append(
            CraftChecklistItem(
                item_id=item_id,
                code=code,
                continuity_category=str(entry.get("continuity_category") or "craft"),
                severity_default=str(entry.get("severity_default") or "warn"),
                description=str(entry.get("description") or ""),
            )
        )
    return items


def _severity(level: str) -> str:
    if level == "fail":
        return ContinuitySeverity.FAIL.value
    if level == "pass":
        return ContinuitySeverity.PASS.value
    return ContinuitySeverity.WARN.value


def run_craft_checks(
    *,
    chapter_id: uuid.UUID,
    chapter_number: int,
    prose: str,
    genre_profile: GenreProfile,
    pack_json: dict[str, Any],
    payoffs: list[ForeshadowPayoffContext],
    plants: list[ForeshadowPlantContext],
    all_twists: list[ForeshadowTwistContext],
    genre_pack: dict[str, Any] | None = None,
) -> list[ContinuityIssue]:
    """Evaluate craft checklist when an active craft pack is bound."""
    checklist = parse_checklist(pack_json)
    codes = {item.code for item in checklist}
    issues: list[ContinuityIssue] = []
    prose_lower = prose.lower()
    min_plants_default = max(2, _genre_default_min(genre_profile, genre_pack))

    if "craft_mystery_clue_after_reveal" in codes:
        for payoff in payoffs:
            if payoff.target_chapter_number != chapter_number:
                continue
            prior_plants = count_eligible_plants(
                plants, payoff.twist.twist_id, payoff.target_chapter_number
            )
            if prior_plants == 0:
                issues.append(
                    ContinuityIssue(
                        fingerprint=(
                            f"foreshadow:{payoff.twist.twist_id}:"
                            f"craft_mystery_clue_after_reveal:{payoff.target_chapter_id}"
                        ),
                        severity=_severity("fail"),
                        category=ContinuityCategory.foreshadow.value,
                        code="craft_mystery_clue_after_reveal",
                        message=(
                            f'Payoff ch.{payoff.target_chapter_number} cho "{payoff.twist.title}" '
                            "thiếu clue plant trước reveal (craft pack)"
                        ),
                        chapter_refs=[payoff.target_chapter_number],
                        entity_ids=[str(payoff.twist.twist_id)],
                        evidence={
                            "twist_id": str(payoff.twist.twist_id),
                            "twist_title": payoff.twist.title,
                            "plant_count": prior_plants,
                            "craft_pack_id": pack_json.get("id"),
                        },
                    )
                )

    if "craft_mystery_insufficient_plants" in codes:
        for payoff in payoffs:
            if payoff.target_chapter_number != chapter_number:
                continue
            required = max(payoff.min_plants, min_plants_default)
            if required <= 0:
                continue
            count = count_eligible_plants(
                plants, payoff.twist.twist_id, payoff.target_chapter_number
            )
            if count < required:
                issues.append(
                    ContinuityIssue(
                        fingerprint=(
                            f"foreshadow:{payoff.twist.twist_id}:"
                            f"craft_mystery_insufficient_plants:{payoff.target_chapter_id}"
                        ),
                        severity=_severity("fail"),
                        category=ContinuityCategory.foreshadow.value,
                        code="craft_mystery_insufficient_plants",
                        message=(
                            f'Payoff ch.{payoff.target_chapter_number} cho "{payoff.twist.title}" '
                            f"thiếu plant fair-play (cần {required}, có {count})"
                        ),
                        chapter_refs=[payoff.target_chapter_number],
                        entity_ids=[str(payoff.twist.twist_id)],
                        evidence={
                            "twist_id": str(payoff.twist.twist_id),
                            "twist_title": payoff.twist.title,
                            "min_plants": required,
                            "plant_count": count,
                            "craft_pack_id": pack_json.get("id"),
                        },
                    )
                )

    if "craft_mystery_unlabeled_misdirection" in codes:
        if any(marker in prose_lower for marker in RED_HERRING_MARKERS):
            twists_no_misdirection = [t for t in all_twists if not (t.misdirection or "").strip()]
            for twist in twists_no_misdirection:
                issues.append(
                    ContinuityIssue(
                        fingerprint=(
                            f"craft:{twist.twist_id}:craft_mystery_unlabeled_misdirection:{chapter_id}"
                        ),
                        severity=_severity("warn"),
                        category=ContinuityCategory.craft.value,
                        code="craft_mystery_unlabeled_misdirection",
                        message=(
                            f"Misdirection trong prose ch.{chapter_number} chưa gắn "
                            f'nhãn cho twist "{twist.title}"'
                        ),
                        chapter_refs=[chapter_number],
                        entity_ids=[str(twist.twist_id)],
                        evidence={
                            "twist_id": str(twist.twist_id),
                            "twist_title": twist.title,
                            "craft_pack_id": pack_json.get("id"),
                        },
                    )
                )
                break

    if "craft_mystery_reader_spoiler" in codes:
        for twist in all_twists:
            secret = twist.secret_truth.strip()
            if not secret or secret.lower() not in prose_lower:
                continue
            walls = twist.constraints_json.get("knowledge_walls") or []
            if not isinstance(walls, list):
                continue
            for wall in walls:
                if not isinstance(wall, dict):
                    continue
                before_ch = wall.get("before_chapter")
                if isinstance(before_ch, int) and chapter_number < before_ch:
                    issues.append(
                        ContinuityIssue(
                            fingerprint=(
                                f"craft:{twist.twist_id}:craft_mystery_reader_spoiler:{chapter_id}"
                            ),
                            severity=_severity("warn"),
                            category=ContinuityCategory.craft.value,
                            code="craft_mystery_reader_spoiler",
                            message=(
                                f'Reader spoiler ch.{chapter_number} — secret của "{twist.title}" '
                                "xuất hiện trước knowledge wall"
                            ),
                            chapter_refs=[chapter_number],
                            entity_ids=[str(twist.twist_id)],
                            evidence={
                                "twist_id": str(twist.twist_id),
                                "twist_title": twist.title,
                                "before_chapter": before_ch,
                                "craft_pack_id": pack_json.get("id"),
                            },
                        )
                    )
                    break

    return issues
