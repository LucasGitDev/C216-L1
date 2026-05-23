from __future__ import annotations

from typing import AsyncIterator

import asyncpg

from app.db.pool import get_pool


async def get_conn() -> AsyncIterator[asyncpg.Connection]:
    pool = get_pool()
    async with pool.acquire() as conn:
        yield conn
