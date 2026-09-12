"""Prose word count helpers."""


def count_words(content: str) -> int:
    """Count words in prose content (whitespace-separated tokens)."""
    stripped = content.strip()
    if not stripped:
        return 0
    return len(stripped.split())
