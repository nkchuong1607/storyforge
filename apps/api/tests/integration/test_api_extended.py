"""Additional integration tests for coverage and edge cases."""

import pytest
from httpx import AsyncClient

from tests.factories import blank_project_payload, project_create_payload


@pytest.mark.integration
async def test_get_bible_entry_by_id(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    list_resp = await client.get(f"/projects/{project_id}/bible/entries", headers=user_a_headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["pagination"]["total_items"] == 0

    create_entry = await client.post(
        f"/projects/{project_id}/bible/entries",
        json={
            "entry_key": "world_rules.test",
            "section": "world_rules",
            "title": "Test",
        },
        headers=user_a_headers,
    )
    entry_id = create_entry.json()["id"]

    get_resp = await client.get(
        f"/projects/{project_id}/bible/entries/{entry_id}", headers=user_a_headers
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["entry_key"] == "world_rules.test"


@pytest.mark.integration
async def test_get_bible_entry_not_found(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]
    missing_id = "99999999-9999-4999-8999-999999999999"

    response = await client.get(
        f"/projects/{project_id}/bible/entries/{missing_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 404


@pytest.mark.integration
async def test_update_project_metadata(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(title="Original"), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/projects/{project_id}",
        json={"title": "Updated Title", "description": "New desc"},
        headers=user_a_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["title"] == "Updated Title"


@pytest.mark.integration
async def test_mystery_template_seeds(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    payload = project_create_payload(
        title="Mystery Case",
        template="mystery_starter",
        genre_profile="mystery",
    )
    response = await client.post("/projects", json=payload, headers=user_a_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["bible_entry_count"] == 4
    assert body["chapter_count"] == 1


@pytest.mark.integration
async def test_slug_conflict_on_explicit_slug(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    payload = blank_project_payload(title="One")
    payload["slug"] = "fixed-slug"
    first = await client.post("/projects", json=payload, headers=user_a_headers)
    assert first.status_code == 201

    second = await client.post("/projects", json=payload, headers=user_a_headers)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "slug_conflict"
    assert second.json()["error"]["details"][0]["suggested_slug"] == "fixed-slug-2"


@pytest.mark.integration
async def test_list_projects_with_search_query(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    await client.post(
        "/projects",
        json=blank_project_payload(title="Unique Alpha Title"),
        headers=user_a_headers,
    )
    await client.post(
        "/projects",
        json=blank_project_payload(title="Other"),
        headers=user_a_headers,
    )

    response = await client.get("/projects?q=Alpha", headers=user_a_headers)
    assert response.status_code == 200
    assert response.json()["pagination"]["total_items"] == 1


@pytest.mark.integration
async def test_list_bible_entries_with_section_filter(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=project_create_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.get(
        f"/projects/{project_id}/bible/entries?section=world_rules",
        headers=user_a_headers,
    )
    assert response.status_code == 200
    assert response.json()["pagination"]["total_items"] >= 2


@pytest.mark.integration
async def test_create_chapter_success(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 1, "title": "Chapter One"},
        headers=user_a_headers,
    )
    assert response.status_code == 201
    assert response.json()["number"] == 1


@pytest.mark.integration
async def test_invalid_user_id_header(client: AsyncClient) -> None:
    response = await client.get("/projects", headers={"X-User-Id": "invalid"})
    assert response.status_code == 401


@pytest.mark.integration
async def test_auto_slug_suffix_on_duplicate_title(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    payload = blank_project_payload(title="Duplicate Title")
    first = await client.post("/projects", json=payload, headers=user_a_headers)
    second = await client.post("/projects", json=payload, headers=user_a_headers)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["slug"] != second.json()["slug"]


@pytest.mark.integration
async def test_update_bible_entry_section_and_metadata(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]
    entry_resp = await client.post(
        f"/projects/{project_id}/bible/entries",
        json={
            "entry_key": "glossary.term",
            "section": "glossary",
            "title": "Term",
        },
        headers=user_a_headers,
    )
    entry_id = entry_resp.json()["id"]

    patch_resp = await client.patch(
        f"/projects/{project_id}/bible/entries/{entry_id}",
        json={
            "section": "timeline",
            "metadata": {"type": "note"},
            "title": "Updated Term",
        },
        headers=user_a_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["section"] == "timeline"


@pytest.mark.integration
async def test_delete_bible_entry(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]
    entry_resp = await client.post(
        f"/projects/{project_id}/bible/entries",
        json={
            "entry_key": "objects.item",
            "section": "objects",
            "title": "Item",
        },
        headers=user_a_headers,
    )
    entry_id = entry_resp.json()["id"]

    delete_resp = await client.delete(
        f"/projects/{project_id}/bible/entries/{entry_id}",
        headers=user_a_headers,
    )
    assert delete_resp.status_code == 204

    get_resp = await client.get(
        f"/projects/{project_id}/bible/entries/{entry_id}",
        headers=user_a_headers,
    )
    assert get_resp.status_code == 404


@pytest.mark.integration
async def test_get_unknown_project_returns_404(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    response = await client.get(
        "/projects/99999999-9999-4999-8999-999999999999",
        headers=user_a_headers,
    )
    assert response.status_code == 404


@pytest.mark.integration
async def test_get_missing_bible_version(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.get(
        f"/projects/{project_id}/bible/versions/99",
        headers=user_a_headers,
    )
    assert response.status_code == 404


@pytest.mark.integration
async def test_list_archived_projects(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create_resp = await client.post(
        "/projects", json=blank_project_payload(title="Archived"), headers=user_a_headers
    )
    project_id = create_resp.json()["id"]
    await client.delete(f"/projects/{project_id}", headers=user_a_headers)

    active_resp = await client.get("/projects", headers=user_a_headers)
    assert active_resp.json()["pagination"]["total_items"] == 0

    archived_resp = await client.get("/projects?status=archived", headers=user_a_headers)
    assert archived_resp.json()["pagination"]["total_items"] == 1
