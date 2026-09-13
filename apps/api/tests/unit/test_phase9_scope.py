"""Export scope resolver unit tests."""

import uuid

import pytest

from app.models.chapter import Chapter
from app.models.enums import ChapterStatus, ExportChapterScope
from app.services.export.scope import is_draft_chapter, resolve_chapters_for_export


def _chapter(number: int, status: ChapterStatus) -> Chapter:
    return Chapter(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        number=number,
        title=f"Ch {number}",
        status=status,
    )


@pytest.mark.unit
def test_settled_only_filters_drafts() -> None:
    chapters = [
        _chapter(1, ChapterStatus.settled),
        _chapter(2, ChapterStatus.drafting),
    ]
    result = resolve_chapters_for_export(
        chapters, scope=ExportChapterScope.settled_only, chapter_ids=None
    )
    assert len(result) == 1
    assert result[0].number == 1


@pytest.mark.unit
def test_include_drafts() -> None:
    chapters = [_chapter(1, ChapterStatus.drafting)]
    result = resolve_chapters_for_export(
        chapters, scope=ExportChapterScope.include_drafts, chapter_ids=None
    )
    assert len(result) == 1
    assert is_draft_chapter(chapters[0])
