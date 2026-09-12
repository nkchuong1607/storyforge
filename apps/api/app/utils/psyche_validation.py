"""Psyche card validation and partial merge helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def merge_psyche_card(
    existing: dict[str, Any] | None,
    patch: dict[str, Any],
) -> dict[str, Any]:
    """Deep-merge partial psyche card updates at application layer."""
    base = deepcopy(existing) if existing else {}
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merged = dict(base[key])
            merged.update(value)
            base[key] = merged
        else:
            base[key] = value
    return base


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def _non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def psyche_has_t2_minimum(psyche_card: dict[str, Any] | None) -> bool:
    if not psyche_card:
        return False
    legacy_traits = psyche_card.get("traits")
    legacy_goals = psyche_card.get("goals")
    if _non_empty_list(legacy_traits) or _non_empty_list(legacy_goals):
        return True
    return (
        _non_empty_str(psyche_card.get("drive"))
        or _non_empty_str(psyche_card.get("need"))
        or _non_empty_str(psyche_card.get("wound"))
    )


def psyche_meets_t3_minimum(psyche_card: dict[str, Any] | None) -> bool:
    if not psyche_card:
        return False
    boundaries = psyche_card.get("moral_boundaries")
    has_boundaries = _non_empty_list(boundaries)
    hierarchy = psyche_card.get("value_hierarchy")
    traits = psyche_card.get("traits")
    has_hierarchy = _non_empty_list(hierarchy) or _non_empty_list(traits)
    return has_boundaries and has_hierarchy


def validate_psyche_card_for_tier(
    *,
    tier: int,
    psyche_card: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Return validation detail entries; empty when valid."""
    if tier < 3:
        return []
    details: list[dict[str, Any]] = []
    if not psyche_meets_t3_minimum(psyche_card):
        if not _non_empty_list((psyche_card or {}).get("moral_boundaries")):
            details.append({"field": "psyche_card.moral_boundaries", "required": True})
        hierarchy = (psyche_card or {}).get("value_hierarchy")
        traits = (psyche_card or {}).get("traits")
        if not _non_empty_list(hierarchy) and not _non_empty_list(traits):
            details.append({"field": "psyche_card.value_hierarchy", "required": True})
    return details
