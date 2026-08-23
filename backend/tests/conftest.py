import os

# Settings() is constructed at import time (app.db.session, app.main). Make
# sure required env vars exist before any app module is imported, so the
# test suite never depends on a real .env file being present.
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest_asyncio  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # noqa: E402

from app.core.config import get_settings  # noqa: E402


@pytest_asyncio.fixture
async def db_session():
    """A real session against the actual Postgres database, wrapped in a
    transaction that's rolled back at teardown. Used only by tests that
    need genuine SQL behavior (ordering, JSONB, constraints) — most of
    this suite uses fakes instead and never touches a database at all.
    Requires the `db` service to be reachable (skip with --no-deps).

    Deliberately does NOT reuse app.db.session.engine: that's a
    module-level singleton, and pytest-asyncio gives each test function
    its own event loop by default, so a pooled asyncpg connection
    created in one test's loop breaks on the next test's different loop.
    A fresh, disposable engine per test sidesteps that entirely.
    """
    settings = get_settings()
    test_engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    try:
        async with test_engine.connect() as connection:
            transaction = await connection.begin()
            session = AsyncSession(bind=connection, expire_on_commit=False)
            try:
                yield session
            finally:
                await session.close()
                await transaction.rollback()
    finally:
        await test_engine.dispose()
