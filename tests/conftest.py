"""Shared pytest fixtures for all tests."""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from src.config import settings
from src.identity.infrastructure.services import Argon2PasswordHasher
from src.identity.interface.api.dependencies import get_session
from src.main import app
from src.shared.infrastructure import Base

# Test database URL (use separate test database)
# Use project-specific database name for multi-agent isolation
# Use rsplit to replace only the database name at the end, not the username
_base_url, _db_name = settings.database_url.rsplit("/", 1)
_test_db_name = os.getenv("KOULU_TEST_DB_NAME", "koulu_test")

# pytest-xdist: each worker gets its own database to avoid DDL conflicts
_xdist_worker = os.getenv("PYTEST_XDIST_WORKER", "")
if _xdist_worker:
    _test_db_name = f"{_test_db_name}_{_xdist_worker}"

TEST_DATABASE_URL = f"{_base_url}/{_test_db_name}"

# Process-level flag: DDL runs once per worker process, not per test.
_tables_created = False


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine.

    Tables are created once per process (guarded by _tables_created flag)
    instead of per-test. Tables are never dropped — test DBs are ephemeral.
    """
    global _tables_created  # noqa: PLW0603
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    if not _tables_created:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _tables_created = True

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session with savepoint rollback for isolation.

    Uses connection-level transaction control: the connection holds an outer
    transaction that is never committed. The session operates inside savepoints
    (begin_nested). When test code calls session.commit(), it only commits the
    savepoint. An event listener auto-restarts a new savepoint after each commit
    so subsequent operations continue inside savepoints. At teardown, the outer
    connection transaction is rolled back, wiping all test data.
    """
    async with db_engine.connect() as conn:
        trans = await conn.begin()  # outer transaction — never committed
        session = AsyncSession(bind=conn, expire_on_commit=False)
        await conn.begin_nested()  # initial SAVEPOINT

        # After each savepoint ends (commit or rollback), start a new one
        # so subsequent session operations stay inside savepoints.
        @event.listens_for(session.sync_session, "after_transaction_end")
        def _restart_savepoint(_sync_session: Any, _transaction: Any) -> None:
            if conn.closed:
                return
            if not conn.in_nested_transaction() and conn.sync_connection:
                conn.sync_connection.begin_nested()

        yield session

        await session.close()
        await trans.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with overridden database session."""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def password_hasher() -> Argon2PasswordHasher:
    """Get password hasher."""
    return Argon2PasswordHasher()


@pytest.fixture
def context() -> dict[str, Any]:
    """Shared test context for storing state between steps."""
    return {}
