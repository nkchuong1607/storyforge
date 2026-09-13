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
    power_system = "power_system"
    scene_structure = "scene_structure"
    relationship_arc = "relationship_arc"
    stakes = "stakes"
    research = "research"
    series = "series"


class ResearchNoteStatus(StrEnum):
    active = "active"
    archived = "archived"
    promoted = "promoted"


class ResearchNoteLinkType(StrEnum):
    character = "character"
    place = "place"
    fact = "fact"
    chapter = "chapter"


class Phase9BibleSection(StrEnum):
    world = "world"
    characters = "characters"
    timeline = "timeline"
    glossary = "glossary"
    objects = "objects"
    style = "style"
    power_system = "power_system"


class ExportJobType(StrEnum):
    epub = "epub"
    docx = "docx"
    git_md_mirror = "git_md_mirror"


class ExportJobStatus(StrEnum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class ExportChapterScope(StrEnum):
    settled_only = "settled_only"
    include_drafts = "include_drafts"
    selected = "selected"


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
    relationship = "relationship"
    stakes = "stakes"


class LedgerEventType(StrEnum):
    status_change = "status_change"
    location_change = "location_change"
    timeline_anchor = "timeline_anchor"
    bible_promote = "bible_promote"
    cultivation_change = "cultivation_change"
    technique_learned = "technique_learned"
    resource_consumed = "resource_consumed"
    relationship_change = "relationship_change"
    stakes_escalation = "stakes_escalation"


class SceneType(StrEnum):
    scene = "scene"
    sequel = "sequel"
    transition = "transition"
    exposition = "exposition"


class RelationType(StrEnum):
    ally = "ally"
    rival = "rival"
    mentor = "mentor"
    family = "family"
    romantic = "romantic"
    enemy = "enemy"
    custom = "custom"


class StakesEntryStatus(StrEnum):
    planned = "planned"
    planted = "planted"
    resolved = "resolved"
    abandoned = "abandoned"


class SceneStrictness(StrEnum):
    relaxed = "relaxed"
    standard = "standard"
    strict = "strict"


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
