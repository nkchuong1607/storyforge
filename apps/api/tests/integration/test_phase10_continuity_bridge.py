"""Phase 10 continuity bridge integration tests."""

import pytest
from httpx import AsyncClient

from tests.factories import project_create_payload


async def _strict_run(client: AsyncClient, headers: dict[str, str]) -> tuple[str, str]:
    project_id = (
        await client.post("/projects", json=project_create_payload(), headers=headers)
    ).json()["id"]
    chapter_id = (await client.get(f"/projects/{project_id}/chapters", headers=headers)).json()[
        "items"
    ][0]["id"]
    await client.patch(
        f"/projects/{project_id}/reality-settings",
        json={"reality_anchors": "strict"},
        headers=headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "History records 9 November 1985 as pivotal."},
        headers=headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/fact-check/runs",
        headers=headers,
    )
    return project_id, chapter_id


@pytest.mark.integration
async def test_continuity_strict_shows_fact_check_warn(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _strict_run(client, user_a_headers)
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check.status_code == 200
    issues = [i for i in check.json()["issues"] if i.get("category") == "fact_check"]
    assert issues
    assert all(i["severity"] == "warn" for i in issues)


@pytest.mark.integration
async def test_continuity_soft_no_fact_check_category(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = (
        await client.post("/projects", json=project_create_payload(), headers=user_a_headers)
    ).json()["id"]
    chapter_id = (
        await client.get(f"/projects/{project_id}/chapters", headers=user_a_headers)
    ).json()["items"][0]["id"]
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "9 November 1985 in Berlin."},
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    issues = [i for i in check.json()["issues"] if i.get("category") == "fact_check"]
    assert not issues
