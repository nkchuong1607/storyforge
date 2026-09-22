"""Phase 11b export golden integration tests."""

from __future__ import annotations

import json
import uuid
import zipfile
from io import BytesIO
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bible import BibleVersion
from tests.factories import blank_project_payload

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "golden" / "export_golden"


async def _seed_golden_export_project(
    client: AsyncClient,
    headers: dict[str, str],
    session: AsyncSession,
) -> tuple[str, str]:
    scenario = json.loads((GOLDEN_DIR / "scenario.json").read_text(encoding="utf-8"))
    create = await client.post(
        "/projects",
        json=blank_project_payload(title=scenario["project_title"]),
        headers=headers,
    )
    assert create.status_code == 201
    project_id = create.json()["id"]
    project_slug = create.json()["slug"]

    settled_ch = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 1, "title": "Opening Chapter"},
        headers=headers,
    )
    assert settled_ch.status_code == 201
    settled_id = settled_ch.json()["id"]

    draft_ch = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 2, "title": "Draft Chapter"},
        headers=headers,
    )
    assert draft_ch.status_code == 201
    draft_id = draft_ch.json()["id"]

    await client.post(
        f"/projects/{project_id}/chapters/{settled_id}/prose-versions",
        json={"content": scenario["prose_settled"]},
        headers=headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{draft_id}/prose-versions",
        json={"content": scenario["prose_draft"]},
        headers=headers,
    )

    await client.post(
        f"/projects/{project_id}/chapters/{settled_id}/continuity-check",
        headers=headers,
    )
    settle = await client.post(
        f"/projects/{project_id}/chapters/{settled_id}/settle",
        headers={**headers, "Idempotency-Key": str(uuid.uuid4())},
    )
    assert settle.status_code == 200

    version = await session.scalar(
        select(BibleVersion).where(
            BibleVersion.project_id == uuid.UUID(project_id),
            BibleVersion.version == 1,
        )
    )
    assert version is not None
    snapshot = dict(version.snapshot_json)
    entries = list(snapshot.get("entries", []))
    entries.extend([scenario["bible_world_entry"], scenario["bible_character_entry"]])
    snapshot["entries"] = entries
    version.snapshot_json = snapshot
    await session.commit()

    return project_id, project_slug


@pytest.mark.integration
async def test_export_golden_docx_and_git_md_defaults(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    expected_paths = json.loads((GOLDEN_DIR / "expected_paths.json").read_text(encoding="utf-8"))
    expected_manifest = json.loads(
        (GOLDEN_DIR / "expected_manifest.json").read_text(encoding="utf-8")
    )
    project_id, project_slug = await _seed_golden_export_project(client, user_a_headers, session)

    for job_type in ("docx", "git_md_mirror"):
        enqueue = await client.post(
            f"/projects/{project_id}/export/jobs",
            json={"job_type": job_type, "options": {}},
            headers=user_a_headers,
        )
        assert enqueue.status_code == 202
        job = enqueue.json()
        assert job["options"]["chapter_scope"] == "settled_only"
        assert job["options"]["strip_secrets"] is True
        assert job["status"] == "done"

        download = await client.get(
            f"/projects/{project_id}/export/jobs/{job['id']}/download",
            headers=user_a_headers,
        )
        assert download.status_code == 200
        content = download.content
        assert len(content) > 0
        assert b"secret_truth" not in content.lower()

        if job_type == "docx":
            with zipfile.ZipFile(BytesIO(content)) as zf:
                names = set(zf.namelist())
                for part in expected_paths["docx_parts"]:
                    assert part in names
                doc_xml = zf.read("word/document.xml").decode("utf-8")
                assert "Opening Chapter" in doc_xml
                assert "Draft Chapter" not in doc_xml
                assert "&amp;" in doc_xml or "&" not in doc_xml.split("<w:t")[1][:20]
        else:
            with zipfile.ZipFile(BytesIO(content)) as zf:
                names = set(zf.namelist())
                for suffix in expected_paths["required_suffixes"]:
                    assert any(n.endswith(suffix) for n in names), suffix
                prefix = f"{project_slug}/"
                chapter_path = next(n for n in names if n.endswith("01-opening-chapter.md"))
                chapter_body = zf.read(chapter_path).decode("utf-8")
                assert chapter_body.startswith("---\n")
                assert "number: 1" in chapter_body
                assert "secret_truth" not in chapter_body.lower()
                manifest = json.loads(zf.read(f"{prefix}manifest.json"))
                for key in expected_manifest["required_keys"]:
                    assert key in manifest
                assert manifest["chapter_count"] >= expected_manifest["min_chapter_count"]
                assert len(manifest["chapters"]) == 1


@pytest.mark.integration
async def test_export_epub_regression(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    project_id, _ = await _seed_golden_export_project(client, user_a_headers, session)
    enqueue = await client.post(
        f"/projects/{project_id}/export/jobs",
        json={"job_type": "epub", "options": {}},
        headers=user_a_headers,
    )
    assert enqueue.status_code == 202
    job = enqueue.json()
    assert job["status"] == "done"
    download = await client.get(
        f"/projects/{project_id}/export/jobs/{job['id']}/download",
        headers=user_a_headers,
    )
    assert download.status_code == 200
    assert download.content[:2] == b"PK"
    assert b"secret_truth" not in download.content.lower()


@pytest.mark.integration
async def test_export_settled_only_excludes_draft(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    project_id, project_slug = await _seed_golden_export_project(client, user_a_headers, session)
    enqueue = await client.post(
        f"/projects/{project_id}/export/jobs",
        json={"job_type": "git_md_mirror", "options": {"chapter_scope": "settled_only"}},
        headers=user_a_headers,
    )
    assert enqueue.status_code == 202
    job = enqueue.json()
    assert job["status"] == "done"
    assert job["result_json"]["chapter_count"] == 1

    download = await client.get(
        f"/projects/{project_id}/export/jobs/{job['id']}/download",
        headers=user_a_headers,
    )
    with zipfile.ZipFile(BytesIO(download.content)) as zf:
        chapter_files = [n for n in zf.namelist() if "/chapters/" in n]
        assert len(chapter_files) == 1
        assert "draft-chapter" not in chapter_files[0].lower()
        manifest = json.loads(zf.read(f"{project_slug}/manifest.json"))
        assert manifest["chapter_count"] == 1
