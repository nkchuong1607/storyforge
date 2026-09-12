"""Phase 5 OOC integration tests."""

import uuid

import pytest
from httpx import AsyncClient

from tests.integration.test_phase5 import _promote_to_t3, _setup_project


@pytest.mark.integration
async def test_ooc_fail_blocks_settle(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")
    await _promote_to_t3(client, project_id, char_id, user_a_headers)

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong hạ sát dân thường trong làng."},
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check.status_code == 200
    psych_issues = [
        i
        for i in check.json()["issues"]
        if i["category"] == "psychology" and i["severity"] == "fail"
    ]
    assert any(i["code"] == "psych_ooc_moral_boundary_violation" for i in psych_issues)

    settle = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers={**user_a_headers, "Idempotency-Key": str(uuid.uuid4())},
    )
    assert settle.status_code == 409
    assert settle.json()["error"]["code"] == "continuity_fail_blocks_settle"


@pytest.mark.integration
async def test_ooc_override_allows_settle(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")
    await _promote_to_t3(client, project_id, char_id, user_a_headers)

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong hạ sát dân thường trong làng."},
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    fail_issue = next(
        i for i in check.json()["issues"] if i["code"] == "psych_ooc_moral_boundary_violation"
    )

    override = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-overrides",
        json={"issue_fingerprint": fail_issue["fingerprint"], "reason": "Cố ý — ma đạo"},
        headers=user_a_headers,
    )
    assert override.status_code == 201

    settle = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers={**user_a_headers, "Idempotency-Key": str(uuid.uuid4())},
    )
    assert settle.status_code == 200


@pytest.mark.integration
async def test_ooc_allow_moral_break_warn_or_pass(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")
    await _promote_to_t3(client, project_id, char_id, user_a_headers, allow_moral_break=True)

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong hạ sát dân thường trong làng."},
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    psych_issues = [i for i in check.json()["issues"] if i["category"] == "psychology"]
    assert not any(i["severity"] == "fail" for i in psych_issues)
    assert any(i["code"] == "psych_moral_boundary_crossed" for i in psych_issues)


@pytest.mark.integration
async def test_value_jump_warn(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")
    await _promote_to_t3(client, project_id, char_id, user_a_headers)

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong bỏ rơi gia đình để trả thù."},
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    codes = [i["code"] for i in check.json()["issues"]]
    assert "psych_value_hierarchy_jump" in codes


@pytest.mark.integration
async def test_arc_skip_warn(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")
    await _promote_to_t3(client, project_id, char_id, user_a_headers)
    await client.patch(
        f"/projects/{project_id}/characters/{char_id}/psyche-card",
        json={
            "psyche_card": {
                "arc_flags": {
                    "expected_arc_beats": ["betrayal_ch7", "redemption_ch15"],
                }
            }
        },
        headers=user_a_headers,
    )

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong redemption_ch15 trên đỉnh núi."},
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    codes = [i["code"] for i in check.json()["issues"]]
    assert "psych_arc_beat_skip" in codes


@pytest.mark.integration
async def test_t0_extra_no_psychology_issue(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    create = await client.post(
        f"/projects/{project_id}/characters",
        json={"display_name": "Extra", "role_one_liner": "extra", "tier": 0},
        headers=user_a_headers,
    )
    assert create.status_code == 201

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Extra hạ sát dân thường trong làng."},
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    psych_issues = [i for i in check.json()["issues"] if i["category"] == "psychology"]
    assert psych_issues == []
