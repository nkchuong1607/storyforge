"""Integration test fixtures."""

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy import text


@pytest_asyncio.fixture(autouse=True)
async def reset_database(engine) -> AsyncGenerator[None, None]:
    """Truncate tenant tables between integration tests for isolation."""
    tables = (
        "twist_payoffs",
        "twist_plants",
        "twist_plans",
        "settle_idempotency_keys",
        "continuity_overrides",
        "continuity_reports",
        "ledger_events",
        "prose_versions",
        "scene_beats",
        "characters",
        "character_provisional",
        "chapters",
        "bible_entry_staging",
        "bible_versions",
        "project_members",
        "projects",
    )
    async with engine.begin() as conn:
        for table in tables:
            await conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
    yield
