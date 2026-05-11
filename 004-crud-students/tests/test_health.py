from httpx import AsyncClient


async def test_healthcheck_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_process_time_middleware_adds_header(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert "X-Process-Time" in response.headers


async def test_database_ping_returns_latency(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/db")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"] == "postgres"
    assert isinstance(payload["latency_ms"], (int, float))
    assert payload["latency_ms"] >= 0
    assert payload["latency_ms"] < 1000, f"DB ping muito lento: {payload['latency_ms']}ms"
