"""PostgreSQL enum definitions mirrored in Python."""

from enum import StrEnum


class ProjectStatus(StrEnum):
    active = "active"
    archived = "archived"


class ProjectMemberRole(StrEnum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"


class ProjectLanguage(StrEnum):
    vi = "vi"
    en = "en"
    mixed = "mixed"


class GenreProfile(StrEnum):
    xianxia = "xianxia"
    mystery = "mystery"
    literary = "literary"
    romance = "romance"
    custom = "custom"


class ProjectTemplate(StrEnum):
    blank = "blank"
    xianxia_starter = "xianxia_starter"
    mystery_starter = "mystery_starter"


class BibleSection(StrEnum):
    world_rules = "world_rules"
    locations = "locations"
    factions = "factions"
    glossary = "glossary"
    timeline = "timeline"
    characters = "characters"
    objects = "objects"


class ChapterStatus(StrEnum):
    planned = "planned"
    drafting = "drafting"
    continuity_pending = "continuity_pending"
    settled = "settled"
    locked = "locked"
