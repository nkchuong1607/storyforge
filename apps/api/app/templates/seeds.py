"""Project template seed data builders."""

from dataclasses import dataclass
from typing import Any

from app.models.enums import BibleSection, ChapterStatus, ProjectTemplate


@dataclass(frozen=True)
class TemplateBibleEntry:
    entry_key: str
    section: BibleSection
    title: str
    content_md: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class TemplateChapter:
    number: int
    title: str
    status: ChapterStatus = ChapterStatus.planned


@dataclass(frozen=True)
class TemplateCharacter:
    display_name: str
    role_one_liner: str | None = None


@dataclass(frozen=True)
class TemplateSeed:
    bible_entries: list[TemplateBibleEntry]
    chapters: list[TemplateChapter]
    characters: list[TemplateCharacter]

    def build_snapshot_json(self, template: ProjectTemplate) -> dict[str, Any]:
        return {
            "version": 0,
            "entries": [
                {
                    "entry_key": entry.entry_key,
                    "section": entry.section.value,
                    "title": entry.title,
                    "content_md": entry.content_md,
                    "metadata": entry.metadata,
                }
                for entry in self.bible_entries
            ],
            "generated_from_template": template.value,
        }


_XIANXIA_ENTRIES = [
    TemplateBibleEntry(
        entry_key="world_rules.cultivation.realms",
        section=BibleSection.world_rules,
        title="Cảnh giới tu luyện",
        content_md="## Luyện Khí\n\nCảnh giới đầu tiên trên con đường tu tiên.",
        metadata={"type": "canon", "status": "active"},
    ),
    TemplateBibleEntry(
        entry_key="world_rules.cultivation.techniques",
        section=BibleSection.world_rules,
        title="Phương pháp tu luyện",
        content_md="## Tâm pháp\n\nQuy tắc tu luyện cơ bản của thế giới.",
        metadata={"type": "canon", "status": "active"},
    ),
    TemplateBibleEntry(
        entry_key="locations.main_sect",
        section=BibleSection.locations,
        title="Tông môn chính",
        content_md="## Thiên Kiếm Phái\n\nTông môn trung tâm của câu chuyện.",
        metadata={"type": "canon", "status": "active"},
    ),
    TemplateBibleEntry(
        entry_key="factions.rival_clans",
        section=BibleSection.factions,
        title="Các thế lực đối địch",
        content_md="## Ma đạo\n\nPhe phản diện chính.",
        metadata={"type": "canon", "status": "active"},
    ),
    TemplateBibleEntry(
        entry_key="glossary.cultivation_terms",
        section=BibleSection.glossary,
        title="Thuật ngữ tu tiên",
        content_md="## Linh khí\n\nNăng lượng cơ bản của thế giới.",
        metadata={"type": "canon", "status": "active"},
    ),
]

_MYSTERY_ENTRIES = [
    TemplateBibleEntry(
        entry_key="world_rules.investigation.protocol",
        section=BibleSection.world_rules,
        title="Quy trình điều tra",
        content_md="## Hiện trường\n\nQuy tắc thu thập manh mối.",
        metadata={"type": "canon", "status": "active"},
    ),
    TemplateBibleEntry(
        entry_key="locations.crime_scene",
        section=BibleSection.locations,
        title="Hiện trường vụ án",
        content_md="## Phòng khách sạn 402\n\nĐịa điểm mở đầu.",
        metadata={"type": "canon", "status": "active"},
    ),
    TemplateBibleEntry(
        entry_key="timeline.case_events",
        section=BibleSection.timeline,
        title="Dòng thời gian vụ án",
        content_md="## Ngày 1\n\nThi thể được phát hiện.",
        metadata={"type": "canon", "status": "active"},
    ),
    TemplateBibleEntry(
        entry_key="characters.detective_profile",
        section=BibleSection.characters,
        title="Hồ sơ thám tử",
        content_md="## Thám tử chính\n\nKinh nghiệm và phương pháp làm việc.",
        metadata={"type": "canon", "status": "active"},
    ),
]

_XIANXIA_CHARACTERS = [
    TemplateCharacter(display_name="Lý Phong", role_one_liner="Nhân vật chính — kiếm tu"),
    TemplateCharacter(display_name="Diệp Vân", role_one_liner="Sư muội — đồng môn"),
]

_MYSTERY_CHARACTERS = [
    TemplateCharacter(display_name="Trần Hạo", role_one_liner="Thám tử chính"),
    TemplateCharacter(display_name="Linh An", role_one_liner="Trợ lý điều tra"),
]

_XIANXIA_CHAPTERS = [
    TemplateChapter(number=1, title="Chương 1 — Khởi đầu"),
]

_MYSTERY_CHAPTERS = [
    TemplateChapter(number=1, title="Chương 1 — Hiện trường"),
]


def get_template_seed(template: ProjectTemplate) -> TemplateSeed:
    """Return seed data for a project template."""
    if template == ProjectTemplate.xianxia_starter:
        return TemplateSeed(
            bible_entries=_XIANXIA_ENTRIES,
            chapters=_XIANXIA_CHAPTERS,
            characters=_XIANXIA_CHARACTERS,
        )
    if template == ProjectTemplate.mystery_starter:
        return TemplateSeed(
            bible_entries=_MYSTERY_ENTRIES,
            chapters=_MYSTERY_CHAPTERS,
            characters=_MYSTERY_CHARACTERS,
        )
    return TemplateSeed(bible_entries=[], chapters=[], characters=[])
