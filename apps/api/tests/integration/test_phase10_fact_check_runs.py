"""Phase 10 fact-check run integration tests."""

import pytest
from httpx import AsyncClient

from tests.factories import project_create_payload


async def _chapter(client: AsyncClient, headers: dict[str, str]) -> tuple[str, str]:
    project_id = (
        await client.post("/projects", json=project_create_payload(), headers=headers)
    ).json()["id"]
    chapter_id = (await client.get(f"/projects/{project_id}/chapters", headers=headers)).json()[
        "items"
    ][0]["id"]
    return project_id, chapter_id


@pytest.mark.integration
async def test_reality_off_skips_run(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _chapter(client, user_a_headers)
    await client.patch(
        f"/projects/{project_id}/reality-settings",
        json={"reality_anchors": "off"},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "The wall fell on 9 November 1985."},
        headers=user_a_headers,
    )
    run = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/fact-check/runs",
        headers=user_a_headers,
    )
    assert run.status_code == 202
    body = run.json()
    assert body["status"] == "done"
    assert body["skipped_reason"] == "reality_off"
    assert body["claims"] == []


@pytest.mark.integration
async def test_fact_check_run_contradiction(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _chapter(client, user_a_headers)
    await client.patch(
        f"/projects/{project_id}/reality-settings",
        json={"reality_anchors": "strict"},
        headers=user_a_headers,
    )
    prose = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Crowds gathered as the wall fell on 9 November 1985."},
        headers=user_a_headers,
    )
    assert prose.status_code == 201

    run = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/fact-check/runs",
        headers=user_a_headers,
    )
    assert run.status_code == 202
    body = run.json()
    assert body["status"] == "done"
    assert body["summary"]["fail"] >= 1
    fail_claims = [c for c in body["claims"] if c["severity"] == "fail"]
    assert fail_claims
    assert fail_claims[0]["citations"]
    assert fail_claims[0]["proposed_correction"]


@pytest.mark.integration
async def test_duplicate_enqueue_pending(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.config import get_settings
    from app.services.fact_check.queue import SyncFactCheckQueue, reset_fact_check_queue

    monkeypatch.setenv("STORYFORGE_FACT_CHECK_SYNC", "0")
    get_settings.cache_clear()
    reset_fact_check_queue()
    monkeypatch.setattr(
        "app.services.fact_check_service.get_fact_check_queue",
        lambda: SyncFactCheckQueue(),
    )

    project_id, chapter_id = await _chapter(client, user_a_headers)
    await client.patch(
        f"/projects/{project_id}/reality-settings",
        json={"reality_anchors": "strict"},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "On 9 November 1985 history changed."},
        headers=user_a_headers,
    )
    first = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/fact-check/runs",
        headers=user_a_headers,
    )
    assert first.status_code == 202
    assert first.json()["status"] == "pending"

    second = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/fact-check/runs",
        headers=user_a_headers,
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "fact_check_run_pending"


@pytest.mark.integration
async def test_cross_tenant_run_404(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    user_b_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _chapter(client, user_a_headers)
    await client.patch(
        f"/projects/{project_id}/reality-settings",
        json={"reality_anchors": "strict"},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "On 9 November 1985."},
        headers=user_a_headers,
    )
    run = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/fact-check/runs",
        headers=user_a_headers,
    )
    run_id = run.json()["id"]
    foreign = await client.get(
        f"/projects/{project_id}/fact-check/runs/{run_id}",
        headers=user_b_headers,
    )
    assert foreign.status_code == 404
