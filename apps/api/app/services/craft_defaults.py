"""Default craft pack catalog documents."""

from __future__ import annotations

from typing import Any

MYSTERY_FAIR_PLAY_V1_ID = "mystery.fair_play.v1"


def mystery_fair_play_v1() -> dict[str, Any]:
    """Canonical Mystery fair-play craft pack (schema v1)."""
    return {
        "schema_version": 1,
        "id": MYSTERY_FAIR_PLAY_V1_ID,
        "display_name": "Mystery — Fair Play",
        "genre_tags": ["mystery"],
        "compat": {
            "requires_genre_profiles": ["mystery", "custom"],
            "min_app_phase": 10,
        },
        "structure": {
            "template_id": "mystery_three_act_fair_play",
            "beats": [
                {"key": "hook", "act": 1, "required": True},
                {"key": "crime_or_puzzle", "act": 1, "required": True},
                {"key": "investigation_loop", "act": 2, "required": True},
                {"key": "midpoint_reversal", "act": 2, "required": True},
                {"key": "fair_clue_cluster", "act": 2, "required": True},
                {"key": "false_solution", "act": 2, "required": False},
                {"key": "reveal", "act": 3, "required": True},
                {"key": "payoff_wrap", "act": 3, "required": True},
            ],
        },
        "checklist": [
            {
                "id": "clue_before_reveal",
                "severity_default": "fail",
                "continuity_category": "foreshadow",
                "code": "craft_mystery_clue_after_reveal",
                "description": (
                    "Every reveal claim must map to ≥1 planted clue with earlier chapter_ref"
                ),
            },
            {
                "id": "red_herring_labeled",
                "severity_default": "warn",
                "continuity_category": "craft",
                "code": "craft_mystery_unlabeled_misdirection",
                "description": "Misdirection without TwistPlan misdirection entry",
            },
            {
                "id": "detective_knowledge_ledger",
                "severity_default": "warn",
                "continuity_category": "craft",
                "code": "craft_mystery_reader_spoiler",
                "description": (
                    "Reader-known secret appears in detective POV without knowledge ledger event"
                ),
            },
            {
                "id": "fair_play_min_clues",
                "severity_default": "fail",
                "continuity_category": "foreshadow",
                "code": "craft_mystery_insufficient_plants",
                "description": "Payoff requires ≥2 plants (align with mystery rule-pack threshold)",
            },
        ],
        "prompt_hooks": {
            "context_pack_extra_keys": [
                "craft_checklist_open",
                "active_clues",
                "active_misdirections",
            ],
            "prompt_edit_skills": [
                "mystery_clue_plant",
                "mystery_reveal_align",
                "mystery_red_herring",
            ],
        },
        "golden": {
            "fixture_project_slug": "golden-mystery-fair-play",
            "min_seeded_flags": 3,
            "fakellm_coverage_target": 0.9,
        },
    }


def catalog_seed_packs() -> list[dict[str, Any]]:
    """Packs inserted by migration seed."""
    return [mystery_fair_play_v1()]


def pack_display_name(pack_json: dict[str, Any]) -> str:
    name = pack_json.get("display_name")
    if isinstance(name, str) and name:
        return name
    pack_id = pack_json.get("id")
    return str(pack_id) if pack_id else "Craft Pack"


def is_genre_compatible(pack_json: dict[str, Any], genre_profile: str) -> bool:
    compat = pack_json.get("compat") or {}
    required = compat.get("requires_genre_profiles") or []
    if not isinstance(required, list) or not required:
        return True
    return genre_profile in required
