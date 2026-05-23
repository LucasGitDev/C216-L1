import time

import asyncpg
from fastapi import APIRouter, Depends

from app.api.deps import get_conn

router = APIRouter()


@router.get(
    "/health",
    summary="Verificar saúde da API",
    operation_id="healthCheck",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get(
    "/health/db",
    summary="Verificar saúde e latência do banco",
    operation_id="healthCheckDb",
)
async def health_check_db(
    conn: asyncpg.Connection = Depends(get_conn),
) -> dict[str, object]:
    start = time.perf_counter()
    result = await conn.fetchval("SELECT 1")
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {
        "status": "ok" if result == 1 else "error",
        "database": "postgres",
        "latency_ms": round(elapsed_ms, 3),
    }
