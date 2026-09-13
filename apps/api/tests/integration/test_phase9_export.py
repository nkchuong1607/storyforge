"""Phase 9 export job integration tests."""

import pytest
from httpx import AsyncClient

from tests.factories import project_create_payload


async def _project(client: AsyncClient, headers: dict[str, str]) -> str:
    resp = await client.post("/projects", json=project_create_payload(), headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.integration
async def test_export_epub_lifecycle(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _project(client, user_a_headers)
    enqueue = await client.post(
        f"/projects/{project_id}/export/jobs",
        json={"job_type": "epub", "options": {"chapter_scope": "settled_only"}},
        headers=user_a_headers,
    )
    assert enqueue.status_code == 202
    job_id = enqueue.json()["id"]

    status_resp = await client.get(
        f"/projects/{project_id}/export/jobs/{job_id}",
        headers=user_a_headers,
    )
    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body["status"] in ("done", "failed")

    if body["status"] == "done":
        download = await client.get(
            f"/projects/{project_id}/export/jobs/{job_id}/download",
            headers=user_a_headers,
        )
        assert download.status_code == 200
        assert len(download.content) > 0
    else:
        assert body["error_message"]

    pending_dl = await client.get(
        f"/projects/{project_id}/export/jobs/{job_id}/download",
        headers=user_a_headers,
    )
    if body["status"] != "done":
        assert pending_dl.status_code == 409


@pytest.mark.integration
async def test_export_git_md_mirror(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _project(client, user_a_headers)
    resp = await client.post(
        f"/projects/{project_id}/export/jobs",
        json={
            "job_type": "git_md_mirror",
            "options": {"git_md_push_stub": True, "chapter_scope": "include_drafts"},
        },
        headers=user_a_headers,
    )
    assert resp.status_code == 202
    job = resp.json()
    if job["status"] == "done":
        assert job["result_json"].get("push_stub", {}).get("status") == "skipped_phase9"


@pytest.mark.integration
async def test_export_cancel_pending(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.config import get_settings
    from app.services.export.queue import SyncExportQueue, reset_export_queue

    monkeypatch.setenv("STORYFORGE_EXPORT_SYNC", "0")
    get_settings.cache_clear()
    reset_export_queue()

    monkeypatch.setattr(
        "app.services.export_service.get_export_queue",
        lambda: SyncExportQueue(),
    )

    project_id = await _project(client, user_a_headers)
    enqueue = await client.post(
        f"/projects/{project_id}/export/jobs",
        json={"job_type": "docx"},
        headers=user_a_headers,
    )
    assert enqueue.status_code == 202
    job_id = enqueue.json()["id"]
    assert enqueue.json()["status"] == "pending"
    cancel = await client.delete(
        f"/projects/{project_id}/export/jobs/{job_id}",
        headers=user_a_headers,
    )
    assert cancel.status_code == 204

    get_settings.cache_clear()
    reset_export_queue()
