"""Phase 9 series continuity WARN rules."""

from __future__ import annotations

from app.models.bible import BibleEntryStaging
from app.models.enums import ContinuityCategory, ContinuitySeverity
from app.models.project import Project
from app.services.continuity.engine import ContinuityIssue


def run_series_checks(
    *,
    project: Project,
    slice_version: int,
    staging_rows: list[BibleEntryStaging],
    inherited_keys: set[str],
) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []
    last_seen = project.last_seen_series_slice_version or 0
    if slice_version > last_seen and project.series_id:
        issues.append(
            ContinuityIssue(
                fingerprint=f"series:{project.id}:series_parent_slice_updated",
                severity=ContinuitySeverity.WARN.value,
                category=ContinuityCategory.series.value,
                code="series_parent_slice_updated",
                message=f"Parent slice v{slice_version} > last seen v{last_seen}",
                chapter_refs=[],
                entity_ids=[str(project.series_id)],
                evidence={"slice_version": slice_version, "last_seen": last_seen},
            )
        )

    for row in staging_rows:
        metadata = row.metadata_ or {}
        if metadata.get("series_override") and not metadata.get("override_reason"):
            issues.append(
                ContinuityIssue(
                    fingerprint=f"series:{row.id}:series_override_without_reason",
                    severity=ContinuitySeverity.WARN.value,
                    category=ContinuityCategory.series.value,
                    code="series_override_without_reason",
                    message="Override staging missing override_reason",
                    chapter_refs=[],
                    entity_ids=[str(row.id)],
                    evidence={"entry_key": row.entry_key},
                )
            )
        override_key = metadata.get("overrides_series_key") or row.entry_key
        if not metadata.get("series_override") and override_key in inherited_keys:
            issues.append(
                ContinuityIssue(
                    fingerprint=f"series:{row.id}:series_inherited_key_conflict",
                    severity=ContinuitySeverity.WARN.value,
                    category=ContinuityCategory.series.value,
                    code="series_inherited_key_conflict",
                    message="Staging edits inherited key without series_override flag",
                    chapter_refs=[],
                    entity_ids=[str(row.id)],
                    evidence={"entry_key": row.entry_key},
                )
            )
    return issues


def inherited_keys_from_slice(slice_json: dict) -> set[str]:
    keys: set[str] = set()

    def walk(prefix: str, node: object) -> None:
        if not isinstance(node, dict):
            return
        for key, value in node.items():
            full = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict) and ("title" in value or "content_md" in value):
                keys.add(full)
            else:
                walk(full, value)

    for section, content in slice_json.items():
        walk(section, content)
    return keys
