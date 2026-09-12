"""Unit tests for heuristic character extractor."""

import pytest

from app.utils.character_extractor import extract_mentions_from_text, extract_snippet


@pytest.mark.unit
def test_extract_at_mentions() -> None:
    mentions = extract_mentions_from_text("Gặp @Hắc Y Nhân tại cổng.")
    assert "Hắc Y Nhân" in mentions


@pytest.mark.unit
def test_extract_quoted_names() -> None:
    mentions = extract_mentions_from_text('Hắn gọi "Lý Phong" và đi.')
    assert "Lý Phong" in mentions


@pytest.mark.unit
def test_extract_capitalized_vietnamese_names() -> None:
    text = "Lý Phong tu luyện trên núi Thanh Vân."
    mentions = extract_mentions_from_text(text)
    assert "Lý Phong" in mentions


@pytest.mark.unit
def test_extract_skips_common_tokens() -> None:
    mentions = extract_mentions_from_text("The sun rose over Monday.")
    assert "The" not in mentions
    assert "Monday" not in mentions


@pytest.mark.unit
def test_extract_snippet_with_context() -> None:
    content = "A" * 100 + "Hắc Y Nhân" + "B" * 100
    snippet = extract_snippet(content, "Hắc Y Nhân", radius=20)
    assert "Hắc Y Nhân" in snippet
    assert snippet.startswith("...")


@pytest.mark.unit
def test_extract_deduplicates_mentions() -> None:
    text = 'Lý Phong nói "Lý Phong" và @Lý Phong'
    mentions = extract_mentions_from_text(text)
    assert mentions.count("Lý Phong") == 1
