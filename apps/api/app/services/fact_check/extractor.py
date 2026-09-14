"""Deterministic claim extraction from prose."""

from __future__ import annotations

import re
from calendar import month_name

from app.models.enums import FactClaimCategory, FactClaimSourceType, RealityAnchorsMode
from app.providers.fact_check.types import ClaimDraft, ResearchNoteSnapshot

_MONTHS = {name.lower(): idx for idx, name in enumerate(month_name) if name}
_DATE_PATTERNS = [
    re.compile(
        r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+(\d{4})\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(\d{4})-(\d{2})(?:-(\d{2}))?\b"),
]
_ANCHOR_PATTERN = re.compile(r"\[\[anchor\]\](.*?)\[\[/anchor\]\]", re.DOTALL | re.IGNORECASE)
_PLACE_PATTERN = re.compile(r"\b(?:in|at|to|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b")
_ALL_CATEGORIES = {c.value for c in FactClaimCategory}


def normalize_date(text: str) -> str | None:
    text = text.strip()
    for pattern in _DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        groups = match.groups()
        if len(groups) == 3 and groups[0].isdigit():
            day, month_name_raw, year = groups
            month = _MONTHS.get(month_name_raw.lower())
            if month:
                return f"{year}-{month:02d}-{int(day):02d}"
        elif len(groups) == 2 and groups[0].isalpha():
            month_name_raw, year = groups
            month = _MONTHS.get(month_name_raw.lower())
            if month:
                return f"{year}-{month:02d}"
        elif len(groups) >= 2 and groups[0].isdigit():
            year, month = groups[0], groups[1]
            day = groups[2] if len(groups) > 2 and groups[2] else "01"
            return f"{year}-{month}-{day}"
    return None


def _excerpt(prose: str, start: int, end: int, radius: int = 20) -> str:
    left = max(0, start - radius)
    right = min(len(prose), end + radius)
    return prose[left:right]


def _category_enabled(category: str, enabled: list[str]) -> bool:
    if not enabled:
        return True
    return category in enabled


def extract_claims(
    *,
    prose: str,
    reality_mode: str,
    enabled_categories: list[str],
    category_override: list[str] | None = None,
    research_notes: list[ResearchNoteSnapshot] | None = None,
    include_research_notes: bool = True,
) -> list[ClaimDraft]:
    if reality_mode == RealityAnchorsMode.off.value:
        return []

    active_categories = category_override or enabled_categories
    claims: list[ClaimDraft] = []

    if reality_mode == RealityAnchorsMode.soft.value:
        for match in _ANCHOR_PATTERN.finditer(prose):
            anchor_text = match.group(1).strip()
            start = match.start(1)
            end = match.end(1)
            if _category_enabled(FactClaimCategory.date.value, active_categories):
                normalized = normalize_date(anchor_text)
                if normalized:
                    claims.append(
                        ClaimDraft(
                            category=FactClaimCategory.date.value,
                            text=anchor_text,
                            normalized_text=normalized,
                            span_start=start,
                            span_end=end,
                            span_excerpt=_excerpt(prose, start, end),
                            source_type=FactClaimSourceType.anchor_marker.value,
                        )
                    )
                    continue
            if _category_enabled(FactClaimCategory.place.value, active_categories):
                claims.append(
                    ClaimDraft(
                        category=FactClaimCategory.place.value,
                        text=anchor_text,
                        normalized_text=anchor_text.lower(),
                        span_start=start,
                        span_end=end,
                        span_excerpt=_excerpt(prose, start, end),
                        source_type=FactClaimSourceType.anchor_marker.value,
                    )
                )
    else:
        for pattern in _DATE_PATTERNS:
            if not _category_enabled(FactClaimCategory.date.value, active_categories):
                break
            for match in pattern.finditer(prose):
                text = match.group(0)
                claims.append(
                    ClaimDraft(
                        category=FactClaimCategory.date.value,
                        text=text,
                        normalized_text=normalize_date(text),
                        span_start=match.start(),
                        span_end=match.end(),
                        span_excerpt=_excerpt(prose, match.start(), match.end()),
                        source_type=FactClaimSourceType.prose.value,
                    )
                )

        if _category_enabled(FactClaimCategory.place.value, active_categories):
            for match in _PLACE_PATTERN.finditer(prose):
                place = match.group(1)
                if place.lower() in {"the", "a", "an"}:
                    continue
                start = match.start(1)
                end = match.end(1)
                claims.append(
                    ClaimDraft(
                        category=FactClaimCategory.place.value,
                        text=place,
                        normalized_text=place.lower(),
                        span_start=start,
                        span_end=end,
                        span_excerpt=_excerpt(prose, start, end),
                        source_type=FactClaimSourceType.prose.value,
                    )
                )

    if include_research_notes and research_notes:
        for note in research_notes:
            claims.append(
                ClaimDraft(
                    category=FactClaimCategory.historical_event.value,
                    text=note.title,
                    normalized_text=note.title.lower(),
                    span_start=None,
                    span_end=None,
                    span_excerpt=note.body_md[:120],
                    source_type=FactClaimSourceType.research_note.value,
                    source_research_note_id=note.id,
                )
            )

    return _dedupe_claims(claims)


def _dedupe_claims(claims: list[ClaimDraft]) -> list[ClaimDraft]:
    seen: set[tuple[str, str, int | None]] = set()
    unique: list[ClaimDraft] = []
    for claim in claims:
        key = (claim.category, claim.normalized_text or claim.text, claim.span_start)
        if key in seen:
            continue
        seen.add(key)
        unique.append(claim)
    return unique
