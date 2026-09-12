"""Heuristic character mention extractor v1."""

from __future__ import annotations

import re

_CAPITAL = "A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬĐÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ"
_WORD_TAIL = r"[\wÀ-ỹ]"
_BOUNDARY_BEFORE = r"(?<![\wÀ-ỹ])"
_BOUNDARY_AFTER = r"(?![\wÀ-ỹ])"
_NAME_TOKEN = rf"[{_CAPITAL}]{_WORD_TAIL}*"
_CAPITALIZED_NAME = re.compile(
    rf"{_BOUNDARY_BEFORE}({_NAME_TOKEN}(?:\s+{_NAME_TOKEN})+){_BOUNDARY_AFTER}"
)
_AT_MENTION = re.compile(rf"@({_NAME_TOKEN}(?:\s+{_NAME_TOKEN})*)")
_QUOTED_NAME = re.compile(r'"([^"\n]{1,80})"')

_SKIP_TOKENS = frozenset(
    {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "he",
        "she",
        "they",
        "it",
        "i",
        "you",
        "we",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    }
)


def _is_valid_mention(text: str) -> bool:
    cleaned = text.strip()
    if len(cleaned) < 2:
        return False
    if cleaned.casefold() in _SKIP_TOKENS:
        return False
    if cleaned.isdigit():
        return False
    return True


def _drop_substring_mentions(mentions: list[str]) -> list[str]:
    kept: list[str] = []
    for candidate in mentions:
        normalized = candidate.casefold()
        if any(
            normalized != other.casefold() and normalized in other.casefold() for other in mentions
        ):
            continue
        kept.append(candidate)
    return kept


def extract_mentions_from_text(text: str) -> list[str]:
    """Extract candidate character mentions from prose text."""
    mentions: list[str] = []
    seen: set[str] = set()

    def add(raw: str) -> None:
        candidate = raw.strip()
        if not _is_valid_mention(candidate):
            return
        key = candidate.casefold()
        if key in seen:
            return
        seen.add(key)
        mentions.append(candidate)

    for match in _AT_MENTION.finditer(text):
        add(match.group(1))
    for match in _QUOTED_NAME.finditer(text):
        add(match.group(1))
    for match in _CAPITALIZED_NAME.finditer(text):
        add(match.group(1))

    return _drop_substring_mentions(mentions)


def extract_snippet(content: str, mention: str, *, radius: int = 80) -> str:
    """Return ±radius char context around first mention occurrence."""
    lower_content = content.casefold()
    lower_mention = mention.casefold()
    idx = lower_content.find(lower_mention)
    if idx < 0:
        return ""
    start = max(0, idx - radius)
    end = min(len(content), idx + len(mention) + radius)
    snippet = content[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    return snippet
