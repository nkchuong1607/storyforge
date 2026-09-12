"""Character alias and name normalization helpers."""

from __future__ import annotations


def normalize_name(value: str) -> str:
    return value.strip().casefold()


def alias_present(aliases: list, mention: str) -> bool:
    normalized = normalize_name(mention)
    return any(normalize_name(alias) == normalized for alias in aliases)


def display_name_matches(display_name: str, mention: str) -> bool:
    return normalize_name(display_name) == normalize_name(mention)


def append_alias_if_distinct(aliases: list, mention: str, display_name: str) -> list:
    """Return updated aliases list; append mention when distinct from display_name."""
    updated = list(aliases)
    if display_name_matches(display_name, mention):
        return updated
    if alias_present(updated, mention):
        return updated
    updated.append(mention.strip())
    return updated
