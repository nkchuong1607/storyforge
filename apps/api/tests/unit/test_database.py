"""Database session dependency tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database import get_db_session


@pytest.mark.unit
async def test_get_db_session_commits_on_success() -> None:
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=session)
    context.__aexit__ = AsyncMock(return_value=None)

    factory = MagicMock(return_value=context)

    original = __import__("app.database", fromlist=["async_session_factory"]).async_session_factory
    try:
        import app.database as db_module

        db_module.async_session_factory = factory
        gen = get_db_session()
        yielded = await gen.__anext__()
        assert yielded is session
        with pytest.raises(StopAsyncIteration):
            await gen.__anext__()
    finally:
        db_module.async_session_factory = original

    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.unit
async def test_get_db_session_rolls_back_on_error() -> None:
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=session)
    context.__aexit__ = AsyncMock(return_value=None)

    factory = MagicMock(return_value=context)

    import app.database as db_module

    original = db_module.async_session_factory
    try:
        db_module.async_session_factory = factory
        gen = get_db_session()
        await gen.__anext__()
        with pytest.raises(RuntimeError):
            await gen.athrow(RuntimeError("boom"))
    finally:
        db_module.async_session_factory = original

    session.rollback.assert_awaited_once()
