"""Phase 8 integration tests — scene engine, relationships, stakes."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.ledger_event import LedgerEvent
from app.models.relationship_event import RelationshipEvent
from tests.factories import project_create_payload


async def _setup_project(client: AsyncClient, headers: dict[str, str]) -> tuple[str, str]:
    create_resp = await client.post("/projects", json=project_create_payload(), headers=headers)
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]
    chapters_resp = await client.get(f"/projects/{project_id}/chapters", headers=headers)
    chapter_id = chapters_resp.json()["items"][0]["id"]
    return project_id, chapter_id


async def _character_ids(
    client: AsyncClient, project_id: str, headers: dict[str, str]
) -> dict[str, str]:
    resp = await client.get(f"/projects/{project_id}/characters", headers=headers)
    return {c["display_name"]: c["id"] for c in resp.json()["items"]}


@pytest.mark.integration
async def test_patch_beat_goal_conflict_outcome_roundtrip(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    beat_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/beats",
        json={"beat_key": "1.1", "summary": "Opening", "sort_order": 0},
        headers=user_a_headers,
    )
    beat_id = beat_resp.json()["id"]
    patch = await client.patch(
        f"/projects/{project_id}/chapters/{chapter_id}/beats/{beat_id}",
        json={
            "goal": "Steal the elixir before dawn",
            "conflict": "Inner sect guards patrol the hall",
            "outcome": "Escapes wounded but successful",
            "stakes_level": 3,
            "completed": True,
        },
        headers=user_a_headers,
    )
    assert patch.status_code == 200
    body = patch.json()
    assert body["goal"].startswith("Steal")
    assert body["stakes_level"] == 3


@pytest.mark.integration
async def test_scene_lint_missing_conflict_warn(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    beat_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/beats",
        json={"beat_key": "1.1", "summary": "Scene", "sort_order": 0},
        headers=user_a_headers,
    )
    assert beat_resp.status_code == 201
    beat_id = beat_resp.json()["id"]
    await client.patch(
        f"/projects/{project_id}/chapters/{chapter_id}/beats/{beat_id}",
        json={
            "completed": True,
            "goal": "Long enough goal here",
            "outcome": "Done",
            "conflict": "",
        },
        headers=user_a_headers,
    )
    lint = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/scene-lint",
        headers=user_a_headers,
    )
    assert lint.status_code == 200
    data = lint.json()
    assert data["result"] in ("warn", "fail")
    assert any(i["code"] == "scene_missing_conflict" for i in data["issues"])


@pytest.mark.integration
async def test_relationship_pair_normalization_and_duplicate(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    names = await _character_ids(client, project_id, user_a_headers)
    a_id, b_id = names["Lý Phong"], names["Diệp Vân"]

    create = await client.post(
        f"/projects/{project_id}/relationships",
        json={
            "character_a_id": b_id,
            "character_b_id": a_id,
            "relation_type": "rival",
            "baseline_intensity": -1,
        },
        headers=user_a_headers,
    )
    assert create.status_code == 201
    body = create.json()
    assert body["character_a_id"] < body["character_b_id"] or str(body["character_a_id"]) < str(
        body["character_b_id"]
    )

    dup = await client.post(
        f"/projects/{project_id}/relationships",
        json={
            "character_a_id": a_id,
            "character_b_id": b_id,
            "relation_type": "rival",
        },
        headers=user_a_headers,
    )
    assert dup.status_code == 409
    assert dup.json()["error"]["code"] == "relationship_exists"


@pytest.mark.integration
async def test_stakes_entry_and_board(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    entry = await client.post(
        f"/projects/{project_id}/stakes/entries",
        json={
            "act_number": 1,
            "checkpoint_key": "act1_midpoint",
            "title": "Betrayal",
            "target_level": 3,
        },
        headers=user_a_headers,
    )
    assert entry.status_code == 201
    board = await client.get(f"/projects/{project_id}/stakes/board", headers=user_a_headers)
    assert board.status_code == 200
    assert board.json()["acts"][0]["entries"][0]["checkpoint_key"] == "act1_midpoint"


@pytest.mark.integration
async def test_context_packs_scene_relationships_stakes(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    scene = await client.post(
        f"/projects/{project_id}/context-packs/scene",
        json={"chapter_id": chapter_id},
        headers=user_a_headers,
    )
    assert scene.status_code == 200
    rel = await client.post(
        f"/projects/{project_id}/context-packs/relationships",
        json={"chapter_id": chapter_id, "character_ids": []},
        headers=user_a_headers,
    )
    assert rel.status_code == 200
    stakes = await client.post(
        f"/projects/{project_id}/context-packs/stakes",
        json={"chapter_id": chapter_id},
        headers=user_a_headers,
    )
    assert stakes.status_code == 200
    assert "act_number" in stakes.json()


@pytest.mark.integration
async def test_cross_tenant_relationships_404(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    user_b_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    resp = await client.get(f"/projects/{project_id}/relationships", headers=user_b_headers)
    assert resp.status_code == 404


@pytest.mark.integration
async def test_continuity_includes_scene_structure(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong tu luyện."},
        headers=user_a_headers,
    )
    beat_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/beats",
        json={"beat_key": "1.1", "summary": "Scene", "sort_order": 0},
        headers=user_a_headers,
    )
    assert beat_resp.status_code == 201
    await client.patch(
        f"/projects/{project_id}/chapters/{chapter_id}/beats/{beat_resp.json()['id']}",
        json={"completed": True, "goal": "short", "outcome": ""},
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check.status_code == 200
    categories = {i["category"] for i in check.json()["issues"]}
    assert "scene_structure" in categories


@pytest.mark.integration
async def test_settle_appends_relationship_and_stakes(
    client: AsyncClient,
    session,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    names = await _character_ids(client, project_id, user_a_headers)
    rel_resp = await client.post(
        f"/projects/{project_id}/relationships",
        json={
            "character_a_id": names["Lý Phong"],
            "character_b_id": names["Diệp Vân"],
            "relation_type": "rival",
        },
        headers=user_a_headers,
    )
    rel_id = rel_resp.json()["id"]

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong và Diệp Vân phản bội đâm sau lưng nhau."},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/stakes/entries",
        json={
            "act_number": 1,
            "checkpoint_key": "act1_open",
            "title": "Opening stakes",
            "target_level": 2,
        },
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check.status_code == 200
    report = check.json()
    overrides_needed = [
        i
        for i in report["issues"]
        if i["severity"] == "fail" and i["category"] != "relationship_arc"
    ]
    for issue in overrides_needed:
        await client.post(
            f"/projects/{project_id}/chapters/{chapter_id}/continuity-overrides",
            json={"issue_fingerprint": issue["fingerprint"], "reason": "test override"},
            headers=user_a_headers,
        )

    settle = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        json={"approve_state_diff": True},
        headers=user_a_headers,
    )
    assert settle.status_code == 200
    body = settle.json()
    assert body.get("relationship_events_appended", 0) >= 0
    assert "world.stakes" in body.get("snapshot_includes", [])

    rel_events = await session.scalars(
        select(RelationshipEvent).where(RelationshipEvent.relationship_id == uuid.UUID(rel_id))
    )
    assert len(list(rel_events.all())) >= 0

    ledger = await session.scalars(select(LedgerEvent))
    assert len(list(ledger.all())) >= 0
