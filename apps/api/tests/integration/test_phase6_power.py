"""Phase 6 power system integration tests."""

import pytest
from httpx import AsyncClient

from tests.factories import blank_project_payload, project_create_payload


async def _setup_xianxia(client: AsyncClient, headers: dict[str, str]) -> str:
    resp = await client.post("/projects", json=project_create_payload(), headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_ranks(
    client: AsyncClient,
    project_id: str,
    headers: dict[str, str],
    *,
    include_nascent: bool = False,
) -> list[str]:
    names = [
        ("qi_refining", "Luyện Khí"),
        ("foundation", "Trúc Cơ"),
        ("core", "Kim Đan"),
    ]
    if include_nascent:
        names.append(("nascent", "Nguyên Anh"))
    ids: list[str] = []
    for key, name in names:
        r = await client.post(
            f"/projects/{project_id}/power-system/ranks",
            json={"rank_key": key, "display_name": name},
            headers=headers,
        )
        assert r.status_code == 201
        ids.append(r.json()["id"])
    return ids


@pytest.mark.integration
async def test_power_ranks_crud_and_reorder(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _setup_xianxia(client, user_a_headers)
    rank_ids = await _create_ranks(client, project_id, user_a_headers)

    listed = await client.get(f"/projects/{project_id}/power-system/ranks", headers=user_a_headers)
    assert listed.status_code == 200
    assert len(listed.json()["items"]) == len(rank_ids)

    reordered = await client.put(
        f"/projects/{project_id}/power-system/ranks/reorder",
        json={"rank_ids": list(reversed(rank_ids))},
        headers=user_a_headers,
    )
    assert reordered.status_code == 200
    assert reordered.json()["items"][0]["rank_key"] == "core"


@pytest.mark.integration
async def test_delete_rank_in_use_409(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _setup_xianxia(client, user_a_headers)
    rank_ids = await _create_ranks(client, project_id, user_a_headers)
    tech = await client.post(
        f"/projects/{project_id}/power-system/techniques",
        json={
            "technique_key": "azure_sword",
            "display_name": "Thanh Vân Kiếm",
            "min_rank_id": rank_ids[0],
        },
        headers=user_a_headers,
    )
    assert tech.status_code == 201
    deleted = await client.delete(
        f"/projects/{project_id}/power-system/ranks/{rank_ids[0]}",
        headers=user_a_headers,
    )
    assert deleted.status_code == 409
    assert deleted.json()["error"]["code"] == "rank_in_use"


@pytest.mark.integration
async def test_rank_jump_continuity_fail(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _setup_xianxia(client, user_a_headers)
    await _create_ranks(client, project_id, user_a_headers, include_nascent=True)
    chapters = await client.get(f"/projects/{project_id}/chapters", headers=user_a_headers)
    ch1_id = chapters.json()["items"][0]["id"]
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_name = chars.json()["items"][0]["display_name"]

    await client.post(
        f"/projects/{project_id}/chapters/{ch1_id}/prose-versions",
        json={
            "content": (
                f"{char_name} độ kiếp thành công, đột phá lên Trúc Cơ "
                "sau nhiều năm tu luyện Luyện Khí."
            )
        },
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{ch1_id}/continuity-check",
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{ch1_id}/settle",
        json={"approve_state_diff": True},
        headers=user_a_headers,
    )

    ch2 = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 2, "title": "Chương 2"},
        headers=user_a_headers,
    )
    ch2_id = ch2.json()["id"]
    await client.post(
        f"/projects/{project_id}/chapters/{ch2_id}/prose-versions",
        json={
            "content": (
                f"{char_name} trong một đêm đột phá thẳng lên Nguyên Anh không breakthrough."
            )
        },
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{ch2_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check.status_code == 200
    codes = [i["code"] for i in check.json()["issues"]]
    assert "power_rank_jump_without_breakthrough" in codes


@pytest.mark.integration
async def test_mystery_skips_power_rules(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    payload = blank_project_payload(title="Mystery")
    payload["genre_profile"] = "mystery"
    resp = await client.post("/projects", json=payload, headers=user_a_headers)
    project_id = resp.json()["id"]
    await client.patch(
        f"/projects/{project_id}/power-system/settings",
        json={"enabled": True},
        headers=user_a_headers,
    )
    rank = await client.post(
        f"/projects/{project_id}/power-system/ranks",
        json={"rank_key": "qi", "display_name": "Luyện Khí"},
        headers=user_a_headers,
    )
    assert rank.status_code == 201
    ch = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 1, "title": "Chương 1"},
        headers=user_a_headers,
    )
    chapter_id = ch.json()["id"]
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Nhân vật lên Kim Đan."},
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    power_codes = [i["code"] for i in check.json()["issues"] if i.get("category") == "power_system"]
    assert power_codes == []


@pytest.mark.integration
async def test_power_settings_and_technique_crud(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _setup_xianxia(client, user_a_headers)
    rank_ids = await _create_ranks(client, project_id, user_a_headers)
    settings = await client.patch(
        f"/projects/{project_id}/power-system/settings",
        json={"priority_gap": 3},
        headers=user_a_headers,
    )
    assert settings.status_code == 200
    assert settings.json()["priority_gap"] == 3

    tech = await client.post(
        f"/projects/{project_id}/power-system/techniques",
        json={
            "technique_key": "azure_sword",
            "display_name": "Thanh Vân Kiếm",
            "min_rank_id": rank_ids[0],
        },
        headers=user_a_headers,
    )
    assert tech.status_code == 201
    tech_id = tech.json()["id"]
    updated = await client.patch(
        f"/projects/{project_id}/power-system/techniques/{tech_id}",
        json={"notes_md": "Kiếm pháp cơ bản"},
        headers=user_a_headers,
    )
    assert updated.status_code == 200
    deleted = await client.delete(
        f"/projects/{project_id}/power-system/techniques/{tech_id}",
        headers=user_a_headers,
    )
    assert deleted.status_code == 204


@pytest.mark.integration
async def test_cross_tenant_power_404(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    user_b_headers: dict[str, str],
) -> None:
    project_id = await _setup_xianxia(client, user_a_headers)
    resp = await client.get(f"/projects/{project_id}/power-system/ranks", headers=user_b_headers)
    assert resp.status_code == 404


@pytest.mark.integration
async def test_genre_rule_pack_patch_and_reset(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id = await _setup_xianxia(client, user_a_headers)
    get_resp = await client.get(f"/projects/{project_id}/genre-rule-pack", headers=user_a_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["pack"]["modules"]["power_system"]["enabled"] is True

    patch = await client.patch(
        f"/projects/{project_id}/genre-rule-pack",
        json={"pack": {"thresholds": {"foreshadow_min_plants_default": 5}}},
        headers=user_a_headers,
    )
    assert patch.status_code == 200
    assert patch.json()["pack"]["thresholds"]["foreshadow_min_plants_default"] == 5

    reset = await client.post(
        f"/projects/{project_id}/genre-rule-pack/reset?confirm=true",
        headers=user_a_headers,
    )
    assert reset.status_code == 200
    assert reset.json()["pack"]["thresholds"]["foreshadow_min_plants_default"] == 1
