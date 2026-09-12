"""Word count utility tests."""

import pytest

from app.utils.word_count import count_words


@pytest.mark.unit
def test_count_words_basic() -> None:
    assert count_words("hello world") == 2


@pytest.mark.unit
def test_count_words_empty() -> None:
    assert count_words("") == 0
    assert count_words("   ") == 0
