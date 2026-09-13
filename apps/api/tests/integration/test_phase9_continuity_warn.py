"""Phase 9 continuity WARN integration tests."""

import pytest
from httpx import AsyncClient

from tests.factories import project_create_payload


@pytest.mark.integration
async def test_continuity_research_orphan_warn(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = (
        await client.post("/projects", json=project_create_payload(), headers=user_a_headers)
    ).json()["id"]
    chapters = await client.get(f"/projects/{project_id}/chapters", headers=user_a_headers)
    chapter_id = chapters.json()["items"][0]["id"]
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = chars.json()["items"][0]["id"]

    note = await client.post(
        f"/projects/{project_id}/research/notes",
        json={"title": "Orphan link", "body_md": "test"},
        headers=user_a_headers,
    )
    note_id = note.json()["id"]
    await client.post(
        f"/projects/{project_id}/research/notes/{note_id}/links",
        json={"link_type": "character", "character_id": char_id},
        headers=user_a_headers,
    )
    await client.patch(
        f"/projects/{project_id}/characters/{char_id}",
        json={"status": "archived"},
        headers=user_a_headers,
    )

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong tu luyện trên núi."},
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check.status_code == 200
    issues = check.json()["issues"]
    research_issues = [i for i in issues if i.get("category") == "research"]
    if research_issues:
        assert all(i["severity"] == "warn" for i in research_issues)
        assert any(i["code"] == "research_link_orphan_character" for i in research_issues)
