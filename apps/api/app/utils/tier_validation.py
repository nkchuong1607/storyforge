"""Tier promotion validation for progressive characters."""

from __future__ import annotations

from typing import Any

from app.utils.psyche_validation import psyche_has_t2_minimum, psyche_meets_t3_minimum


class TierRequirementsError(Exception):
    """Raised when tier promotion requirements are not met."""

    def __init__(self, message: str, details: list[dict[str, Any]]) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


def _has_voice_or_relation(metadata: dict[str, Any]) -> bool:
    if metadata.get("voice_hint"):
        return True
    relations = metadata.get("relations")
    return isinstance(relations, list) and len(relations) > 0


def _has_arc_or_secret(metadata: dict[str, Any]) -> bool:
    return bool(metadata.get("arc_note") or metadata.get("secret_stub"))


def validate_tier_promotion(
    *,
    current_tier: int,
    role_one_liner: str | None,
    psyche_card: dict[str, Any] | None,
    metadata: dict[str, Any],
    confirm_t3: bool = False,
) -> int:
    """Validate and return the next tier. Raises TierRequirementsError on failure."""
    if current_tier >= 3:
        raise TierRequirementsError("Character is already at maximum tier", [])

    next_tier = current_tier + 1

    if next_tier == 1:
        if not _has_voice_or_relation(metadata):
            raise TierRequirementsError(
                "T1 requires voice_hint or relations in metadata",
                [{"field": "metadata.voice_hint", "required": True}],
            )
        return next_tier

    if next_tier == 2:
        if not psyche_has_t2_minimum(psyche_card):
            raise TierRequirementsError(
                "T2 requires psyche_card with at least one trait, goal, drive, or need",
                [{"field": "psyche_card.drive", "required": True}],
            )
        return next_tier

    if next_tier == 3:
        if not confirm_t3:
            raise TierRequirementsError(
                "T3 promotion requires confirm_t3=true",
                [{"field": "confirm_t3", "required": True}],
            )
        details: list[dict[str, Any]] = []
        if not psyche_meets_t3_minimum(psyche_card):
            details.append({"field": "psyche_card.moral_boundaries", "required": True})
            details.append({"field": "psyche_card.value_hierarchy", "required": True})
        if not _has_arc_or_secret(metadata):
            details.append({"field": "metadata.arc_note", "required": True})
        if details:
            raise TierRequirementsError(
                "T3 requires psyche_card traits and moral_boundaries plus arc or secret",
                details,
            )
        return next_tier

    return next_tier


def compute_tier_suggest(appearance_count: int, metadata: dict[str, Any]) -> bool:
    if metadata.get("tier_suggest") is True:
        return True
    return (appearance_count or 0) >= 3
