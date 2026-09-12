"""Phase 4 fairness integration tests."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ChapterStatus
from tests.factories import project_create_payload


async def _mystery_project(client: AsyncClient, headers: dict[str, str]) -> tuple[str, str, str]:
    create = await client.post(
        "/projects",
        json=project_create_payload(
            title="Mystery Case",
            template="mystery_starter",
            genre_profile="mystery",
        ),
        headers=headers,
    )
    assert create.status_code == 201
    project_id = create.json()["id"]
    chapters = await client.get(f"/projects/{project_id}/chapters", headers=headers)
    ch1_id = chapters.json()["items"][0]["id"]
    ch5 = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 5, "title": "Reveal"},
        headers=headers,
    )
    return project_id, ch1_id, ch5.json()["id"]


async def _prepare_payoff_chapter(
    client: AsyncClient,
    project_id: str,
    chapter_id: str,
    headers: dict[str, str],
) -> None:
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Payoff chapter prose for continuity check."},
        headers=headers,
    )


@pytest.mark.integration
async def test_mystery_payoff_without_plants_fail(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _, payoff_ch_id = await _mystery_project(client, user_a_headers)
    twist_resp = await client.post(
        f"/projects/{project_id}/twists",
        json={
            "title": "Killer identity",
            "secret_truth": "Butler did it",
            "constraints_json": {"min_plants_before_payoff": 2},
        },
        headers=user_a_headers,
    )
    twist_id = twist_resp.json()["id"]
    await client.post(
        f"/projects/{project_id}/twists/{twist_id}/payoffs",
        json={"target_chapter_id": payoff_ch_id, "min_plants": 2},
        headers=user_a_headers,
    )
    await _prepare_payoff_chapter(client, project_id, payoff_ch_id, user_a_headers)
    check = await client.post(
        f"/projects/{project_id}/chapters/{payoff_ch_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check.status_code == 200
    body = check.json()
    assert body["result"] == "fail"
    codes = {i["code"] for i in body["issues"]}
    assert "foreshadow_payoff_without_plants" in codes
    for issue in body["issues"]:
        if issue["category"] == "foreshadow":
            assert "secret_truth" not in str(issue.get("evidence", {}))


@pytest.mark.integration
async def test_xianxia_zero_plants_warn(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    create = await client.post(
        "/projects",
        json=project_create_payload(),
        headers=user_a_headers,
    )
    project_id = create.json()["id"]
    ch5 = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": 5, "title": "Reveal"},
        headers=user_a_headers,
    )
    payoff_ch = ch5.json()["id"]
    twist = await client.post(
        f"/projects/{project_id}/twists",
        json={"title": "Bloodline", "secret_truth": "Ancient blood"},
        headers=user_a_headers,
    )
    twist_id = twist.json()["id"]
    await client.post(
        f"/projects/{project_id}/twists/{twist_id}/payoffs",
        json={"target_chapter_id": payoff_ch, "min_plants": 1},
        headers=user_a_headers,
    )
    await _prepare_payoff_chapter(client, project_id, payoff_ch, user_a_headers)
    check = await client.post(
        f"/projects/{project_id}/chapters/{payoff_ch}/continuity-check",
        headers=user_a_headers,
    )
    assert check.status_code == 200
    assert check.json()["result"] == "warn"
    assert any(i["code"] == "foreshadow_payoff_without_plants" for i in check.json()["issues"])


@pytest.mark.integration
async def test_override_allows_settle_after_foreshadow_fail(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    project_id, _, payoff_ch_id = await _mystery_project(client, user_a_headers)
    twist_resp = await client.post(
        f"/projects/{project_id}/twists",
        json={"title": "Twist", "secret_truth": "Secret"},
        headers=user_a_headers,
    )
    twist_id = twist_resp.json()["id"]
    await client.post(
        f"/projects/{project_id}/twists/{twist_id}/payoffs",
        json={"target_chapter_id": payoff_ch_id, "min_plants": 1},
        headers=user_a_headers,
    )
    await _prepare_payoff_chapter(client, project_id, payoff_ch_id, user_a_headers)
    check = await client.post(
        f"/projects/{project_id}/chapters/{payoff_ch_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check.json()["result"] == "fail"
    fingerprint = next(
        i["fingerprint"]
        for i in check.json()["issues"]
        if i["code"] == "foreshadow_payoff_without_plants"
    )
    override = await client.post(
        f"/projects/{project_id}/chapters/{payoff_ch_id}/continuity-overrides",
        json={"issue_fingerprint": fingerprint, "reason": "Beta reader early reveal"},
        headers=user_a_headers,
    )
    assert override.status_code == 201

    settle = await client.post(
        f"/projects/{project_id}/chapters/{payoff_ch_id}/settle",
        json={"approve_state_diff": True},
        headers={**user_a_headers, "Idempotency-Key": str(uuid.uuid4())},
    )
    assert settle.status_code == 200
    twist_after = await client.get(
        f"/projects/{project_id}/twists/{twist_id}", headers=user_a_headers
    )
    assert twist_after.json()["status"] == "paid_off"


@pytest.mark.integration
async def test_unseeded_reveal_fail(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    from app.models.enums import TwistPlanStatus
    from app.models.twist import TwistPlan

    project_id, _, payoff_ch_id = await _mystery_project(client, user_a_headers)
    twist_resp = await client.post(
        f"/projects/{project_id}/twists",
        json={"title": "Early reveal", "secret_truth": "Hidden"},
        headers=user_a_headers,
    )
    twist_id = twist_resp.json()["id"]
    await client.post(
        f"/projects/{project_id}/twists/{twist_id}/payoffs",
        json={"target_chapter_id": payoff_ch_id, "min_plants": 1},
        headers=user_a_headers,
    )
    twist_row = await session.get(TwistPlan, uuid.UUID(twist_id))
    assert twist_row is not None
    twist_row.status = TwistPlanStatus.seeded
    await session.commit()
    await _prepare_payoff_chapter(client, project_id, payoff_ch_id, user_a_headers)
    check = await client.post(
        f"/projects/{project_id}/chapters/{payoff_ch_id}/continuity-check",
        headers=user_a_headers,
    )
    codes = {i["code"] for i in check.json()["issues"]}
    assert "foreshadow_unseeded_reveal" in codes


@pytest.mark.integration
async def test_plant_patch_locked_chapter_409(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    from sqlalchemy import select

    from app.models.chapter import Chapter

    create = await client.post(
        "/projects",
        json=project_create_payload(),
        headers=user_a_headers,
    )
    project_id = create.json()["id"]
    chapters = await client.get(f"/projects/{project_id}/chapters", headers=user_a_headers)
    ch_id = chapters.json()["items"][0]["id"]
    twist = await client.post(
        f"/projects/{project_id}/twists",
        json={"title": "T", "secret_truth": "S"},
        headers=user_a_headers,
    )
    twist_id = twist.json()["id"]
    plant = await client.post(
        f"/projects/{project_id}/twists/{twist_id}/plants",
        json={"chapter_id": ch_id, "salience": "soft", "snippet": "x"},
        headers=user_a_headers,
    )
    plant_id = plant.json()["id"]

    chapter = await session.scalar(select(Chapter).where(Chapter.id == uuid.UUID(ch_id)))
    assert chapter is not None
    chapter.status = ChapterStatus.locked
    await session.commit()

    patch = await client.patch(
        f"/projects/{project_id}/twists/{twist_id}/plants/{plant_id}",
        json={"snippet": "blocked"},
        headers=user_a_headers,
    )
    assert patch.status_code == 409
    assert patch.json()["error"]["code"] == "chapter_locked"
