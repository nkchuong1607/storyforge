"""Export processor unit tests."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.chapter import Chapter
from app.models.enums import ChapterStatus
from app.models.export_job import ExportJob
from app.models.project import Project
from app.services.export_processor import process_export_job


@pytest.mark.unit
async def test_process_export_job_no_chapters_fails() -> None:
    session = AsyncMock()
    job_id = uuid.uuid4()
    project_id = uuid.uuid4()
    job = ExportJob(
        project_id=project_id,
        requested_by_user_id=uuid.uuid4(),
        job_type="epub",
        status="pending",
        options_json={"chapter_scope": "settled_only"},
    )
    job.id = job_id
    project = Project(slug="novel", title="Novel", created_by=uuid.uuid4())
    project.id = project_id

    session.get = AsyncMock(return_value=job)
    with (
        patch("app.services.export_processor.ExportRepository") as export_repo_cls,
        patch("app.services.export_processor.ProjectRepository") as project_repo_cls,
        patch("app.services.export_processor.ChapterRepository") as chapter_repo_cls,
    ):
        export_repo_cls.return_value.update = AsyncMock()
        project_repo_cls.return_value.get_by_id = AsyncMock(return_value=project)
        chapter_repo_cls.return_value.list_all_for_project = AsyncMock(return_value=[])

        await process_export_job(session, job_id)
        assert job.status == "failed"
        assert job.error_message


@pytest.mark.unit
async def test_process_export_job_epub_success() -> None:
    session = AsyncMock()
    job_id = uuid.uuid4()
    project_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    job = ExportJob(
        project_id=project_id,
        requested_by_user_id=uuid.uuid4(),
        job_type="epub",
        status="pending",
        options_json={"chapter_scope": "include_drafts", "strip_secrets": True},
    )
    job.id = job_id
    project = Project(slug="novel", title="Novel", created_by=uuid.uuid4())
    project.id = project_id
    project.bible_version_current = 1
    chapter = Chapter(
        project_id=project_id,
        number=1,
        title="Opening",
        status=ChapterStatus.drafting,
    )
    chapter.id = chapter_id
    prose = MagicMock(content="Chapter prose")

    session.get = AsyncMock(return_value=job)
    with (
        patch("app.services.export_processor.ExportRepository") as export_repo_cls,
        patch("app.services.export_processor.ProjectRepository") as project_repo_cls,
        patch("app.services.export_processor.ChapterRepository") as chapter_repo_cls,
        patch("app.services.export_processor.ProseRepository") as prose_repo_cls,
        patch("app.services.export_processor.BibleRepository") as bible_repo_cls,
        patch("app.services.export_processor.get_settings") as settings_mock,
    ):
        export_repo_cls.return_value.update = AsyncMock()
        project_repo_cls.return_value.get_by_id = AsyncMock(return_value=project)
        chapter_repo_cls.return_value.list_all_for_project = AsyncMock(return_value=[chapter])
        prose_repo_cls.return_value.get_latest = AsyncMock(return_value=prose)
        bible_repo_cls.return_value.get_version = AsyncMock(return_value=None)
        settings_mock.return_value.export_artifact_dir = "/tmp/storyforge-test-export"

        await process_export_job(session, job_id)
        assert job.status == "done"
        assert job.artifact_filename == "novel.epub"


@pytest.mark.unit
async def test_process_export_job_git_md_mirror() -> None:
    session = AsyncMock()
    job_id = uuid.uuid4()
    project_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    job = ExportJob(
        project_id=project_id,
        requested_by_user_id=uuid.uuid4(),
        job_type="git_md_mirror",
        status="pending",
        options_json={
            "chapter_scope": "include_drafts",
            "git_md_push_stub": True,
            "include_bible": True,
        },
    )
    job.id = job_id
    project = Project(slug="novel", title="Novel", created_by=uuid.uuid4())
    project.id = project_id
    project.bible_version_current = 2
    chapter = Chapter(
        project_id=project_id,
        number=1,
        title="Opening",
        status=ChapterStatus.drafting,
    )
    chapter.id = chapter_id

    session.get = AsyncMock(return_value=job)
    with (
        patch("app.services.export_processor.ExportRepository") as export_repo_cls,
        patch("app.services.export_processor.ProjectRepository") as project_repo_cls,
        patch("app.services.export_processor.ChapterRepository") as chapter_repo_cls,
        patch("app.services.export_processor.ProseRepository") as prose_repo_cls,
        patch("app.services.export_processor.BibleRepository") as bible_repo_cls,
        patch("app.services.export_processor.get_settings") as settings_mock,
    ):
        export_repo_cls.return_value.update = AsyncMock()
        project_repo_cls.return_value.get_by_id = AsyncMock(return_value=project)
        chapter_repo_cls.return_value.list_all_for_project = AsyncMock(return_value=[chapter])
        prose_repo_cls.return_value.get_latest = AsyncMock(return_value=MagicMock(content="text"))
        bible_repo_cls.return_value.get_version = AsyncMock(
            return_value=MagicMock(snapshot_json={"entries": []})
        )
        settings_mock.return_value.export_artifact_dir = "/tmp/storyforge-test-export"

        await process_export_job(session, job_id)
        assert job.status == "done"
        assert job.result_json["push_stub"]["status"] == "skipped_phase9"


@pytest.mark.unit
async def test_process_export_job_docx_success() -> None:
    session = AsyncMock()
    job_id = uuid.uuid4()
    project_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    job = ExportJob(
        project_id=project_id,
        requested_by_user_id=uuid.uuid4(),
        job_type="docx",
        status="pending",
        options_json={"chapter_scope": "include_drafts"},
    )
    job.id = job_id
    project = Project(slug="novel", title="Novel", created_by=uuid.uuid4())
    project.id = project_id
    project.bible_version_current = 1
    chapter = Chapter(
        project_id=project_id,
        number=1,
        title="Opening",
        status=ChapterStatus.drafting,
    )
    chapter.id = chapter_id
    session.get = AsyncMock(return_value=job)
    with (
        patch("app.services.export_processor.ExportRepository") as export_repo_cls,
        patch("app.services.export_processor.ProjectRepository") as project_repo_cls,
        patch("app.services.export_processor.ChapterRepository") as chapter_repo_cls,
        patch("app.services.export_processor.ProseRepository") as prose_repo_cls,
        patch("app.services.export_processor.BibleRepository") as bible_repo_cls,
        patch("app.services.export_processor.get_settings") as settings_mock,
    ):
        export_repo_cls.return_value.update = AsyncMock()
        project_repo_cls.return_value.get_by_id = AsyncMock(return_value=project)
        chapter_repo_cls.return_value.list_all_for_project = AsyncMock(return_value=[chapter])
        prose_repo_cls.return_value.get_latest = AsyncMock(return_value=MagicMock(content="text"))
        bible_repo_cls.return_value.get_version = AsyncMock(return_value=None)
        settings_mock.return_value.export_artifact_dir = "/tmp/storyforge-test-export"

        await process_export_job(session, job_id)
        assert job.status == "done"
        assert job.artifact_filename == "novel.docx"
