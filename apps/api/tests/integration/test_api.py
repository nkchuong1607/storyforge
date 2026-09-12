"""Phase 1 API integration tests."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bible import BibleVersion
from tests.factories import blank_project_payload, project_create_payload


@pytest.mark.integration
async def test_health_returns_ok_without_auth(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.integration
async def test_missing_user_id_returns_401(client: AsyncClient) -> None:
    response = await client.get("/projects")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


@pytest.mark.integration
async def test_create_project_seeds_bible_and_membership(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    response = await client.post("/projects", json=project_create_payload(), headers=user_a_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["bible_version_current"] == 0
    assert body["chapter_count"] == 1
    assert body["bible_entry_count"] == 5
    project_id = body["id"]

    version = await session.scalar(
        select(BibleVersion).where(
            BibleVersion.project_id == uuid.UUID(project_id),
            BibleVersion.version == 0,
        )
    )
    assert version is not None
    assert version.snapshot_json["generated_from_template"] == "xianxia_starter"


@pytest.mark.integration
async def test_list_projects_scoped_to_user(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    user_b_headers: dict[str, str],
) -> None:
    await client.post(
        "/projects",
        json=project_create_payload(title="A Project"),
        headers=user_a_headers,
    )
    await client.post(
        "/projects",
        json=blank_project_payload(title="B Project"),
        headers=user_b_headers,
    )

    response = await client.get("/projects", headers=user_a_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "A Project"


@pytest.mark.integration
async def test_bible_staging_crud_does_not_mutate_bible_version(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    version_before = await session.scalar(
        select(BibleVersion).where(BibleVersion.project_id == uuid.UUID(project_id))
    )
    snapshot_before = dict(version_before.snapshot_json)  # type: ignore[union-attr]

    entry_resp = await client.post(
        f"/projects/{project_id}/bible/entries",
        json={
            "entry_key": "world_rules.test.entry",
            "section": "world_rules",
            "title": "Test Entry",
            "content_md": "Body",
        },
        headers=user_a_headers,
    )
    assert entry_resp.status_code == 201
    entry_id = entry_resp.json()["id"]

    patch_resp = await client.patch(
        f"/projects/{project_id}/bible/entries/{entry_id}",
        json={"content_md": "Updated body"},
        headers=user_a_headers,
    )
    assert patch_resp.status_code == 200

    await session.refresh(version_before)  # type: ignore[arg-type]
    assert version_before.snapshot_json == snapshot_before  # type: ignore[union-attr]

    delete_resp = await client.delete(
        f"/projects/{project_id}/bible/entries/{entry_id}",
        headers=user_a_headers,
    )
    assert delete_resp.status_code == 204


@pytest.mark.integration
async def test_list_chapters_and_characters(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=project_create_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    chapters_resp = await client.get(f"/projects/{project_id}/chapters", headers=user_a_headers)
    assert chapters_resp.status_code == 200
    assert chapters_resp.json()["pagination"]["total_items"] == 1

    characters_resp = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    assert characters_resp.status_code == 200
    assert characters_resp.json()["pagination"]["total_items"] == 2


@pytest.mark.integration
async def test_cross_tenant_project_access_denied(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    user_b_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=project_create_payload(title="Secret"), headers=user_b_headers
    )
    project_b_id = create_resp.json()["id"]

    response = await client.get(
        f"/projects/{project_b_id}/bible/entries",
        headers=user_a_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


@pytest.mark.integration
async def test_bible_settle_returns_501(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.post(
        f"/projects/{project_id}/bible/settle",
        headers=user_a_headers,
    )
    assert response.status_code == 501
    assert response.json()["error"]["code"] == "not_implemented"


@pytest.mark.integration
async def test_project_detail_and_archive(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(title="Archive Me"), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    detail_resp = await client.get(f"/projects/{project_id}", headers=user_a_headers)
    assert detail_resp.status_code == 200

    archive_resp = await client.delete(f"/projects/{project_id}", headers=user_a_headers)
    assert archive_resp.status_code == 204

    second_archive = await client.delete(f"/projects/{project_id}", headers=user_a_headers)
    assert second_archive.status_code == 204


@pytest.mark.integration
async def test_list_bible_versions(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=project_create_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    versions_resp = await client.get(
        f"/projects/{project_id}/bible/versions", headers=user_a_headers
    )
    assert versions_resp.status_code == 200
    assert versions_resp.json()["items"][0]["version"] == 0

    version_detail = await client.get(
        f"/projects/{project_id}/bible/versions/0", headers=user_a_headers
    )
    assert version_detail.status_code == 200
    assert version_detail.json()["entry_count"] == 5


@pytest.mark.integration
async def test_create_chapter_conflict(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=project_create_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    conflict_resp = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 1, "title": "Duplicate"},
        headers=user_a_headers,
    )
    assert conflict_resp.status_code == 409
    assert conflict_resp.json()["error"]["code"] == "chapter_number_conflict"


@pytest.mark.integration
async def test_entry_key_conflict(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    payload = {
        "entry_key": "world_rules.test",
        "section": "world_rules",
        "title": "One",
    }
    first = await client.post(
        f"/projects/{project_id}/bible/entries", json=payload, headers=user_a_headers
    )
    assert first.status_code == 201

    second = await client.post(
        f"/projects/{project_id}/bible/entries", json=payload, headers=user_a_headers
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "entry_key_conflict"
