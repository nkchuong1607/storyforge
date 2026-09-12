"""Phase 4 integration tests — twists, board, context packs."""

import pytest
from httpx import AsyncClient

from app.services.twist_context_pack import json_has_secret_truth_key
from tests.factories import project_create_payload


async def _setup_project(
    client: AsyncClient,
    headers: dict[str, str],
    *,
    genre_profile: str = "xianxia",
    template: str = "xianxia_starter",
) -> tuple[str, str]:
    create_resp = await client.post(
        "/projects",
        json=project_create_payload(genre_profile=genre_profile, template=template),
        headers=headers,
    )
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]
    chapters_resp = await client.get(f"/projects/{project_id}/chapters", headers=headers)
    chapter_id = chapters_resp.json()["items"][0]["id"]
    return project_id, chapter_id


async def _create_twist(
    client: AsyncClient,
    project_id: str,
    headers: dict[str, str],
    *,
    title: str = "Sát thủ là sư phụ",
    secret_truth: str = "Sư phụ Thanh Phong đã giết môn chủ cũ.",
) -> dict:
    resp = await client.post(
        f"/projects/{project_id}/twists",
        json={"title": title, "secret_truth": secret_truth},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.integration
async def test_list_twists_pagination(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    await _create_twist(client, project_id, user_a_headers)
    resp = await client.get(f"/projects/{project_id}/twists", headers=user_a_headers)
    assert resp.status_code == 200
    assert resp.json()["pagination"]["total_items"] >= 1


@pytest.mark.integration
async def test_create_twist_seeded(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    body = await _create_twist(client, project_id, user_a_headers)
    assert body["status"] == "seeded"
    assert body["plant_count"] == 0


@pytest.mark.integration
async def test_plant_transitions_to_planted(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    plant_resp = await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/plants",
        json={
            "chapter_id": chapter_id,
            "salience": "hard",
            "snippet": "Mùi hương quen thuộc",
        },
        headers=user_a_headers,
    )
    assert plant_resp.status_code == 201
    twist_resp = await client.get(
        f"/projects/{project_id}/twists/{twist['id']}", headers=user_a_headers
    )
    assert twist_resp.json()["status"] == "planted"


@pytest.mark.integration
async def test_payoff_transitions_to_armed(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    ch2 = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 5, "title": "Payoff chapter"},
        headers=user_a_headers,
    )
    assert ch2.status_code == 201
    payoff_ch_id = ch2.json()["id"]
    payoff_resp = await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/payoffs",
        json={"target_chapter_id": payoff_ch_id, "min_plants": 1},
        headers=user_a_headers,
    )
    assert payoff_resp.status_code == 201
    twist_resp = await client.get(
        f"/projects/{project_id}/twists/{twist['id']}", headers=user_a_headers
    )
    assert twist_resp.json()["status"] == "armed"


@pytest.mark.integration
async def test_writer_audience_strips_secret_truth(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    resp = await client.get(
        f"/projects/{project_id}/twists/{twist['id']}?audience=writer",
        headers=user_a_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "secret_truth" not in body or body.get("secret_truth") is None
    assert body.get("misdirection") is None


@pytest.mark.integration
async def test_context_pack_no_secret_truth(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/plants",
        json={"chapter_id": chapter_id, "salience": "soft", "snippet": "hint"},
        headers=user_a_headers,
    )
    pack_resp = await client.post(
        f"/projects/{project_id}/context-packs/twists",
        json={"chapter_id": chapter_id, "chapter_number": 1, "audience": "writer"},
        headers=user_a_headers,
    )
    assert pack_resp.status_code == 200
    body = pack_resp.json()
    assert body["meta"]["secret_truth_stripped"] is True
    assert not json_has_secret_truth_key(body)


@pytest.mark.integration
async def test_board_four_columns(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/plants",
        json={"chapter_id": chapter_id, "salience": "soft", "snippet": "plant"},
        headers=user_a_headers,
    )
    ch2 = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 12, "title": "Reveal"},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/payoffs",
        json={"target_chapter_id": ch2.json()["id"], "min_plants": 2},
        headers=user_a_headers,
    )
    board = await client.get(f"/projects/{project_id}/twists/board", headers=user_a_headers)
    assert board.status_code == 200
    columns = {c["id"]: c for c in board.json()["columns"]}
    assert set(columns) == {"secrets", "plants", "payoffs", "revealed"}
    assert any(c["card_type"] == "plant" for c in columns["plants"]["cards"])
    assert any(c["card_type"] == "payoff" for c in columns["payoffs"]["cards"])


@pytest.mark.integration
async def test_cross_tenant_twist_404(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    user_b_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    resp = await client.get(
        f"/projects/{project_id}/twists/{twist['id']}",
        headers=user_b_headers,
    )
    assert resp.status_code == 404


@pytest.mark.integration
async def test_second_payoff_422(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    ch2 = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 5, "title": "Payoff"},
        headers=user_a_headers,
    )
    target_id = ch2.json()["id"]
    first = await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/payoffs",
        json={"target_chapter_id": target_id},
        headers=user_a_headers,
    )
    assert first.status_code == 201
    second = await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/payoffs",
        json={"target_chapter_id": chapter_id},
        headers=user_a_headers,
    )
    assert second.status_code == 422
    assert second.json()["error"]["code"] == "payoff_already_exists"


@pytest.mark.integration
async def test_transition_abandon_twist(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/plants",
        json={"chapter_id": chapter_id, "salience": "soft", "snippet": "hint"},
        headers=user_a_headers,
    )
    resp = await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/transition",
        json={"status": "abandoned"},
        headers=user_a_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "abandoned"


@pytest.mark.integration
async def test_patch_twist_and_list_with_filter(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    patch = await client.patch(
        f"/projects/{project_id}/twists/{twist['id']}",
        json={"title": "Updated title", "misdirection": "New trail"},
        headers=user_a_headers,
    )
    assert patch.status_code == 200
    assert patch.json()["title"] == "Updated title"
    get_resp = await client.get(
        f"/projects/{project_id}/twists/{twist['id']}",
        headers=user_a_headers,
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["misdirection"] == "New trail"


@pytest.mark.integration
async def test_abandon_twist_via_delete(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    resp = await client.delete(
        f"/projects/{project_id}/twists/{twist['id']}",
        headers=user_a_headers,
    )
    assert resp.status_code == 204
    get_resp = await client.get(
        f"/projects/{project_id}/twists/{twist['id']}",
        headers=user_a_headers,
    )
    assert get_resp.json()["status"] == "abandoned"


@pytest.mark.integration
async def test_list_plants_for_twist(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/plants",
        json={"chapter_id": chapter_id, "salience": "hard", "snippet": "x"},
        headers=user_a_headers,
    )
    resp = await client.get(
        f"/projects/{project_id}/twists/{twist['id']}/plants",
        headers=user_a_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


@pytest.mark.integration
async def test_delete_plant_and_payoff(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    twist = await _create_twist(client, project_id, user_a_headers)
    plant = await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/plants",
        json={"chapter_id": chapter_id, "salience": "soft", "snippet": "temp"},
        headers=user_a_headers,
    )
    plant_id = plant.json()["id"]
    ch5 = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 8, "title": "Payoff"},
        headers=user_a_headers,
    )
    payoff = await client.post(
        f"/projects/{project_id}/twists/{twist['id']}/payoffs",
        json={"target_chapter_id": ch5.json()["id"], "min_plants": 1},
        headers=user_a_headers,
    )
    payoff_id = payoff.json()["id"]

    get_payoff = await client.get(
        f"/projects/{project_id}/twists/{twist['id']}/payoffs",
        headers=user_a_headers,
    )
    assert get_payoff.status_code == 200

    del_payoff = await client.delete(
        f"/projects/{project_id}/twists/{twist['id']}/payoffs/{payoff_id}",
        headers=user_a_headers,
    )
    assert del_payoff.status_code == 204

    del_plant = await client.delete(
        f"/projects/{project_id}/twists/{twist['id']}/plants/{plant_id}",
        headers=user_a_headers,
    )
    assert del_plant.status_code == 204


@pytest.mark.integration
async def test_promise_kind_same_gates(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    resp = await client.post(
        f"/projects/{project_id}/twists",
        json={
            "title": "Promise arc",
            "secret_truth": "Hero will return",
            "kind": "promise",
        },
        headers=user_a_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["kind"] == "promise"
    assert resp.json()["status"] == "seeded"
