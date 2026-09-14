"""Phase 10 settle guard integration tests."""

import pytest
from httpx import AsyncClient

from tests.factories import project_create_payload


async def _prepare_chapter(
    client: AsyncClient, headers: dict[str, str], *, block: bool
) -> tuple[str, str]:
    project_id = (
        await client.post("/projects", json=project_create_payload(), headers=headers)
    ).json()["id"]
    chapter_id = (await client.get(f"/projects/{project_id}/chapters", headers=headers)).json()[
        "items"
    ][0]["id"]
    await client.patch(
        f"/projects/{project_id}/reality-settings",
        json={"reality_anchors": "strict", "fact_check_blocks_settle": block},
        headers=headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "On 9 November 1985 the wall fell."},
        headers=headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/fact-check/runs",
        headers=headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=headers,
    )
    await client.patch(
        f"/projects/{project_id}/chapters/{chapter_id}",
        json={"status": "reviewing"},
        headers=headers,
    )
    return project_id, chapter_id


@pytest.mark.integration
async def test_settle_default_allows_open_fact_check_fail(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _prepare_chapter(client, user_a_headers, block=False)
    settle = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        json={"approve_state_diff": True},
        headers=user_a_headers,
    )
    assert settle.status_code in (200, 409)
    if settle.status_code == 409:
        assert settle.json()["error"]["code"] != "fact_check_fail_blocks_settle"


@pytest.mark.integration
async def test_settle_blocks_when_fact_check_setting_enabled(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _prepare_chapter(client, user_a_headers, block=True)
    settle = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        json={"approve_state_diff": True},
        headers=user_a_headers,
    )
    assert settle.status_code == 409
    assert settle.json()["error"]["code"] == "fact_check_fail_blocks_settle"
