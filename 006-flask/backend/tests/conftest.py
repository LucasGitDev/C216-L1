from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.db import pool as db_pool
from app.main import create_application

INIT_SQL_PATH = Path(__file__).resolve().parent.parent / "scripts" / "init.sql"


def _admin_dsn(dsn: str, *, admin_db: str = "postgres") -> str:
    parsed = urlparse(dsn)
    return urlunparse(parsed._replace(path=f"/{admin_db}"))


def _database_name(dsn: str) -> str:
    return urlparse(dsn).path.lstrip("/")


async def _ensure_database(dsn: str) -> None:
    name = _database_name(dsn)
    admin = await asyncpg.connect(dsn=_admin_dsn(dsn))
    try:
        exists = await admin.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", name
        )
        if not exists:
            await admin.execute(f'CREATE DATABASE "{name}"')
    finally:
        await admin.close()


async def _apply_schema(dsn: str) -> None:
    sql = INIT_SQL_PATH.read_text()
    conn = await asyncpg.connect(dsn=dsn)
    try:
        await conn.execute(sql)
    finally:
        await conn.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def _db_ready() -> None:
    os.environ.setdefault("APP_DEBUG", "false")
    settings = get_settings()
    test_dsn = settings.database_url_test
    await _ensure_database(test_dsn)
    await _apply_schema(test_dsn)


@pytest_asyncio.fixture(loop_scope="session")
async def db_pool_fixture(_db_ready: None) -> asyncpg.Pool:
    settings = get_settings()
    pool = await asyncpg.create_pool(
        dsn=settings.database_url_test, min_size=1, max_size=4
    )
    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE professores RESTART IDENTITY")
    db_pool.set_pool(pool)
    try:
        yield pool
    finally:
        db_pool.set_pool(None)
        await pool.close()


@pytest_asyncio.fixture(loop_scope="session", autouse=True)
async def _truncate(db_pool_fixture: asyncpg.Pool) -> None:
    async with db_pool_fixture.acquire() as conn:
        await conn.execute("TRUNCATE professores RESTART IDENTITY")


@pytest_asyncio.fixture(loop_scope="session")
async def client(db_pool_fixture: asyncpg.Pool) -> AsyncClient:
    application = create_application(use_lifespan=False)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client
