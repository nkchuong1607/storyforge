"""Phase 9 research integration tests."""

import pytest
from httpx import AsyncClient

from tests.factories import project_create_payload


async def _project(client: AsyncClient, headers: dict[str, str]) -> str:
    resp = await client.post("/projects", json=project_create_payload(), headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.integration
async def test_research_crud_and_search(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _project(client, user_a_headers)
    create = await client.post(
        f"/projects/{project_id}/research/notes",
        json={
            "title": "Lịch sử Huyết Đan",
            "body_md": "Huyết Đan chỉ dùng khi tu luyện đạt Trúc Cơ",
            "tags": ["cultivation"],
        },
        headers=user_a_headers,
    )
    assert create.status_code == 201
    note_id = create.json()["id"]

    get_resp = await client.get(
        f"/projects/{project_id}/research/notes/{note_id}",
        headers=user_a_headers,
    )
    assert get_resp.status_code == 200

    search = await client.get(
        f"/projects/{project_id}/research/notes/search",
        params={"q": "Huyết"},
        headers=user_a_headers,
    )
    assert search.status_code == 200
    assert search.json()["total"] >= 1

    patch = await client.patch(
        f"/projects/{project_id}/research/notes/{note_id}",
        json={"title": "Updated title"},
        headers=user_a_headers,
    )
    assert patch.status_code == 200


@pytest.mark.integration
async def test_research_promote_to_staging(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _project(client, user_a_headers)
    create = await client.post(
        f"/projects/{project_id}/research/notes",
        json={"title": "Promote me", "body_md": "Canon candidate"},
        headers=user_a_headers,
    )
    note_id = create.json()["id"]
    promote = await client.post(
        f"/projects/{project_id}/research/notes/{note_id}/promote",
        json={"section": "world", "title": "World rule from research"},
        headers=user_a_headers,
    )
    assert promote.status_code == 200
    staging_id = promote.json()["staging_entry_id"]

    promote2 = await client.post(
        f"/projects/{project_id}/research/notes/{note_id}/promote",
        json={"section": "world", "title": "World rule from research"},
        headers=user_a_headers,
    )
    assert promote2.status_code == 200
    assert promote2.json()["staging_entry_id"] == staging_id

    patch = await client.patch(
        f"/projects/{project_id}/research/notes/{note_id}",
        json={"title": "Nope"},
        headers=user_a_headers,
    )
    assert patch.status_code == 409
    assert patch.json()["error"]["code"] == "note_not_editable"


@pytest.mark.integration
async def test_research_link_character(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = chars.json()["items"][0]["id"]
    note = await client.post(
        f"/projects/{project_id}/research/notes",
        json={"title": "Link test", "body_md": "body"},
        headers=user_a_headers,
    )
    note_id = note.json()["id"]
    link = await client.post(
        f"/projects/{project_id}/research/notes/{note_id}/links",
        json={"link_type": "character", "character_id": char_id},
        headers=user_a_headers,
    )
    assert link.status_code == 201
    dup = await client.post(
        f"/projects/{project_id}/research/notes/{note_id}/links",
        json={"link_type": "character", "character_id": char_id},
        headers=user_a_headers,
    )
    assert dup.status_code == 409


@pytest.mark.integration
async def test_research_cross_tenant(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    user_b_headers: dict[str, str],
) -> None:
    project_id = await _project(client, user_a_headers)
    note = await client.post(
        f"/projects/{project_id}/research/notes",
        json={"title": "Secret", "body_md": "x"},
        headers=user_a_headers,
    )
    note_id = note.json()["id"]
    forbidden = await client.get(
        f"/projects/{project_id}/research/notes/{note_id}",
        headers=user_b_headers,
    )
    assert forbidden.status_code == 404
