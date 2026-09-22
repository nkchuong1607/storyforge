"""Phase 11b export golden unit tests (no DB)."""

from __future__ import annotations

import json
import uuid
import zipfile
from io import BytesIO
from pathlib import Path

import pytest

from app.models.chapter import Chapter
from app.models.enums import ChapterStatus
from app.models.project import Project
from app.services.export.builders import build_docx_bytes, build_git_md_tree

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "golden" / "export_golden"


@pytest.mark.unit
def test_golden_docx_and_git_md_artifacts() -> None:
    scenario = json.loads((GOLDEN_DIR / "scenario.json").read_text(encoding="utf-8"))
    expected_paths = json.loads((GOLDEN_DIR / "expected_paths.json").read_text(encoding="utf-8"))
    expected_manifest = json.loads(
        (GOLDEN_DIR / "expected_manifest.json").read_text(encoding="utf-8")
    )

    project = Project(
        id=uuid.uuid4(),
        slug="golden-export-novel",
        title=scenario["project_title"],
        created_by=uuid.uuid4(),
        bible_version_current=1,
    )
    chapter = Chapter(
        id=uuid.uuid4(),
        project_id=project.id,
        number=1,
        title="Opening Chapter",
        status=ChapterStatus.locked,
    )
    snapshot = {"entries": [scenario["bible_world_entry"], scenario["bible_character_entry"]]}

    docx = build_docx_bytes(
        project,
        [chapter],
        {str(chapter.id): scenario["prose_settled"]},
        strip_secrets=True,
    )
    with zipfile.ZipFile(BytesIO(docx)) as zf:
        names = set(zf.namelist())
        for part in expected_paths["docx_parts"]:
            assert part in names
        doc_xml = zf.read("word/document.xml").decode("utf-8")
        assert "Opening Chapter" in doc_xml
        assert "secret_truth" not in doc_xml.lower()

    files = build_git_md_tree(
        project,
        [chapter],
        {str(chapter.id): scenario["prose_settled"]},
        snapshot,
        strip_secrets=True,
        include_bible=True,
    )
    for suffix in expected_paths["required_suffixes"]:
        assert any(path.endswith(suffix) for path in files), suffix
    chapter_path = f"{project.slug}/chapters/01-opening-chapter.md"
    chapter_body = files[chapter_path].decode("utf-8")
    assert chapter_body.startswith("---\n")
    assert "secret_truth" not in chapter_body.lower()
    manifest = json.loads(files[f"{project.slug}/manifest.json"])
    for key in expected_manifest["required_keys"]:
        assert key in manifest
    assert manifest["chapter_count"] >= expected_manifest["min_chapter_count"]
