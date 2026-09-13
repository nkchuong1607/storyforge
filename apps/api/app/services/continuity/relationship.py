"""Phase 8 relationship arc continuity rules R-A1–R-A4."""

from __future__ import annotations

import uuid
from typing import Any

from app.models.character import Character
from app.models.enums import ContinuityCategory, ContinuitySeverity
from app.models.relationship import Relationship
from app.models.relationship_event import RelationshipEvent
from app.services.continuity.engine import ContinuityIssue

BETRAYAL_KEYWORDS = ("phản bội", "đâm sau lưng", "phản đối", "betrayal", "backstab")
ALLY_KEYWORDS = ("đồng minh", "cùng phe", "ally", "brother")


def normalize_pair(
    character_a_id: uuid.UUID, character_b_id: uuid.UUID
) -> tuple[uuid.UUID, uuid.UUID]:
    if character_a_id == character_b_id:
        raise ValueError("same character")
    if character_a_id < character_b_id:
        return character_a_id, character_b_id
    return character_b_id, character_a_id


def compute_intensity(baseline: int, settled_events: list[RelationshipEvent]) -> int:
    total = baseline + sum(e.intensity_delta for e in settled_events)
    return max(-5, min(5, total))


def build_relationship_event_proposals(
    *,
    prose: str,
    relationships: list[Relationship],
    characters: list[Character],
    chapter_id: uuid.UUID,
) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    prose_lower = prose.lower()
    if not any(kw in prose_lower for kw in BETRAYAL_KEYWORDS):
        return proposals

    char_by_id = {c.id: c for c in characters}
    for rel in relationships:
        name_a = char_by_id.get(rel.character_a_id)
        name_b = char_by_id.get(rel.character_b_id)
        if name_a is None or name_b is None:
            continue
        if name_a.display_name in prose and name_b.display_name in prose:
            proposals.append(
                {
                    "relationship_id": str(rel.id),
                    "event_type": "betrayal",
                    "intensity_delta": -3,
                    "relation_type_after": "enemy",
                    "payload": {
                        "trigger": "sect_betrayal",
                        "visibility": "public",
                        "keywords_matched": [kw for kw in BETRAYAL_KEYWORDS if kw in prose_lower],
                    },
                    "chapter_id": str(chapter_id),
                }
            )
    return proposals


def run_relationship_checks(
    *,
    prose: str,
    chapter_number: int,
    characters: list[Character],
    relationships: list[Relationship],
    settled_events: list[RelationshipEvent],
    relationship_event_proposals: list[dict],
    beats: list[Any],
) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []
    prose_lower = prose.lower()
    char_by_id = {c.id: c for c in characters}

    events_by_rel: dict[uuid.UUID, list[RelationshipEvent]] = {}
    for event in settled_events:
        events_by_rel.setdefault(event.relationship_id, []).append(event)

    rel_by_pair: dict[tuple[uuid.UUID, uuid.UUID], Relationship] = {}
    for rel in relationships:
        rel_by_pair[(rel.character_a_id, rel.character_b_id)] = rel

    if any(kw in prose_lower for kw in BETRAYAL_KEYWORDS):
        for rel in relationships:
            name_a = char_by_id.get(rel.character_a_id)
            name_b = char_by_id.get(rel.character_b_id)
            if name_a is None or name_b is None:
                continue
            if name_a.display_name not in prose or name_b.display_name not in prose:
                continue
            has_proposal = any(
                p.get("relationship_id") == str(rel.id) for p in relationship_event_proposals
            )
            if not has_proposal:
                issues.append(
                    ContinuityIssue(
                        fingerprint=f"relationship_arc:{rel.id}:intensity_jump_without_event",
                        severity=ContinuitySeverity.FAIL.value,
                        category=ContinuityCategory.relationship_arc.value,
                        code="relationship_intensity_jump_without_event",
                        message=(
                            f"Phản bội giữa {name_a.display_name} và {name_b.display_name} "
                            "chưa có relationship event trong state diff"
                        ),
                        chapter_refs=[chapter_number],
                        entity_ids=[str(rel.id)],
                        evidence={
                            "character_a_id": str(rel.character_a_id),
                            "character_b_id": str(rel.character_b_id),
                            "keywords_matched": [
                                kw for kw in BETRAYAL_KEYWORDS if kw in prose_lower
                            ],
                        },
                    )
                )

    for rel in relationships:
        events = events_by_rel.get(rel.id, [])
        if not events:
            continue
        latest = events[-1]
        type_after = latest.relation_type_after or rel.relation_type
        name_a = char_by_id.get(rel.character_a_id)
        name_b = char_by_id.get(rel.character_b_id)
        if name_a is None or name_b is None:
            continue
        if type_after == "enemy" and any(kw in prose_lower for kw in ALLY_KEYWORDS):
            if name_a.display_name in prose and name_b.display_name in prose:
                has_reconciliation = any(
                    p.get("relationship_id") == str(rel.id)
                    and p.get("event_type") == "reconciliation"
                    for p in relationship_event_proposals
                )
                if not has_reconciliation:
                    issues.append(
                        ContinuityIssue(
                            fingerprint=f"relationship_arc:{rel.id}:type_contradiction",
                            severity=ContinuitySeverity.WARN.value,
                            category=ContinuityCategory.relationship_arc.value,
                            code="relationship_type_contradiction",
                            message=(
                                f"Cặp {name_a.display_name}/{name_b.display_name} "
                                "đang enemy nhưng prose gợi ý đồng minh"
                            ),
                            chapter_refs=[chapter_number],
                            entity_ids=[str(rel.id)],
                            evidence={"relation_type_after": type_after},
                        )
                    )

        payload = latest.payload or {}
        if payload.get("visibility") == "secret":
            knows = payload.get("knows") or []
            for beat in beats:
                pov_id = getattr(beat, "pov_character_id", None)
                if pov_id and str(pov_id) not in knows:
                    if name_a.display_name in prose and name_b.display_name in prose:
                        issues.append(
                            ContinuityIssue(
                                fingerprint=f"relationship_arc:{rel.id}:secret_leak",
                                severity=ContinuitySeverity.WARN.value,
                                category=ContinuityCategory.relationship_arc.value,
                                code="relationship_secret_visibility_leak",
                                message="Quan hệ bí mật bị lộ qua POV không biết",
                                chapter_refs=[chapter_number],
                                entity_ids=[str(rel.id)],
                                evidence={"pov_character_id": str(pov_id)},
                            )
                        )

    pov_ids = {
        getattr(b, "pov_character_id", None) for b in beats if getattr(b, "pov_character_id", None)
    }
    t1_chars = [c for c in characters if c.tier >= 1]
    for i, char_a in enumerate(t1_chars):
        for char_b in t1_chars[i + 1 :]:
            if char_a.id not in pov_ids and char_b.id not in pov_ids:
                continue
            if char_a.display_name not in prose or char_b.display_name not in prose:
                continue
            try:
                a_id, b_id = normalize_pair(char_a.id, char_b.id)
            except ValueError:
                continue
            if (a_id, b_id) not in rel_by_pair:
                issues.append(
                    ContinuityIssue(
                        fingerprint=f"relationship_arc:pair:{a_id}:{b_id}:unregistered",
                        severity=ContinuitySeverity.WARN.value,
                        category=ContinuityCategory.relationship_arc.value,
                        code="relationship_unregistered_pair",
                        message=(
                            f"Cặp {char_a.display_name}/{char_b.display_name} "
                            "tương tác nhưng chưa đăng ký relationship"
                        ),
                        chapter_refs=[chapter_number],
                        entity_ids=[str(a_id), str(b_id)],
                        evidence={},
                    )
                )

    return issues
