"""FakeVerifier deterministic provider tests."""

import uuid

import pytest

from app.providers.fact_check.fake import FakeVerifier
from app.providers.fact_check.types import ClaimDraft, ProviderContext


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fake_verifier_contradiction() -> None:
    claim = ClaimDraft(
        category="date",
        text="9 November 1985",
        normalized_text="1985-11-09",
        span_start=0,
        span_end=16,
        span_excerpt="9 November 1985",
        source_type="prose",
    )
    context = ProviderContext(
        project_id=uuid.uuid4(),
        research_notes=[],
        http_enabled=False,
        force_refresh=False,
        cache_enabled=True,
    )
    result = await FakeVerifier().verify(claim, context)
    assert result.severity == "fail"
    assert result.proposed_correction == "9 November 1989"
    assert result.citations[0].url.startswith("https://fake.storyforge.test/")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fake_verifier_verified_date() -> None:
    claim = ClaimDraft(
        category="date",
        text="March 1945",
        normalized_text="1945-03",
        span_start=0,
        span_end=10,
        span_excerpt="March 1945",
        source_type="prose",
    )
    context = ProviderContext(
        project_id=uuid.uuid4(),
        research_notes=[],
        http_enabled=False,
        force_refresh=False,
        cache_enabled=True,
    )
    result = await FakeVerifier().verify(claim, context)
    assert result.severity == "pass"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fake_verifier_inconclusive_unknown() -> None:
    claim = ClaimDraft(
        category="place",
        text="Atlantis",
        normalized_text="atlantis",
        span_start=0,
        span_end=8,
        span_excerpt="Atlantis",
        source_type="prose",
    )
    context = ProviderContext(
        project_id=uuid.uuid4(),
        research_notes=[],
        http_enabled=False,
        force_refresh=False,
        cache_enabled=True,
    )
    result = await FakeVerifier().verify(claim, context)
    assert result.severity == "warn"
