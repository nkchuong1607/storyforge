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
    reviewing = "reviewing"
    settled = "settled"
    locked = "locked"


class ProseSource(StrEnum):
    human = "human"
    ai_writer = "ai_writer"
    ai_editor = "ai_editor"


class ContinuityResult(StrEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class ContinuitySeverity(StrEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class ContinuityCategory(StrEnum):
    character = "character"
    timeline = "timeline"
    location = "location"
    world_rule = "world_rule"
    bible_staging = "bible_staging"
    foreshadow = "foreshadow"
    psychology = "psychology"


class TwistPlanStatus(StrEnum):
    seeded = "seeded"
    planted = "planted"
    armed = "armed"
    paid_off = "paid_off"
    abandoned = "abandoned"


class TwistPlanKind(StrEnum):
    twist = "twist"
    promise = "promise"


class PlantSalience(StrEnum):
    soft = "soft"
    hard = "hard"


class GenreStrictness(StrEnum):
    strict = "strict"
    relaxed = "relaxed"


class ContextAudience(StrEnum):
    author = "author"
    writer = "writer"


class LedgerEntityType(StrEnum):
    character = "character"
    object = "object"
    knowledge = "knowledge"
    promise = "promise"


class LedgerEventType(StrEnum):
    status_change = "status_change"
    location_change = "location_change"
    timeline_anchor = "timeline_anchor"
    bible_promote = "bible_promote"


class CharacterStatus(StrEnum):
    established = "established"
    provisional = "provisional"
    archived = "archived"


class ProvisionalStatus(StrEnum):
    pending = "pending"
    merged = "merged"
    rejected = "rejected"


class ExtractorSource(StrEnum):
    heuristic = "heuristic"
    manual = "manual"
    llm = "llm"
