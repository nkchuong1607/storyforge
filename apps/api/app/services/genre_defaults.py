"""Default genre rule packs by profile."""

from __future__ import annotations

from typing import Any

from app.models.enums import GenreProfile


def default_genre_rule_pack(profile: GenreProfile | None) -> dict[str, Any]:
    """Return canonical default pack for a genre profile."""
    resolved = profile or GenreProfile.custom
    base: dict[str, Any] = {
        "schema_version": 1,
        "base_profile": resolved.value,
        "modules": {
            "power_system": {"enabled": False},
            "foreshadow": {"enabled": True},
            "psychology": {"enabled": True},
            "timeline": {"enabled": True},
        },
        "strictness": {
            "foreshadow": "relaxed",
            "power": "strict",
            "psychology": "standard",
        },
        "promises": [],
        "forbidden": [],
        "expected_payoffs": [],
        "thresholds": {
            "foreshadow_min_plants_default": 1,
            "foreshadow_payoff_without_plants": "warn",
            "power_max_rank_jump_per_chapter": 1,
            "power_combat_upset": "warn",
        },
        "tone": {"primary": "vi", "violence_ceiling": "moderate", "romance_subplot": "optional"},
    }

    if resolved == GenreProfile.xianxia:
        base["display_name"] = "Kiếm hiệp tu chân"
        base["modules"]["power_system"]["enabled"] = True
        base["strictness"]["power"] = "strict"
        base["strictness"]["foreshadow"] = "relaxed"
        base["promises"] = ["Cảnh giới leo thang có căn cứ"]
        base["forbidden"] = ["Nhảy cảnh giới không breakthrough"]
        base["thresholds"]["power_combat_upset"] = "fail"
    elif resolved == GenreProfile.mystery:
        base["display_name"] = "Trinh thám"
        base["strictness"]["foreshadow"] = "strict"
        base["thresholds"]["foreshadow_min_plants_default"] = 2
        base["thresholds"]["foreshadow_payoff_without_plants"] = "fail"
    elif resolved == GenreProfile.literary:
        base["display_name"] = "Văn học"
        base["strictness"]["foreshadow"] = "relaxed"
    elif resolved == GenreProfile.romance:
        base["display_name"] = "Lãng mạn"
        base["strictness"]["psychology"] = "standard"
        base["tone"]["romance_subplot"] = "primary"
    else:
        base["display_name"] = "Tùy chỉnh"
        base["base_profile"] = "custom"

    return base


def deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    """Deep merge patch into base (mutates copy of base)."""
    result = dict(base)
    for key, value in patch.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def merged_genre_pack(stored: dict[str, Any], profile: GenreProfile | None) -> dict[str, Any]:
    """Merge stored overrides onto profile defaults."""
    defaults = default_genre_rule_pack(profile)
    if not stored:
        return defaults
    return deep_merge(defaults, stored)


def validate_genre_pack(pack: dict[str, Any]) -> None:
    """Validate minimal pack shape."""
    if "schema_version" in pack and not isinstance(pack["schema_version"], int):
        raise ValueError("schema_version must be integer")
