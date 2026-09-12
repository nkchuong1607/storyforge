"""Shared pytest fixtures."""

import os
import uuid
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.community.postgres import PostgresContainer

from alembic import command
from app.config import get_settings
from app.database import get_db_session
from app.main import app

USER_A_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
USER_B_ID = uuid.UUID("22222222-2222-4222-8222-222222222222")


def _to_async_url(url: str) -> str:
    if "+asyncpg" in url:
        return url
    if "+psycopg2" in url:
        return url.replace("+psycopg2", "+asyncpg")
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _run_migrations(database_url: str) -> None:
    import pathlib

    os.environ["DATABASE_URL"] = database_url
    get_settings.cache_clear()

    api_root = pathlib.Path(__file__).resolve().parents[1]
    alembic_cfg = Config(str(api_root / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    env_url = os.environ.get("DATABASE_URL")
    if env_url:
        async_url = _to_async_url(env_url)
        _run_migrations(async_url)
        yield async_url
        return

    try:
        with PostgresContainer("postgres:16-alpine") as postgres:
            async_url = _to_async_url(postgres.get_connection_url())
            _run_migrations(async_url)
            yield async_url
    except Exception:
        fallback = "postgresql+asyncpg://storyforge:storyforge@localhost:5432/storyforge"
        _run_migrations(fallback)
        yield fallback


@pytest_asyncio.fixture
async def engine(postgres_url: str):
    test_engine = create_async_engine(postgres_url, echo=False)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as db_session:
        yield db_session
        await db_session.rollback()


@pytest_asyncio.fixture
async def client(engine, postgres_url: str) -> AsyncGenerator[AsyncClient, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as db_session:
            try:
                yield db_session
                await db_session.commit()
            except Exception:
                await db_session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_get_db
    get_settings.cache_clear()
    os.environ["DATABASE_URL"] = postgres_url

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def user_a_headers() -> dict[str, str]:
    return {"X-User-Id": str(USER_A_ID)}


@pytest.fixture
def user_b_headers() -> dict[str, str]:
    return {"X-User-Id": str(USER_B_ID)}
