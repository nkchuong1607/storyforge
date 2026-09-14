"""Phase 10 claim disposition and promote integration tests."""

import pytest
from httpx import AsyncClient

from tests.factories import project_create_payload


async def _run_with_fail_claim(
    client: AsyncClient, headers: dict[str, str]
) -> tuple[str, str, dict]:
    project_id = (
        await client.post("/projects", json=project_create_payload(), headers=headers)
    ).json()["id"]
    chapter_id = (await client.get(f"/projects/{project_id}/chapters", headers=headers)).json()[
        "items"
    ][0]["id"]
    await client.patch(
        f"/projects/{project_id}/reality-settings",
        json={"reality_anchors": "strict"},
        headers=headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "The Berlin wall fell on 9 November 1985."},
        headers=headers,
    )
    run = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/fact-check/runs",
        headers=headers,
    )
    body = run.json()
    fail_claim = next(c for c in body["claims"] if c["severity"] == "fail")
    return project_id, chapter_id, fail_claim


@pytest.mark.integration
async def test_disposition_intentional_fiction(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _chapter_id, claim = await _run_with_fail_claim(client, user_a_headers)
    resp = await client.post(
        f"/projects/{project_id}/fact-check/claims/{claim['id']}/disposition",
        json={"disposition": "intentional_fiction", "note": "Alt history"},
        headers=user_a_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["author_disposition"] == "intentional_fiction"


@pytest.mark.integration
async def test_accept_fix_handoff_no_prose_mutation(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id, claim = await _run_with_fail_claim(client, user_a_headers)
    before = await client.get(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions/1",
        headers=user_a_headers,
    )
    accept = await client.post(
        f"/projects/{project_id}/fact-check/claims/{claim['id']}/accept-fix",
        json={"handoff_target": "prompt_edit"},
        headers=user_a_headers,
    )
    assert accept.status_code == 200
    payload = accept.json()["handoff_payload"]
    assert payload["original_text"]
    assert payload["suggested_replacement"]
    after = await client.get(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions/1",
        headers=user_a_headers,
    )
    assert after.json()["content"] == before.json()["content"]


@pytest.mark.integration
async def test_promote_evidence_creates_research_note(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _chapter_id, claim = await _run_with_fail_claim(client, user_a_headers)
    promote = await client.post(
        f"/projects/{project_id}/fact-check/claims/{claim['id']}/promote-evidence",
        json={"note_title": "Berlin Wall fall date", "tags": ["berlin"]},
        headers=user_a_headers,
    )
    assert promote.status_code == 201
    body = promote.json()
    assert body["research_note_id"]
    assert "fact-check" in body["research_note"]["tags"]

    again = await client.post(
        f"/projects/{project_id}/fact-check/claims/{claim['id']}/promote-evidence",
        headers=user_a_headers,
    )
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "claim_already_promoted"
