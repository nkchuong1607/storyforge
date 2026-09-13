"""Phase 9 research continuity WARN rules."""

from __future__ import annotations

from app.models.character import Character
from app.models.enums import CharacterStatus, ContinuityCategory, ContinuitySeverity
from app.models.research import ResearchNoteLink
from app.services.continuity.engine import ContinuityIssue, _snapshot_entries_map


def run_research_checks(
    *,
    links: list[ResearchNoteLink],
    characters: list[Character],
    snapshot_json: dict,
) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []
    char_map = {c.id: c for c in characters}
    entries = _snapshot_entries_map(snapshot_json)

    for link in links:
        if link.link_type == "character" and link.character_id:
            char = char_map.get(link.character_id)
            if char is None or char.status == CharacterStatus.archived:
                issues.append(
                    ContinuityIssue(
                        fingerprint=f"research:{link.id}:research_link_orphan_character",
                        severity=ContinuitySeverity.WARN.value,
                        category=ContinuityCategory.research.value,
                        code="research_link_orphan_character",
                        message="Note links deleted or archived character",
                        chapter_refs=[],
                        entity_ids=[str(link.note_id)],
                        evidence={"character_id": str(link.character_id)},
                    )
                )
        elif link.link_type in ("place", "fact") and link.bible_key:
            if link.bible_key not in entries:
                issues.append(
                    ContinuityIssue(
                        fingerprint=f"research:{link.id}:research_link_orphan_bible_key",
                        severity=ContinuitySeverity.WARN.value,
                        category=ContinuityCategory.research.value,
                        code="research_link_orphan_bible_key",
                        message=f"Linked bible key '{link.bible_key}' missing from snapshot",
                        chapter_refs=[],
                        entity_ids=[str(link.note_id)],
                        evidence={"bible_key": link.bible_key},
                    )
                )
    return issues
