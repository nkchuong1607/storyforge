"""Inline export job processing using caller session (sync test mode)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.enums import ExportChapterScope, ExportJobStatus, ExportJobType
from app.models.export_job import ExportJob
from app.repositories.bible import BibleRepository
from app.repositories.chapter import ChapterRepository
from app.repositories.export import ExportRepository
from app.repositories.project import ProjectRepository
from app.repositories.prose import ProseRepository
from app.services.export.builders import (
    build_docx_bytes,
    build_epub_bytes,
    build_git_md_tree,
    write_zip,
)
from app.services.export.scope import resolve_chapters_for_export


async def process_export_job(session: AsyncSession, job_id: uuid.UUID) -> None:
    """Process export job in the provided session (same DB as API request)."""
    settings = get_settings()
    export_repo = ExportRepository(session)
    project_repo = ProjectRepository(session)
    chapter_repo = ChapterRepository(session)
    prose_repo = ProseRepository(session)
    bible_repo = BibleRepository(session)

    job = await session.get(ExportJob, job_id)
    if job is None:
        return
    if job.status not in (ExportJobStatus.pending.value, ExportJobStatus.running.value):
        return

    job.status = ExportJobStatus.running.value
    job.started_at = datetime.now(UTC)
    await session.flush()

    project = await project_repo.get_by_id(job.project_id)
    if project is None:
        job.status = ExportJobStatus.failed.value
        job.error_message = "Project not found"
        job.finished_at = datetime.now(UTC)
        await export_repo.update(job)
        return

    options = job.options_json or {}
    scope = ExportChapterScope(options.get("chapter_scope", "settled_only"))
    chapter_ids_raw = options.get("chapter_ids") or []
    chapter_ids = [uuid.UUID(str(cid)) for cid in chapter_ids_raw]

    all_chapters = await chapter_repo.list_all_for_project(project.id)
    chapters = resolve_chapters_for_export(
        all_chapters, scope=scope, chapter_ids=chapter_ids or None
    )
    if not chapters and scope != ExportChapterScope.include_drafts:
        job.status = ExportJobStatus.failed.value
        job.error_message = "No settled chapters match scope"
        job.finished_at = datetime.now(UTC)
        await export_repo.update(job)
        return

    prose_by_chapter: dict[str, str] = {}
    for chapter in chapters:
        prose = await prose_repo.get_latest(chapter.id)
        prose_by_chapter[str(chapter.id)] = prose.content if prose else ""

    bible_version = options.get("bible_version") or project.bible_version_current
    bible_row = await bible_repo.get_version(project.id, bible_version)
    bible_snapshot = bible_row.snapshot_json if bible_row else {"entries": []}

    strip_secrets = options.get("strip_secrets", True)
    include_bible = options.get("include_bible", True)
    artifact_dir = Path(settings.export_artifact_dir) / str(project.id) / str(job.id)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    job_type = ExportJobType(job.job_type)
    if job_type == ExportJobType.git_md_mirror:
        files = build_git_md_tree(
            project,
            chapters,
            prose_by_chapter,
            bible_snapshot,
            strip_secrets=strip_secrets,
            include_bible=include_bible,
        )
        filename = f"{project.slug}-mirror.zip"
        dest = artifact_dir / filename
        write_zip(files, dest)
        result = {
            "chapter_count": len(chapters),
            "bible_version": bible_version,
            "tree_root": project.slug,
        }
        if options.get("git_md_push_stub"):
            result["push_stub"] = {
                "remote": "origin",
                "branch": "canon-mirror",
                "status": "skipped_phase9",
            }
    elif job_type == ExportJobType.epub:
        content = build_epub_bytes(project, chapters, prose_by_chapter, strip_secrets=strip_secrets)
        filename = f"{project.slug}.epub"
        dest = artifact_dir / filename
        dest.write_bytes(content)
        result = {"chapter_count": len(chapters), "bible_version": bible_version}
    else:
        content = build_docx_bytes(project, chapters, prose_by_chapter, strip_secrets=strip_secrets)
        filename = f"{project.slug}.docx"
        dest = artifact_dir / filename
        dest.write_bytes(content)
        result = {"chapter_count": len(chapters), "bible_version": bible_version}

    job.status = ExportJobStatus.done.value
    job.artifact_path = str(dest)
    job.artifact_filename = filename
    job.artifact_size_bytes = dest.stat().st_size
    job.result_json = result
    job.finished_at = datetime.now(UTC)
    job.error_message = None
    await export_repo.update(job)
