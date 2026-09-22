"""Phase 11 Mystery CraftPack integration tests."""

import json
from pathlib import Path

import pytest
from httpx import AsyncClient

from tests.factories import project_create_payload

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "golden" / "mystery_fair_play"
MYSTERY_PACK_ID = "mystery.fair_play.v1"


async def _golden_mystery_project(
    client: AsyncClient, headers: dict[str, str]
) -> tuple[str, str, str]:
    scenario = json.loads((GOLDEN_DIR / "scenario.json").read_text(encoding="utf-8"))
    create = await client.post(
        "/projects",
        json=project_create_payload(
            title=scenario["project_title"],
            template="mystery_starter",
            genre_profile=scenario["genre_profile"],
        ),
        headers=headers,
    )
    assert create.status_code == 201
    project_id = create.json()["id"]
    genre_before = await client.get(f"/projects/{project_id}/genre-rule-pack", headers=headers)
    pack_before = genre_before.json()["pack"]

    install = await client.post(
        f"/projects/{project_id}/craft-packs/{MYSTERY_PACK_ID}/install",
        headers=headers,
    )
    assert install.status_code == 200
    activate = await client.post(
        f"/projects/{project_id}/craft-packs/{MYSTERY_PACK_ID}/activate",
        headers=headers,
    )
    assert activate.status_code == 200

    genre_after = await client.get(f"/projects/{project_id}/genre-rule-pack", headers=headers)
    assert genre_after.json()["pack"] == pack_before

    ch5 = await client.post(
        f"/projects/{project_id}/chapters",
        json={"number": scenario["payoff_chapter_number"], "title": "Reveal"},
        headers=headers,
    )
    assert ch5.status_code == 201
    ch1 = await client.get(f"/projects/{project_id}/chapters", headers=headers)
    ch1_id = ch1.json()["items"][0]["id"]
    return project_id, ch1_id, ch5.json()["id"]


@pytest.mark.integration
async def test_craft_pack_catalog(client: AsyncClient, user_a_headers: dict[str, str]) -> None:
    resp = await client.get("/craft-packs", headers=user_a_headers)
    assert resp.status_code == 200
    ids = {item["id"] for item in resp.json()["items"]}
    assert MYSTERY_PACK_ID in ids


@pytest.mark.integration
async def test_install_does_not_overwrite_genre_rule_pack(
    client: AsyncClient, user_a_headers: dict[str, str]
) -> None:
    project_id, _, _ = await _golden_mystery_project(client, user_a_headers)
    bindings = await client.get(f"/projects/{project_id}/craft-packs", headers=user_a_headers)
    body = bindings.json()
    assert body["active_pack_id"] == MYSTERY_PACK_ID


@pytest.mark.integration
async def test_craft_continuity_golden_flags(
    client: AsyncClient, user_a_headers: dict[str, str]
) -> None:
    expected = json.loads((GOLDEN_DIR / "expected_flags.json").read_text(encoding="utf-8"))
    scenario = json.loads((GOLDEN_DIR / "scenario.json").read_text(encoding="utf-8"))
    project_id, ch1_id, payoff_ch_id = await _golden_mystery_project(client, user_a_headers)

    twist_resp = await client.post(
        f"/projects/{project_id}/twists",
        json={
            "title": scenario["twist_title"],
            "secret_truth": "Butler did it",
            "constraints_json": {"min_plants_before_payoff": scenario["min_plants"]},
        },
        headers=user_a_headers,
    )
    twist_id = twist_resp.json()["id"]

    await client.post(
        f"/projects/{project_id}/twists/{twist_id}/payoffs",
        json={"target_chapter_id": payoff_ch_id, "min_plants": scenario["min_plants"]},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{payoff_ch_id}/prose-versions",
        json={"content": scenario["prose_marker"]},
        headers=user_a_headers,
    )

    check = await client.post(
        f"/projects/{project_id}/chapters/{payoff_ch_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check.status_code == 200
    body = check.json()
    codes = {issue["code"] for issue in body["issues"]}
    for code in expected["required_codes"]:
        assert code in codes, f"missing {code} in {codes}"
    assert len(codes.intersection(set(expected["required_codes"]))) >= expected["min_seeded_flags"]


@pytest.mark.integration
async def test_craft_context_pack_no_secret_truth(
    client: AsyncClient, user_a_headers: dict[str, str]
) -> None:
    project_id, _, payoff_ch_id = await _golden_mystery_project(client, user_a_headers)
    chapters = await client.get(f"/projects/{project_id}/chapters", headers=user_a_headers)
    payoff = next(c for c in chapters.json()["items"] if c["id"] == payoff_ch_id)
    resp = await client.post(
        f"/projects/{project_id}/context-packs/craft",
        json={
            "chapter_id": payoff_ch_id,
            "chapter_number": payoff["number"],
            "audience": "writer",
        },
        headers=user_a_headers,
    )
    assert resp.status_code == 200
    text = json.dumps(resp.json())
    assert "secret_truth" not in text


@pytest.mark.integration
async def test_genre_incompatible_install(
    client: AsyncClient, user_a_headers: dict[str, str]
) -> None:
    create = await client.post(
        "/projects",
        json=project_create_payload(genre_profile="xianxia"),
        headers=user_a_headers,
    )
    project_id = create.json()["id"]
    resp = await client.post(
        f"/projects/{project_id}/craft-packs/{MYSTERY_PACK_ID}/install",
        headers=user_a_headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "genre_incompatible"
