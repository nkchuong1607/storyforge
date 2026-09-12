"""Deterministic continuity rule engine (deterministic-v1)."""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass
from typing import Any

from app.models.bible import BibleEntryStaging
from app.models.character import Character
from app.models.enums import ContinuityCategory, ContinuityResult, ContinuitySeverity

RULE_PACK_VERSION = "deterministic-v1+foreshadow-v1"

DEATH_KEYWORDS = ("chết", "tử vong", "băng hà", "mất mạng")
TRANSITION_KEYWORDS = ("đến", "tới", "rời", "đi tới", "quay về")

ACTIVE_INDICATORS = ("nói", "hỏi", "đáp", "cười", "gật", "bước", "nhìn", "thốt")


@dataclass
class ContinuityIssue:
    fingerprint: str
    severity: str
    category: str
    code: str
    message: str
    chapter_refs: list[int]
    entity_ids: list[str]
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "fingerprint": self.fingerprint,
            "severity": self.severity,
            "category": self.category,
            "code": self.code,
            "message": self.message,
            "chapter_refs": self.chapter_refs,
            "entity_ids": self.entity_ids,
            "evidence": self.evidence,
        }


def _stable_hash(*parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()
    return digest[:12]


def _fingerprint(category: str, entity_id: str, code: str, prose: str) -> str:
    return f"{category}:{entity_id}:{code}:{_stable_hash(prose)}"


def _normalize_content(content: str) -> str:
    return " ".join(content.split())


def _snapshot_entries_map(snapshot_json: dict) -> dict[str, dict]:
    entries = snapshot_json.get("entries", [])
    if not isinstance(entries, list):
        return {}
    return {
        entry["entry_key"]: entry
        for entry in entries
        if isinstance(entry, dict) and "entry_key" in entry
    }


def _character_status_from_ledger(entity_id: uuid.UUID, ledger_tail: list[dict]) -> str | None:
    status = "alive"
    for event in ledger_tail:
        if event.get("entity_id") != str(entity_id):
            continue
        if event.get("event_type") != "status_change":
            continue
        payload = event.get("payload", {})
        if isinstance(payload, dict) and "to" in payload:
            status = str(payload["to"])
    return status


def check_character_deceased_appears_alive(
    *,
    character: Character,
    prose: str,
    chapter_number: int,
    ledger_tail: list[dict],
) -> ContinuityIssue | None:
    status = _character_status_from_ledger(character.id, ledger_tail)
    if status not in ("deceased", "missing"):
        return None
    name = character.display_name
    if name not in prose:
        return None
    idx = prose.find(name)
    context = prose[max(0, idx - 20) : idx + len(name) + 40].lower()
    if any(kw in context for kw in ("hồi tưởng", "mộng", "transformed", "revived")):
        return None
    if not any(ind in context for ind in ACTIVE_INDICATORS):
        return None
    return ContinuityIssue(
        fingerprint=_fingerprint(
            "character", str(character.id), "character_deceased_appears_alive", prose
        ),
        severity=ContinuitySeverity.FAIL.value,
        category=ContinuityCategory.character.value,
        code="character_deceased_appears_alive",
        message=(f"Nhân vật '{name}' đã chết ở chương trước nhưng xuất hiện sống ở đoạn này"),
        chapter_refs=[chapter_number],
        entity_ids=[str(character.id)],
        evidence={"prose_excerpt": context, "ledger_event_id": None},
    )


def check_character_status_regression(
    *,
    entity_id: uuid.UUID,
    display_name: str,
    proposal: dict,
    chapter_number: int,
) -> ContinuityIssue | None:
    payload = proposal.get("payload", {})
    if not isinstance(payload, dict):
        return None
    if payload.get("from") == "deceased" and payload.get("to") == "alive":
        if proposal.get("event_type") == "transformed":
            return None
        return ContinuityIssue(
            fingerprint=_fingerprint(
                "character", str(entity_id), "character_status_regression", str(payload)
            ),
            severity=ContinuitySeverity.WARN.value,
            category=ContinuityCategory.character.value,
            code="character_status_regression",
            message=f"Nhân vật '{display_name}' có đề xuất deceased → alive không hợp lệ",
            chapter_refs=[chapter_number],
            entity_ids=[str(entity_id)],
            evidence={"proposal": payload},
        )
    return None


def check_character_unknown_in_cast(
    *,
    prose: str,
    characters: list[Character],
    chapter_number: int,
) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []
    known_names = {c.display_name for c in characters}
    name_pattern = (
        r"[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨ"
        r"ƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗ"
        r"ơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+"
    )
    words = re.findall(name_pattern, prose)
    for name in set(words):
        if name in known_names:
            continue
        if len(name) < 2:
            continue
        issues.append(
            ContinuityIssue(
                fingerprint=_fingerprint("character", name, "character_unknown_in_cast", prose),
                severity=ContinuitySeverity.WARN.value,
                category=ContinuityCategory.character.value,
                code="character_unknown_in_cast",
                message=f"Tên '{name}' không khớp danh sách nhân vật",
                chapter_refs=[chapter_number],
                entity_ids=[],
                evidence={"name": name},
            )
        )
    return issues


def check_bible_staging_conflicts_settled(
    *,
    staging_rows: list[BibleEntryStaging],
    snapshot_json: dict,
    bible_version_current: int,
    chapter_number: int,
) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []
    settled = _snapshot_entries_map(snapshot_json)
    for row in staging_rows:
        if row.base_bible_version >= bible_version_current:
            continue
        settled_entry = settled.get(row.entry_key)
        if settled_entry is None:
            continue
        settled_content = _normalize_content(settled_entry.get("content_md", ""))
        staging_content = _normalize_content(row.content_md)
        settled_meta = settled_entry.get("metadata", {}) or {}
        staging_meta = row.metadata_ or {}
        content_conflict = settled_content != staging_content
        status_conflict = (
            settled_meta.get("status") != staging_meta.get("status")
            and settled_meta.get("status") is not None
            and staging_meta.get("status") is not None
        )
        if not content_conflict and not status_conflict:
            continue
        issues.append(
            ContinuityIssue(
                fingerprint=_fingerprint(
                    "bible_staging",
                    row.entry_key,
                    "bible_staging_conflicts_settled",
                    row.content_md,
                ),
                severity=ContinuitySeverity.FAIL.value,
                category=ContinuityCategory.bible_staging.value,
                code="bible_staging_conflicts_settled",
                message=f"Staging '{row.entry_key}' mâu thuẫn với bible đã chốt",
                chapter_refs=[chapter_number],
                entity_ids=[],
                evidence={"entry_key": row.entry_key},
            )
        )
    return issues


def check_world_rule_rank_violation_stub(
    *,
    prose: str,
    snapshot_json: dict,
    chapter_number: int,
) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []
    settled = _snapshot_entries_map(snapshot_json)
    glossary = settled.get("glossary.cultivation_terms") or settled.get(
        "world_rules.cultivation.realms"
    )
    if glossary is None:
        return issues
    glossary_text = glossary.get("content_md", "")
    rank_pattern = re.findall(r"##\s*(\S+)", glossary_text)
    if not rank_pattern:
        return issues
    for rank in rank_pattern:
        if rank in prose and rank not in glossary_text:
            issues.append(
                ContinuityIssue(
                    fingerprint=_fingerprint(
                        "world_rule", rank, "world_rule_rank_violation_stub", prose
                    ),
                    severity=ContinuitySeverity.WARN.value,
                    category=ContinuityCategory.world_rule.value,
                    code="world_rule_rank_violation_stub",
                    message=f"Cảnh giới '{rank}' không có trong glossary",
                    chapter_refs=[chapter_number],
                    entity_ids=[],
                    evidence={"rank": rank},
                )
            )
    return issues


def build_state_diff_stub(
    *,
    prose: str,
    characters: list[Character],
    beats: list[dict],
) -> dict[str, list]:
    ledger_proposals: list[dict] = []
    bible_patch_candidates: list[dict] = []

    for character in characters:
        name = character.display_name
        if name not in prose:
            continue
        idx = prose.find(name)
        window = prose[max(0, idx - 30) : idx + len(name) + 30].lower()
        if any(kw in window for kw in DEATH_KEYWORDS):
            ledger_proposals.append(
                {
                    "entity_type": "character",
                    "entity_id": str(character.id),
                    "event_type": "status_change",
                    "payload": {"from": "alive", "to": "deceased"},
                    "confidence": "stub",
                }
            )
        for beat in beats:
            summary = beat.get("summary", "")
            if "location:" not in summary.lower():
                continue
            if name in summary or name in prose:
                loc_match = re.search(r"location:\s*(\S+)", summary, re.IGNORECASE)
                if loc_match:
                    ledger_proposals.append(
                        {
                            "entity_type": "character",
                            "entity_id": str(character.id),
                            "event_type": "location_change",
                            "payload": {"from": None, "to": loc_match.group(1)},
                            "confidence": "stub",
                        }
                    )

    return {
        "ledger_proposals": ledger_proposals,
        "bible_patch_candidates": bible_patch_candidates,
    }


def check_location_teleport_without_transition(
    *,
    prose: str,
    beats: list[dict],
    chapter_number: int,
) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []
    locations: list[str | None] = []
    for beat in beats:
        summary = beat.get("summary", "")
        match = re.search(r"location:\s*(\S+)", summary, re.IGNORECASE)
        locations.append(match.group(1) if match else None)
    for i in range(1, len(locations)):
        prev_loc, curr_loc = locations[i - 1], locations[i]
        if prev_loc and curr_loc and prev_loc != curr_loc:
            beat_text = beats[i].get("summary", "")
            if not any(kw in beat_text.lower() for kw in TRANSITION_KEYWORDS):
                issues.append(
                    ContinuityIssue(
                        fingerprint=_fingerprint(
                            "location",
                            f"beat-{i}",
                            "location_teleport_without_transition",
                            beat_text,
                        ),
                        severity=ContinuitySeverity.WARN.value,
                        category=ContinuityCategory.location.value,
                        code="location_teleport_without_transition",
                        message="Thay đổi địa điểm giữa các beat không có chuyển cảnh",
                        chapter_refs=[chapter_number],
                        entity_ids=[],
                        evidence={"from": prev_loc, "to": curr_loc},
                    )
                )
    return issues


def run_continuity_checks(
    *,
    prose: str,
    chapter_number: int,
    chapter_id: uuid.UUID | None = None,
    characters: list[Character],
    ledger_tail: list[dict],
    staging_rows: list[BibleEntryStaging],
    snapshot_json: dict,
    bible_version_current: int,
    beats: list[dict],
    active_override_fingerprints: set[str],
    foreshadow_issues: list[ContinuityIssue] | None = None,
) -> tuple[list[dict], dict, dict, ContinuityResult]:
    """Run all Phase 2 + Phase 4 rules; return issues, state_diff, stats, aggregate result."""
    raw_issues: list[ContinuityIssue] = []

    for character in characters:
        issue = check_character_deceased_appears_alive(
            character=character,
            prose=prose,
            chapter_number=chapter_number,
            ledger_tail=ledger_tail,
        )
        if issue:
            raw_issues.append(issue)

    raw_issues.extend(
        check_character_unknown_in_cast(
            prose=prose, characters=characters, chapter_number=chapter_number
        )
    )
    raw_issues.extend(
        check_bible_staging_conflicts_settled(
            staging_rows=staging_rows,
            snapshot_json=snapshot_json,
            bible_version_current=bible_version_current,
            chapter_number=chapter_number,
        )
    )
    raw_issues.extend(
        check_world_rule_rank_violation_stub(
            prose=prose, snapshot_json=snapshot_json, chapter_number=chapter_number
        )
    )
    raw_issues.extend(
        check_location_teleport_without_transition(
            prose=prose, beats=beats, chapter_number=chapter_number
        )
    )
    if foreshadow_issues:
        raw_issues.extend(foreshadow_issues)

    state_diff = build_state_diff_stub(prose=prose, characters=characters, beats=beats)
    for proposal in state_diff.get("ledger_proposals", []):
        if proposal.get("event_type") == "status_change":
            entity_id = uuid.UUID(proposal["entity_id"])
            char = next((c for c in characters if c.id == entity_id), None)
            if char:
                issue = check_character_status_regression(
                    entity_id=entity_id,
                    display_name=char.display_name,
                    proposal=proposal,
                    chapter_number=chapter_number,
                )
                if issue:
                    raw_issues.append(issue)

    filtered = [
        issue for issue in raw_issues if issue.fingerprint not in active_override_fingerprints
    ]
    issues = [issue.to_dict() for issue in filtered]

    fail_count = sum(1 for i in issues if i["severity"] == ContinuitySeverity.FAIL.value)
    warn_count = sum(1 for i in issues if i["severity"] == ContinuitySeverity.WARN.value)
    passed = max(0, len(characters) - fail_count - warn_count)

    stats = {"passed": passed, "warnings": warn_count, "errors": fail_count}

    if fail_count > 0:
        result = ContinuityResult.FAIL
    elif warn_count > 0:
        result = ContinuityResult.WARN
    else:
        result = ContinuityResult.PASS

    return issues, state_diff, stats, result
