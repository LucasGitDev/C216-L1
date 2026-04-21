from fastapi.testclient import TestClient


def test_healthcheck_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_process_time_middleware_adds_header(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert "X-Process-Time" in response.headers
