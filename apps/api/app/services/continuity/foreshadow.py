"""Phase 4 foreshadow fairness rules (F1–F6)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from app.models.enums import ContinuityCategory, ContinuitySeverity, GenreProfile, TwistPlanStatus
from app.services.continuity.engine import ContinuityIssue

FORESHADOW_RULE_PACK_SUFFIX = "+foreshadow-v1"


@dataclass(frozen=True)
class ForeshadowTwistContext:
    twist_id: uuid.UUID
    title: str
    secret_truth: str
    status: TwistPlanStatus
    constraints_json: dict[str, Any]
    genre_strictness: str | None
    misdirection: str | None = None


@dataclass(frozen=True)
class ForeshadowPayoffContext:
    payoff_id: uuid.UUID
    twist: ForeshadowTwistContext
    target_chapter_id: uuid.UUID
    target_chapter_number: int
    min_plants: int
    required_plant_ids: list[uuid.UUID]


@dataclass(frozen=True)
class ForeshadowPlantContext:
    plant_id: uuid.UUID
    twist_id: uuid.UUID
    chapter_id: uuid.UUID
    chapter_number: int


def _is_strict(genre_profile: GenreProfile, twist: ForeshadowTwistContext) -> bool:
    if twist.genre_strictness == "strict":
        return True
    if twist.genre_strictness == "relaxed":
        return False
    return genre_profile == GenreProfile.mystery


def _genre_default_min(genre_profile: GenreProfile, genre_pack: dict | None = None) -> int:
    if genre_pack:
        thresholds = genre_pack.get("thresholds") or {}
        value = thresholds.get("foreshadow_min_plants_default")
        if isinstance(value, int):
            return value
    if genre_profile == GenreProfile.mystery:
        return 2
    return 1


def _payoff_without_plants_severity(genre_profile: GenreProfile, genre_pack: dict | None) -> bool:
    """Return True if payoff-without-plants should FAIL."""
    if genre_pack:
        thresholds = genre_pack.get("thresholds") or {}
        level = thresholds.get("foreshadow_payoff_without_plants")
        if level == "fail":
            return True
        if level == "warn":
            return False
        strictness = (genre_pack.get("strictness") or {}).get("foreshadow")
        if strictness == "strict":
            return True
        if strictness == "relaxed":
            return False
    return genre_profile == GenreProfile.mystery


def _constraints_min(constraints_json: dict[str, Any]) -> int:
    value = constraints_json.get("min_plants_before_payoff")
    if isinstance(value, int) and value >= 0:
        return value
    return 0


def _severity_for_gate(*, strict: bool) -> str:
    return ContinuitySeverity.FAIL.value if strict else ContinuitySeverity.WARN.value


def count_eligible_plants(
    plants: list[ForeshadowPlantContext],
    twist_id: uuid.UUID,
    target_chapter_number: int,
) -> int:
    return sum(
        1
        for plant in plants
        if plant.twist_id == twist_id and plant.chapter_number <= target_chapter_number
    )


def evaluate_payoff_fairness(
    *,
    payoff: ForeshadowPayoffContext,
    plants: list[ForeshadowPlantContext],
    genre_profile: GenreProfile,
) -> tuple[list[str], str]:
    """Return issue codes and fairness state for board display."""
    strict = _is_strict(genre_profile, payoff.twist)
    eligible = count_eligible_plants(plants, payoff.twist.twist_id, payoff.target_chapter_number)
    min_required = max(
        payoff.min_plants,
        _constraints_min(payoff.twist.constraints_json),
        _genre_default_min(genre_profile),
    )
    codes: list[str] = []
    if eligible < min_required:
        codes.append("foreshadow_payoff_without_plants")
        if eligible > 0 and payoff.min_plants > 0 and eligible < payoff.min_plants:
            codes.append("foreshadow_plant_count_below_minimum")
    if payoff.required_plant_ids:
        plant_ids = {p.plant_id for p in plants if p.twist_id == payoff.twist.twist_id}
        plant_chapters = {
            p.plant_id: p.chapter_number for p in plants if p.twist_id == payoff.twist.twist_id
        }
        for req_id in payoff.required_plant_ids:
            if req_id not in plant_ids:
                codes.append("foreshadow_required_plants_missing")
                break
            if plant_chapters.get(req_id, 999) > payoff.target_chapter_number:
                codes.append("foreshadow_required_plants_missing")
                break
    if not codes:
        return [], "ok"
    state = "fail" if strict else "warn"
    if any(c == "foreshadow_required_plants_missing" for c in codes):
        state = "fail"
    return codes, state


def run_foreshadow_checks(
    *,
    chapter_id: uuid.UUID,
    chapter_number: int,
    prose: str,
    genre_profile: GenreProfile,
    payoffs: list[ForeshadowPayoffContext],
    plants: list[ForeshadowPlantContext],
    all_twists: list[ForeshadowTwistContext],
    genre_pack: dict | None = None,
) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []

    for payoff in payoffs:
        twist = payoff.twist
        if twist.status in (TwistPlanStatus.abandoned, TwistPlanStatus.paid_off):
            continue
        strict = _is_strict(genre_profile, twist)
        if genre_pack and _payoff_without_plants_severity(genre_profile, genre_pack):
            strict = True
        eligible = count_eligible_plants(plants, twist.twist_id, payoff.target_chapter_number)
        min_required = max(
            payoff.min_plants,
            _constraints_min(twist.constraints_json),
            _genre_default_min(genre_profile, genre_pack),
        )

        if eligible < min_required:
            fail_on_payoff = _payoff_without_plants_severity(genre_profile, genre_pack)
            severity = (
                ContinuitySeverity.FAIL.value
                if fail_on_payoff or strict
                else ContinuitySeverity.WARN.value
            )
            code = (
                "foreshadow_plant_count_below_minimum"
                if eligible > 0 and payoff.min_plants > 0 and eligible < payoff.min_plants
                else "foreshadow_payoff_without_plants"
            )
            if eligible == 0:
                code = "foreshadow_payoff_without_plants"
            issues.append(
                ContinuityIssue(
                    fingerprint=(
                        f"foreshadow:{twist.twist_id}:payoff_without_plants:"
                        f"{payoff.target_chapter_id}"
                    ),
                    severity=severity,
                    category=ContinuityCategory.foreshadow.value,
                    code=code,
                    message=(
                        f'Payoff ch.{payoff.target_chapter_number} cho "{twist.title}" '
                        f"thiếu plant (cần {min_required}, có {eligible})"
                    ),
                    chapter_refs=[payoff.target_chapter_number],
                    entity_ids=[str(twist.twist_id)],
                    evidence={
                        "twist_id": str(twist.twist_id),
                        "twist_title": twist.title,
                        "min_plants": min_required,
                        "plant_count": eligible,
                        "payoff_id": str(payoff.payoff_id),
                    },
                )
            )

        if payoff.required_plant_ids:
            twist_plants = [p for p in plants if p.twist_id == twist.twist_id]
            plant_map = {p.plant_id: p for p in twist_plants}
            for req_id in payoff.required_plant_ids:
                plant = plant_map.get(req_id)
                if plant is None or plant.chapter_number > payoff.target_chapter_number:
                    issues.append(
                        ContinuityIssue(
                            fingerprint=(
                                f"foreshadow:{twist.twist_id}:required_plants_missing:{req_id}"
                            ),
                            severity=ContinuitySeverity.FAIL.value,
                            category=ContinuityCategory.foreshadow.value,
                            code="foreshadow_required_plants_missing",
                            message=(
                                f'Payoff ch.{payoff.target_chapter_number} cho "{twist.title}" '
                                "thiếu plant bắt buộc"
                            ),
                            chapter_refs=[payoff.target_chapter_number],
                            entity_ids=[str(twist.twist_id)],
                            evidence={
                                "twist_id": str(twist.twist_id),
                                "twist_title": twist.title,
                                "missing_plant_id": str(req_id),
                                "payoff_id": str(payoff.payoff_id),
                            },
                        )
                    )
                    break

        if twist.status == TwistPlanStatus.seeded and eligible == 0:
            issues.append(
                ContinuityIssue(
                    fingerprint=(f"foreshadow:{twist.twist_id}:unseeded_reveal:{chapter_id}"),
                    severity=ContinuitySeverity.FAIL.value,
                    category=ContinuityCategory.foreshadow.value,
                    code="foreshadow_unseeded_reveal",
                    message=(
                        f'Payoff ch.{payoff.target_chapter_number} cho "{twist.title}" '
                        "chưa có plant nào (unseeded reveal)"
                    ),
                    chapter_refs=[payoff.target_chapter_number],
                    entity_ids=[str(twist.twist_id)],
                    evidence={
                        "twist_id": str(twist.twist_id),
                        "twist_title": twist.title,
                        "payoff_id": str(payoff.payoff_id),
                    },
                )
            )

    for twist in all_twists:
        if twist.status in (TwistPlanStatus.abandoned, TwistPlanStatus.paid_off):
            continue
        if twist.secret_truth and twist.secret_truth in prose:
            issues.append(
                ContinuityIssue(
                    fingerprint=(
                        f"foreshadow:{twist.twist_id}:constrained_fact_leaked:{chapter_id}"
                    ),
                    severity=ContinuitySeverity.FAIL.value,
                    category=ContinuityCategory.foreshadow.value,
                    code="foreshadow_constrained_fact_leaked",
                    message=(
                        f'Prose có thể lộ bí mật của twist "{twist.title}" — '
                        "kiểm tra secret_truth trong draft"
                    ),
                    chapter_refs=[chapter_number],
                    entity_ids=[str(twist.twist_id)],
                    evidence={
                        "twist_id": str(twist.twist_id),
                        "twist_title": twist.title,
                    },
                )
            )

        knowledge_walls = twist.constraints_json.get("knowledge_walls") or []
        if isinstance(knowledge_walls, list):
            for wall in knowledge_walls:
                if not isinstance(wall, dict):
                    continue
                char_id = wall.get("character_id")
                before_ch = wall.get("must_not_know_before_chapter")
                if not char_id or not isinstance(before_ch, int):
                    continue
                if chapter_number >= before_ch:
                    continue
                marker = f"@{char_id}"
                if marker in prose and twist.secret_truth in prose:
                    issues.append(
                        ContinuityIssue(
                            fingerprint=(f"foreshadow:{twist.twist_id}:knowledge_wall:{char_id}"),
                            severity=ContinuitySeverity.WARN.value,
                            category=ContinuityCategory.foreshadow.value,
                            code="foreshadow_knowledge_wall",
                            message=(
                                f"Knowledge wall — nhân vật có thể biết sớm bí mật "
                                f'"{twist.title}" trước ch.{before_ch}'
                            ),
                            chapter_refs=[chapter_number],
                            entity_ids=[str(twist.twist_id), str(char_id)],
                            evidence={
                                "twist_id": str(twist.twist_id),
                                "twist_title": twist.title,
                                "character_id": str(char_id),
                                "must_not_know_before_chapter": before_ch,
                            },
                        )
                    )

    return issues
