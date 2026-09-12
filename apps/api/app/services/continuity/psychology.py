"""Phase 5 deterministic psychology / OOC rules (psychology-v1)."""

from __future__ import annotations

import hashlib
import re
import uuid
from typing import Any

from app.models.character import Character
from app.models.enums import ContinuityCategory, ContinuitySeverity
from app.models.psych_state import PsychState
from app.services.continuity.engine import ContinuityIssue

PSYCHOLOGY_RULE_PACK_SUFFIX = "+psychology-v1"

BOUNDARY_KEYWORD_MAP: dict[str, list[str]] = {
    "không giết vô tội": [r"giết.*vô tội", r"hạ sát dân thường", r"giết dân thường"],
    "không phản bội sư môn": [r"phản bội sư môn", r"phản sư"],
}

VALUE_JUMP_KEYWORDS: dict[str, list[str]] = {
    "gia đình": [r"bỏ rơi gia đình", r"phản bội gia đình", r"bỏ mặc gia đình"],
    "công lý": [r"bỏ qua công lý", r"phản công lý"],
    "sức mạnh": [r"phản bội.*sức mạnh"],
}

STRESS_KEYWORDS = ("tức giận", "giận dữ", "phẫn nộ", "stress", "căng thẳng")
BETRAYAL_KEYWORDS = ("phản bội", "nói dối", "lừa dối", "phản bội sư phụ")


def _boundary_hash(boundary: str) -> str:
    return hashlib.sha256(boundary.encode()).hexdigest()[:12]


def psych_fingerprint(
    character_id: uuid.UUID,
    code: str,
    suffix: str,
    chapter_id: uuid.UUID,
) -> str:
    return f"psych:{character_id}:{code}:{suffix}:{chapter_id}"


def character_applies_psychology_rules(character: Character) -> bool:
    if character.tier < 2:
        return False
    psyche = character.psyche_card or {}
    if not psyche or psyche == {}:
        return False
    return True


def _name_in_prose_window(prose: str, name: str, pattern: re.Pattern[str]) -> bool:
    if name not in prose:
        return False
    idx = prose.find(name)
    window = prose[max(0, idx - 80) : idx + len(name) + 120]
    return pattern.search(window) is not None


def check_ooc_moral_boundary(
    *,
    character: Character,
    prose: str,
    chapter_number: int,
    chapter_id: uuid.UUID,
    psych_state_proposals: list[dict[str, Any]] | None = None,
) -> ContinuityIssue | None:
    if not character_applies_psychology_rules(character):
        return None
    psyche = character.psyche_card or {}
    boundaries = psyche.get("moral_boundaries") or []
    if not boundaries:
        return None

    arc_flags = psyche.get("arc_flags") or {}
    allow_break = bool(arc_flags.get("allow_moral_break"))
    expected_beats = arc_flags.get("expected_arc_beats") or []
    current_proposal_arc = None
    if psych_state_proposals:
        for proposal in psych_state_proposals:
            if str(proposal.get("character_id")) == str(character.id):
                current_proposal_arc = proposal.get("arc_beat")
                break

    name = character.display_name
    for boundary in boundaries:
        if not isinstance(boundary, str):
            continue
        patterns = BOUNDARY_KEYWORD_MAP.get(
            boundary.lower(),
            [re.escape(boundary.split()[0]) + r".*" + re.escape(" ".join(boundary.split()[1:]))]
            if " " in boundary
            else [re.escape(boundary)],
        )
        matched = False
        matched_span = ""
        for pat in patterns:
            regex = re.compile(pat, re.IGNORECASE)
            if _name_in_prose_window(prose, name, regex):
                matched = True
                idx = prose.find(name)
                matched_span = prose[max(0, idx - 20) : idx + len(name) + 60]
                break
        if not matched:
            continue

        if current_proposal_arc and current_proposal_arc in expected_beats:
            return None

        code = (
            "psych_moral_boundary_crossed"
            if allow_break or expected_beats
            else ("psych_ooc_moral_boundary_violation")
        )
        severity = (
            ContinuitySeverity.WARN.value
            if allow_break or expected_beats
            else ContinuitySeverity.FAIL.value
        )
        return ContinuityIssue(
            fingerprint=psych_fingerprint(
                character.id,
                "ooc_moral",
                _boundary_hash(boundary),
                chapter_id,
            ),
            severity=severity,
            category=ContinuityCategory.psychology.value,
            code=code,
            message=(f'{name} vi phạm ranh giới đạo đức "{boundary}" ở ch.{chapter_number}'),
            chapter_refs=[chapter_number],
            entity_ids=[str(character.id)],
            evidence={"boundary": boundary, "matched_span": matched_span.strip()},
        )
    return None


def check_value_hierarchy_jump(
    *,
    character: Character,
    prose: str,
    chapter_number: int,
    chapter_id: uuid.UUID,
    psych_state_proposals: list[dict[str, Any]] | None = None,
) -> ContinuityIssue | None:
    if not character_applies_psychology_rules(character):
        return None
    psyche = character.psyche_card or {}
    hierarchy = psyche.get("value_hierarchy") or []
    if not isinstance(hierarchy, list) or len(hierarchy) < 2:
        return None

    proposal = next(
        (
            p
            for p in (psych_state_proposals or [])
            if str(p.get("character_id")) == str(character.id)
        ),
        None,
    )
    if proposal:
        belief_updates = proposal.get("belief_updates") or []
        trigger_refs = proposal.get("trigger_event_refs") or []
        if belief_updates and trigger_refs:
            return None

    top_value = str(hierarchy[0]).lower()
    patterns = VALUE_JUMP_KEYWORDS.get(top_value, [])
    name = character.display_name
    for pat in patterns:
        if _name_in_prose_window(prose, name, re.compile(pat, re.IGNORECASE)):
            return ContinuityIssue(
                fingerprint=psych_fingerprint(
                    character.id,
                    "value_jump",
                    f"{top_value}:demoted",
                    chapter_id,
                ),
                severity=ContinuitySeverity.WARN.value,
                category=ContinuityCategory.psychology.value,
                code="psych_value_hierarchy_jump",
                message=(
                    f'{name} có dấu hiệu bỏ giá trị hàng đầu "{hierarchy[0]}" '
                    f"mà chưa có trigger earned change ở ch.{chapter_number}"
                ),
                chapter_refs=[chapter_number],
                entity_ids=[str(character.id)],
                evidence={
                    "from_value": hierarchy[0],
                    "to_value": hierarchy[1] if len(hierarchy) > 1 else "",
                },
            )
    return None


def check_arc_beat_skip(
    *,
    character: Character,
    prose: str,
    chapter_number: int,
    chapter_id: uuid.UUID,
    psych_state_proposals: list[dict[str, Any]] | None = None,
) -> ContinuityIssue | None:
    if not character_applies_psychology_rules(character):
        return None
    psyche = character.psyche_card or {}
    arc_flags = psyche.get("arc_flags") or {}
    expected = arc_flags.get("expected_arc_beats") or []
    if not expected:
        return None

    proposal = next(
        (
            p
            for p in (psych_state_proposals or [])
            if str(p.get("character_id")) == str(character.id)
        ),
        None,
    )
    if proposal and proposal.get("arc_beat") in expected:
        return None

    current_idx = None
    for idx, beat in enumerate(expected):
        if beat.lower() in prose.lower():
            current_idx = idx
            break
    if current_idx is None or current_idx == 0:
        return None

    skipped = expected[current_idx - 1]
    return ContinuityIssue(
        fingerprint=psych_fingerprint(
            character.id,
            "arc_skip",
            skipped,
            chapter_id,
        ),
        severity=ContinuitySeverity.WARN.value,
        category=ContinuityCategory.psychology.value,
        code="psych_arc_beat_skip",
        message=(
            f'{character.display_name} có thể nhảy beat "{expected[current_idx]}" '
            f'trước "{skipped}" ở ch.{chapter_number}'
        ),
        chapter_refs=[chapter_number],
        entity_ids=[str(character.id)],
        evidence={"expected_beat": skipped, "implied_beat": expected[current_idx]},
    )


def check_unearned_belief_shift(
    *,
    character: Character,
    chapter_number: int,
    chapter_id: uuid.UUID,
    prior_psych: PsychState | None,
    psych_state_proposals: list[dict[str, Any]] | None = None,
) -> ContinuityIssue | None:
    if not character_applies_psychology_rules(character):
        return None
    proposal = next(
        (
            p
            for p in (psych_state_proposals or [])
            if str(p.get("character_id")) == str(character.id)
        ),
        None,
    )
    if proposal is None:
        return None
    belief_updates = proposal.get("belief_updates") or []
    if not belief_updates:
        return None
    if any(not (b.get("trigger_ref") or b.get("trigger_event_refs")) for b in belief_updates):
        trigger_refs = proposal.get("trigger_event_refs") or []
        if not trigger_refs:
            prior_stress = prior_psych.stress_level if prior_psych else 0
            new_stress = int(proposal.get("stress_level", prior_stress))
            psyche = character.psyche_card or {}
            drive = psyche.get("drive") or ""
            contradicts = any(
                drive and drive.lower() in str(b.get("from_belief", "")).lower()
                for b in belief_updates
            )
            if contradicts and new_stress - prior_stress < 3:
                return ContinuityIssue(
                    fingerprint=psych_fingerprint(
                        character.id,
                        "unearned_belief",
                        "shift",
                        chapter_id,
                    ),
                    severity=ContinuitySeverity.WARN.value,
                    category=ContinuityCategory.psychology.value,
                    code="psych_unearned_belief_shift",
                    message=(
                        f"{character.display_name} có belief shift chưa có trigger "
                        f"ở ch.{chapter_number}"
                    ),
                    chapter_refs=[chapter_number],
                    entity_ids=[str(character.id)],
                    evidence={"belief_updates": belief_updates},
                )
    return None


def check_voice_taboo_break(
    *,
    character: Character,
    prose: str,
    chapter_number: int,
    chapter_id: uuid.UUID,
) -> ContinuityIssue | None:
    if not character_applies_psychology_rules(character):
        return None
    psyche = character.psyche_card or {}
    taboos = psyche.get("voice_taboo") or []
    if not taboos:
        return None
    name = character.display_name
    for taboo in taboos:
        if not isinstance(taboo, str):
            continue
        dialogue_pattern = re.compile(
            rf'["\u201c][^"\u201d]*{re.escape(taboo)}[^"\u201d]*["\u201d]\s*[—\-–]\s*{re.escape(name)}',
            re.IGNORECASE,
        )
        alt_pattern = re.compile(
            rf'{re.escape(name)}[^"\n]*["\u201c][^"\u201d]*{re.escape(taboo)}',
            re.IGNORECASE,
        )
        if dialogue_pattern.search(prose) or alt_pattern.search(prose):
            return ContinuityIssue(
                fingerprint=psych_fingerprint(
                    character.id,
                    "voice_taboo",
                    _boundary_hash(taboo),
                    chapter_id,
                ),
                severity=ContinuitySeverity.WARN.value,
                category=ContinuityCategory.psychology.value,
                code="psych_voice_taboo_break",
                message=(f'{name} nói taboo "{taboo}" ở ch.{chapter_number}'),
                chapter_refs=[chapter_number],
                entity_ids=[str(character.id)],
                evidence={"taboo": taboo},
            )
    return None


def build_psych_state_proposals(
    *,
    prose: str,
    characters: list[Character],
    beats: list[dict],
    chapter_id: uuid.UUID,
    prior_states: dict[uuid.UUID, PsychState],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract stub psych proposals and optional psyche card patches."""
    proposals: list[dict[str, Any]] = []
    psyche_patches: list[dict[str, Any]] = []

    for character in characters:
        if not character_applies_psychology_rules(character):
            continue
        name = character.display_name
        if name not in prose:
            continue

        prior = prior_states.get(character.id)
        base_stress = prior.stress_level if prior else 3
        stress_level = base_stress
        dominant_emotion = prior.dominant_emotion if prior else "neutral"
        active_goal = prior.active_goal if prior else ""
        belief_updates: list[dict[str, Any]] = []
        relationship_stance: list[dict[str, Any]] = []
        value_pressure = None
        arc_beat = None
        trigger_refs: list[str] = []

        idx = prose.find(name)
        window = prose[max(0, idx - 40) : idx + len(name) + 80].lower()
        if any(kw in window for kw in STRESS_KEYWORDS):
            stress_level = min(10, base_stress + 2)
            dominant_emotion = "anger"
        if any(kw in window for kw in BETRAYAL_KEYWORDS):
            belief_updates.append(
                {
                    "from_belief": "Tin tưởng sư phụ",
                    "to_belief": "Nghi ngờ sư phụ",
                    "confidence": "extract_stub",
                    "trigger_ref": f"beat:{beats[0]['id']}" if beats and beats[0].get("id") else "",
                }
            )
            stress_level = min(10, stress_level + 1)

        for beat in beats:
            summary = beat.get("summary", "")
            if name in summary or name in prose:
                if beat.get("id"):
                    trigger_refs.append(f"beat:{beat['id']}")
                goal_match = re.search(r"goal:\s*(.+)", summary, re.IGNORECASE)
                if goal_match:
                    active_goal = goal_match.group(1).strip()
                arc_match = re.search(r"arc_beat:\s*(\S+)", summary, re.IGNORECASE)
                if arc_match:
                    arc_beat = arc_match.group(1)

        psyche = character.psyche_card or {}
        hierarchy = psyche.get("value_hierarchy") or []
        if hierarchy and stress_level >= 7:
            value_pressure = hierarchy[0] if isinstance(hierarchy[0], str) else None

        if arc_beat:
            psyche_patches.append(
                {
                    "character_id": str(character.id),
                    "patch": {"arc_flags": {"current_arc_beat": arc_beat}},
                    "confidence": "extract_stub",
                }
            )

        proposals.append(
            {
                "character_id": str(character.id),
                "chapter_id": str(chapter_id),
                "stress_level": stress_level,
                "dominant_emotion": dominant_emotion,
                "active_goal": active_goal,
                "belief_updates": belief_updates,
                "relationship_stance": relationship_stance,
                "value_pressure": value_pressure,
                "arc_beat": arc_beat,
                "trigger_event_refs": trigger_refs,
                "confidence": "extract_stub",
            }
        )

    return proposals, psyche_patches


def run_psychology_checks(
    *,
    prose: str,
    chapter_number: int,
    chapter_id: uuid.UUID,
    characters: list[Character],
    prior_states: dict[uuid.UUID, PsychState],
    psych_state_proposals: list[dict[str, Any]] | None = None,
) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []
    for character in characters:
        if character.display_name not in prose:
            continue
        moral = check_ooc_moral_boundary(
            character=character,
            prose=prose,
            chapter_number=chapter_number,
            chapter_id=chapter_id,
            psych_state_proposals=psych_state_proposals,
        )
        if moral:
            issues.append(moral)
        value_jump = check_value_hierarchy_jump(
            character=character,
            prose=prose,
            chapter_number=chapter_number,
            chapter_id=chapter_id,
            psych_state_proposals=psych_state_proposals,
        )
        if value_jump:
            issues.append(value_jump)
        arc_skip = check_arc_beat_skip(
            character=character,
            prose=prose,
            chapter_number=chapter_number,
            chapter_id=chapter_id,
            psych_state_proposals=psych_state_proposals,
        )
        if arc_skip:
            issues.append(arc_skip)
        unearned = check_unearned_belief_shift(
            character=character,
            chapter_number=chapter_number,
            chapter_id=chapter_id,
            prior_psych=prior_states.get(character.id),
            psych_state_proposals=psych_state_proposals,
        )
        if unearned:
            issues.append(unearned)
        taboo = check_voice_taboo_break(
            character=character,
            prose=prose,
            chapter_number=chapter_number,
            chapter_id=chapter_id,
        )
        if taboo:
            issues.append(taboo)
    return issues
