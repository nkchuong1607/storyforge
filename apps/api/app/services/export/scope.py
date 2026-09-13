"""Export chapter scope resolution."""

import uuid

from app.models.chapter import Chapter
from app.models.enums import ChapterStatus, ExportChapterScope


def resolve_chapters_for_export(
    chapters: list[Chapter],
    *,
    scope: ExportChapterScope,
    chapter_ids: list[uuid.UUID] | None,
) -> list[Chapter]:
    ordered = sorted(chapters, key=lambda c: c.number)
    if scope == ExportChapterScope.selected:
        if not chapter_ids:
            return []
        id_set = set(chapter_ids)
        return [c for c in ordered if c.id in id_set]
    if scope == ExportChapterScope.include_drafts:
        allowed = {
            ChapterStatus.drafting,
            ChapterStatus.reviewing,
            ChapterStatus.settled,
            ChapterStatus.locked,
        }
        return [c for c in ordered if c.status in allowed]
    return [c for c in ordered if c.status in (ChapterStatus.settled, ChapterStatus.locked)]


def is_draft_chapter(chapter: Chapter) -> bool:
    return chapter.status in (ChapterStatus.drafting, ChapterStatus.reviewing)
