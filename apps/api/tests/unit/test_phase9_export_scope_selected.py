"""Export selected scope unit test."""

import uuid

import pytest

from app.models.chapter import Chapter
from app.models.enums import ChapterStatus, ExportChapterScope
from app.services.export.scope import resolve_chapters_for_export


@pytest.mark.unit
def test_selected_scope_filters_chapter_ids() -> None:
    c1 = Chapter(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        number=1,
        title="A",
        status=ChapterStatus.settled,
    )
    c2 = Chapter(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        number=2,
        title="B",
        status=ChapterStatus.settled,
    )
    result = resolve_chapters_for_export(
        [c2, c1], scope=ExportChapterScope.selected, chapter_ids=[c1.id]
    )
    assert len(result) == 1
    assert result[0].id == c1.id
