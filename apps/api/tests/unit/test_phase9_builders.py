"""Export builder unit tests."""

import uuid
import zipfile
from io import BytesIO

import pytest

from app.models.chapter import Chapter
from app.models.enums import ChapterStatus
from app.models.project import Project
from app.services.export.builders import build_epub_bytes, build_git_md_tree


def _project() -> Project:
    return Project(
        id=uuid.uuid4(),
        slug="test-novel",
        title="Test Novel",
        created_by=uuid.uuid4(),
        bible_version_current=1,
    )


def _chapter(number: int) -> Chapter:
    return Chapter(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        number=number,
        title=f"Chapter {number}",
        status=ChapterStatus.settled,
    )


@pytest.mark.unit
def test_build_epub_bytes_non_empty() -> None:
    project = _project()
    chapter = _chapter(1)
    data = build_epub_bytes(project, [chapter], {str(chapter.id): "Prose text"}, strip_secrets=True)
    assert data[:2] == b"PK"


@pytest.mark.unit
def test_git_md_mirror_tree_structure() -> None:
    project = _project()
    chapter = _chapter(1)
    files = build_git_md_tree(
        project,
        [chapter],
        {str(chapter.id): "Body"},
        {"entries": []},
        strip_secrets=True,
        include_bible=True,
    )
    assert f"{project.slug}/chapters/01-chapter-1.md" in files
    assert f"{project.slug}/bible/world.md" in files
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for path, content in files.items():
            zf.writestr(path, content)
    assert buffer.getvalue()
