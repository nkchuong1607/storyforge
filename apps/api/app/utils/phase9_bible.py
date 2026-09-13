"""Phase 9 bible section mapping and entry key helpers."""

import re

from app.models.enums import BibleSection, Phase9BibleSection

PHASE9_TO_BIBLE_SECTION: dict[Phase9BibleSection, BibleSection] = {
    Phase9BibleSection.world: BibleSection.world_rules,
    Phase9BibleSection.characters: BibleSection.characters,
    Phase9BibleSection.timeline: BibleSection.timeline,
    Phase9BibleSection.glossary: BibleSection.glossary,
    Phase9BibleSection.objects: BibleSection.objects,
    Phase9BibleSection.style: BibleSection.glossary,
    Phase9BibleSection.power_system: BibleSection.world_rules,
}

DEFAULT_INHERITED_SECTIONS = ["world", "glossary", "style", "power_system"]

BIBLE_KEY_PATTERN = re.compile(r"^[a-z0-9_]+(?:\.[a-z0-9_]+)*$")


def phase9_section_to_bible_section(section: Phase9BibleSection) -> BibleSection:
    return PHASE9_TO_BIBLE_SECTION[section]


def build_entry_key(section: Phase9BibleSection, title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") or "entry"
    return f"{section.value}.{slug}"


def validate_bible_key(key: str) -> bool:
    return bool(BIBLE_KEY_PATTERN.match(key))


def snapshot_to_slice_json(
    snapshot_json: dict, inherited_sections: list[str] | None = None
) -> dict:
    """Build series slice JSON from a settled bible snapshot."""
    sections = inherited_sections or DEFAULT_INHERITED_SECTIONS
    slice_json: dict = {name: {} for name in sections}
    entries = snapshot_json.get("entries", [])
    if not isinstance(entries, list):
        return slice_json
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = entry.get("entry_key", "")
        for section in sections:
            prefix = f"{section}."
            if key == section or key.startswith(prefix):
                bucket = slice_json.setdefault(section, {})
                parts = key.split(".")
                cursor = bucket
                for part in parts[1:-1]:
                    cursor = cursor.setdefault(part, {})
                cursor[parts[-1]] = {
                    "title": entry.get("title", ""),
                    "content_md": entry.get("content_md", ""),
                }
                break
    return slice_json
