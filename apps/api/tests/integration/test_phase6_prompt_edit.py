"""Phase 6 prompt edit integration tests (FakeLLM only)."""

import pytest
from httpx import AsyncClient

from tests.factories import project_create_payload


async def _setup_chapter(client: AsyncClient, headers: dict[str, str]) -> tuple[str, str]:
    create = await client.post("/projects", json=project_create_payload(), headers=headers)
    project_id = create.json()["id"]
    chapters = await client.get(f"/projects/{project_id}/chapters", headers=headers)
    chapter_id = chapters.json()["items"][0]["id"]
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong tu luyện yên bình trên núi Thanh Vân."},
        headers=headers,
    )
    return project_id, chapter_id


@pytest.mark.integration
async def test_prompt_edit_instruct_fake_llm(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)
    resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prompt-edit/instruct",
        json={"instruction": "Tăng tension", "base_prose_version": 1},
        headers=user_a_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["turn"]["provider"] == "fake"
    assert body["turn"]["model"] == "fake-llm"
    assert body["turn"]["proposed_content"] is not None
    assert "[AI_EDIT:" in body["turn"]["proposed_content"]


@pytest.mark.integration
async def test_prompt_edit_apply_creates_ai_editor_version(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)
    instruct = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prompt-edit/instruct",
        json={"instruction": "Viết ngắn hơn"},
        headers=user_a_headers,
    )
    session_id = instruct.json()["session_id"]
    turn_id = instruct.json()["turn"]["id"]
    apply_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prompt-edit/apply",
        json={"session_id": session_id, "turn_id": turn_id},
        headers=user_a_headers,
    )
    assert apply_resp.status_code == 201
    assert apply_resp.json()["prose_version"]["source"] == "ai_editor"
    assert apply_resp.json()["prose_version"]["version"] == 2

    double = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prompt-edit/apply",
        json={"session_id": session_id, "turn_id": turn_id},
        headers=user_a_headers,
    )
    assert double.status_code == 409


@pytest.mark.integration
async def test_prompt_edit_regenerate_new_turn(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)
    instruct = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prompt-edit/instruct",
        json={"instruction": "Tăng tension"},
        headers=user_a_headers,
    )
    session_id = instruct.json()["session_id"]
    turn_id = instruct.json()["turn"]["id"]
    regen = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prompt-edit/regenerate",
        json={"session_id": session_id, "turn_id": turn_id},
        headers=user_a_headers,
    )
    assert regen.status_code == 201
    assert regen.json()["turn"]["turn_index"] == 2

    sessions = await client.get(
        f"/projects/{project_id}/chapters/{chapter_id}/prompt-edit/sessions",
        headers=user_a_headers,
    )
    assert sessions.status_code == 200
    assert len(sessions.json()["items"][0]["turns"]) == 2


@pytest.mark.integration
async def test_locked_chapter_prompt_edit_409(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        json={"approve_state_diff": True},
        headers=user_a_headers,
    )
    resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prompt-edit/instruct",
        json={"instruction": "test"},
        headers=user_a_headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "chapter_locked"
