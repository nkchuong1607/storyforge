"""Phase 10 reality settings integration tests."""

import pytest
from httpx import AsyncClient

from tests.factories import project_create_payload


async def _project_id(client: AsyncClient, headers: dict[str, str]) -> str:
    resp = await client.post("/projects", json=project_create_payload(), headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.integration
async def test_reality_settings_defaults(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _project_id(client, user_a_headers)
    resp = await client.get(
        f"/projects/{project_id}/reality-settings",
        headers=user_a_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["reality_anchors"] == "soft"
    assert body["fact_check_blocks_settle"] is False
    assert body["include_research_notes"] is True


@pytest.mark.integration
async def test_reality_settings_patch_strict(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _project_id(client, user_a_headers)
    patch = await client.patch(
        f"/projects/{project_id}/reality-settings",
        json={
            "reality_anchors": "strict",
            "enabled_categories": ["date", "place"],
            "fact_check_blocks_settle": True,
        },
        headers=user_a_headers,
    )
    assert patch.status_code == 200
    body = patch.json()
    assert body["reality_anchors"] == "strict"
    assert body["enabled_categories"] == ["date", "place"]
    assert body["fact_check_blocks_settle"] is True
