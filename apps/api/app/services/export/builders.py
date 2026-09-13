"""Export artifact builders for EPUB, DOCX, and git-md mirror."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any

from app.models.chapter import Chapter
from app.models.project import Project
from app.services.export.scope import is_draft_chapter
from app.services.export.secret_strip import strip_secrets_from_snapshot, strip_secrets_from_text


def _chapter_filename(chapter: Chapter) -> str:
    slug = chapter.title.lower().replace(" ", "-")[:40] if chapter.title else "chapter"
    return f"{chapter.number:02d}-{slug}.md"


def build_git_md_tree(
    project: Project,
    chapters: list[Chapter],
    prose_by_chapter: dict[str, str],
    bible_snapshot: dict[str, Any],
    *,
    strip_secrets: bool,
    include_bible: bool,
) -> dict[str, bytes]:
    """Return path -> content bytes for git-md mirror zip."""
    snapshot = strip_secrets_from_snapshot(bible_snapshot) if strip_secrets else bible_snapshot
    root = project.slug
    files: dict[str, bytes] = {}

    meta_lines = [
        f"# {project.title}",
        "",
        f"Bible version: {project.bible_version_current}",
        "",
    ]
    files[f"{root}/README.md"] = "\n".join(meta_lines).encode("utf-8")

    if include_bible:
        world_md = "## World\n\n"
        for entry in snapshot.get("entries", []):
            if isinstance(entry, dict) and str(entry.get("entry_key", "")).startswith("world"):
                content = entry.get("content_md", "")
                if strip_secrets:
                    content = strip_secrets_from_text(content)
                world_md += f"### {entry.get('title', '')}\n\n{content}\n\n"
        files[f"{root}/bible/world.md"] = world_md.encode("utf-8")
        files[f"{root}/bible/glossary.md"] = b"# Glossary\n"

    for chapter in chapters:
        prose = prose_by_chapter.get(str(chapter.id), "")
        if strip_secrets:
            prose = strip_secrets_from_text(prose)
        frontmatter = {
            "number": chapter.number,
            "title": chapter.title,
            "status": chapter.status.value,
            "draft": is_draft_chapter(chapter),
        }
        body = (
            "---\n"
            + json.dumps(frontmatter, ensure_ascii=False)
            + "\n---\n\n"
            + f"# {chapter.title}\n\n"
            + prose
        )
        files[f"{root}/chapters/{_chapter_filename(chapter)}"] = body.encode("utf-8")

    manifest = {
        "project_slug": project.slug,
        "bible_version": project.bible_version_current,
        "chapter_count": len(chapters),
        "chapters": [{"id": str(c.id), "number": c.number, "title": c.title} for c in chapters],
    }
    files[f"{root}/manifest.json"] = json.dumps(manifest, indent=2).encode("utf-8")
    return files


def write_zip(files: dict[str, bytes], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in files.items():
            zf.writestr(path, content)


def build_epub_bytes(
    project: Project,
    chapters: list[Chapter],
    prose_by_chapter: dict[str, str],
    *,
    strip_secrets: bool,
) -> bytes:
    """Minimal EPUB3 zip (mimetype + container + content)."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr(
            "META-INF/container.xml",
            '<?xml version="1.0"?><container version="1.0" '
            'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="OEBPS/content.opf" '
            'media-type="application/oebps-package+xml"/></rootfiles></container>',
        )
        items = []
        spine = []
        for idx, chapter in enumerate(chapters, start=1):
            prose = prose_by_chapter.get(str(chapter.id), "")
            if strip_secrets:
                prose = strip_secrets_from_text(prose)
            name = f"chapter{idx:03d}.xhtml"
            draft_attr = ' epub:type="draft"' if is_draft_chapter(chapter) else ""
            xhtml = (
                f'<?xml version="1.0"?><html xmlns="http://www.w3.org/1999/xhtml">'
                f"<head><title>{chapter.title}</title></head>"
                f"<body{draft_attr}><h1>{chapter.title}</h1><p>{prose}</p></body></html>"
            )
            zf.writestr(f"OEBPS/{name}", xhtml)
            items.append(f'<item id="c{idx}" href="{name}" media-type="application/xhtml+xml"/>')
            spine.append(f'<itemref idref="c{idx}"/>')
        opf = (
            '<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0">'
            f"<metadata><dc:title xmlns:dc='http://purl.org/dc/elements/1.1/'>{project.title}"
            "</dc:title></metadata>"
            f"<manifest>{''.join(items)}</manifest>"
            f"<spine>{''.join(spine)}</spine></package>"
        )
        zf.writestr("OEBPS/content.opf", opf)
    return buffer.getvalue()


def build_docx_bytes(
    project: Project,
    chapters: list[Chapter],
    prose_by_chapter: dict[str, str],
    *,
    strip_secrets: bool,
) -> bytes:
    """Minimal DOCX (Office Open XML zip with word/document.xml)."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>",
        )
        zf.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/'
            'relationships/officeDocument" '
            'Target="word/document.xml"/></Relationships>',
        )
        parts = [f"<w:p><w:r><w:t>{project.title}</w:t></w:r></w:p>"]
        for chapter in chapters:
            prose = prose_by_chapter.get(str(chapter.id), "")
            if strip_secrets:
                prose = strip_secrets_from_text(prose)
            draft = " [DRAFT]" if is_draft_chapter(chapter) else ""
            parts.append(
                f"<w:p><w:r><w:t>{chapter.number}. {chapter.title}{draft}</w:t></w:r></w:p>"
            )
            parts.append(f"<w:p><w:r><w:t>{prose}</w:t></w:r></w:p>")
        document = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body>{''.join(parts)}</w:body></w:document>"
        )
        zf.writestr("word/document.xml", document)
    return buffer.getvalue()
