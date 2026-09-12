"""Phase 5 integration tests — psyche card, psych states, context pack."""

import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.psych_state import PsychState
from tests.factories import project_create_payload


async def _setup_project(client: AsyncClient, headers: dict[str, str]) -> tuple[str, str]:
    create_resp = await client.post("/projects", json=project_create_payload(), headers=headers)
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]
    chapters_resp = await client.get(f"/projects/{project_id}/chapters", headers=headers)
    chapter_id = chapters_resp.json()["items"][0]["id"]
    return project_id, chapter_id


async def _promote_to_t3(
    client: AsyncClient,
    project_id: str,
    char_id: str,
    headers: dict[str, str],
    *,
    allow_moral_break: bool = False,
) -> None:
    await client.patch(
        f"/projects/{project_id}/characters/{char_id}",
        json={"metadata": {"voice_hint": "trầm", "arc_note": "báo thù"}},
        headers=headers,
    )
    await client.post(
        f"/projects/{project_id}/characters/{char_id}/promote-tier",
        headers=headers,
    )
    await client.patch(
        f"/projects/{project_id}/characters/{char_id}/psyche-card",
        json={
            "psyche_card": {
                "drive": "Báo thù",
                "value_hierarchy": ["gia đình", "công lý"],
                "moral_boundaries": ["không giết vô tội"],
                "arc_flags": {"allow_moral_break": allow_moral_break},
            }
        },
        headers=headers,
    )
    await client.post(
        f"/projects/{project_id}/characters/{char_id}/promote-tier",
        headers=headers,
    )
    await client.post(
        f"/projects/{project_id}/characters/{char_id}/promote-tier",
        json={"confirm_t3": True},
        headers=headers,
    )


@pytest.mark.integration
async def test_psyche_card_get_patch_merge(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")

    get_resp = await client.get(
        f"/projects/{project_id}/characters/{char_id}/psyche-card",
        headers=user_a_headers,
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["character_id"] == char_id

    patch_resp = await client.patch(
        f"/projects/{project_id}/characters/{char_id}/psyche-card",
        json={"psyche_card": {"drive": "Tu luyện", "moral_boundaries": ["test"]}},
        headers=user_a_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["psyche_card"]["drive"] == "Tu luyện"


@pytest.mark.integration
async def test_patch_invalid_t3_psyche_card_422(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")
    await _promote_to_t3(client, project_id, char_id, user_a_headers)

    bad = await client.patch(
        f"/projects/{project_id}/characters/{char_id}/psyche-card",
        json={"psyche_card": {"moral_boundaries": []}},
        headers=user_a_headers,
    )
    assert bad.status_code == 422
    assert bad.json()["error"]["code"] == "invalid_psyche_card"


@pytest.mark.integration
async def test_settle_appends_psych_states(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")
    await _promote_to_t3(client, project_id, char_id, user_a_headers)

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong tu luyện yên bình trên núi."},
        headers=user_a_headers,
    )
    check = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check.status_code == 200
    assert "psych_state_proposals" in check.json()["state_diff"]

    settle = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers={**user_a_headers, "Idempotency-Key": str(uuid.uuid4())},
    )
    assert settle.status_code == 200
    assert settle.json()["psych_states_appended"] >= 1

    timeline = await client.get(
        f"/projects/{project_id}/characters/{char_id}/psych-states",
        headers=user_a_headers,
    )
    assert timeline.status_code == 200
    assert len(timeline.json()["items"]) >= 1
    assert timeline.json()["items"][0]["chapter_number"] == 1


@pytest.mark.integration
async def test_psych_state_by_chapter_404_before_settle(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")

    resp = await client.get(
        f"/projects/{project_id}/characters/{char_id}/psych-states/by-chapter/{chapter_id}",
        headers=user_a_headers,
    )
    assert resp.status_code == 404


@pytest.mark.integration
async def test_psych_state_immutable_patch_409(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")
    await _promote_to_t3(client, project_id, char_id, user_a_headers)

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong tu luyện."},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers={**user_a_headers, "Idempotency-Key": str(uuid.uuid4())},
    )

    timeline = await client.get(
        f"/projects/{project_id}/characters/{char_id}/psych-states",
        headers=user_a_headers,
    )
    psych_state_id = timeline.json()["items"][0]["id"]

    patch = await client.patch(
        f"/projects/{project_id}/characters/{char_id}/psych-states/{psych_state_id}",
        headers=user_a_headers,
    )
    assert patch.status_code == 409
    assert patch.json()["error"]["code"] == "psych_state_immutable"


@pytest.mark.integration
async def test_duplicate_psych_state_settle_409(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")
    await _promote_to_t3(client, project_id, char_id, user_a_headers)

    now = datetime.now(UTC)
    session.add(
        PsychState(
            project_id=uuid.UUID(project_id),
            character_id=uuid.UUID(char_id),
            chapter_id=uuid.UUID(chapter_id),
            stress_level=5,
            dominant_emotion="calm",
            active_goal="test",
            settled_at=now,
            created_at=now,
        )
    )
    await session.commit()

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong tu luyện."},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )

    settle = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers={**user_a_headers, "Idempotency-Key": str(uuid.uuid4())},
    )
    assert settle.status_code == 409
    assert settle.json()["error"]["code"] == "psych_state_already_settled"


@pytest.mark.integration
async def test_psych_context_pack(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")
    await _promote_to_t3(client, project_id, char_id, user_a_headers)

    resp = await client.post(
        f"/projects/{project_id}/context-packs/psych",
        json={"chapter_id": chapter_id, "character_ids": [char_id]},
        headers=user_a_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["entries"]) == 1
    assert body["entries"][0]["psyche_summary"]["drive"] == "Báo thù"


@pytest.mark.integration
async def test_cross_tenant_psych_states_404(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    user_b_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_b_headers)
    chars = await client.get(f"/projects/{project_id}/characters", headers=user_b_headers)
    char_id = next(c["id"] for c in chars.json()["items"] if c["display_name"] == "Lý Phong")

    resp = await client.get(
        f"/projects/{project_id}/characters/{char_id}/psych-states",
        headers=user_a_headers,
    )
    assert resp.status_code == 404
