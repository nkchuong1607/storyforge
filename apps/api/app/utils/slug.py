"""Slug generation utilities."""

import re
import unicodedata


def slugify_title(title: str) -> str:
    """Convert a project title to a URL-safe slug."""
    normalized = unicodedata.normalize("NFKD", title.strip())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "project"


def next_slug_candidate(base_slug: str, attempt: int) -> str:
    """Return slug with numeric suffix for conflict resolution."""
    if attempt <= 1:
        return base_slug
    return f"{base_slug}-{attempt}"
