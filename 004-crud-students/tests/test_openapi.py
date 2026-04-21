from fastapi.testclient import TestClient


def test_openapi_schema_exposes_tag_metadata(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()

    assert payload["info"]["title"] == "004 CRUD Alunos"
    assert payload["info"]["summary"] == "Boilerplate FastAPI para exercícios REST."
    assert "endpoint de healthcheck" in payload["info"]["description"]
    assert payload["tags"] == [
        {
            "name": "health",
            "description": "Endpoints de verificação básica da API.",
        },
    ]


def test_openapi_exposes_health_endpoint(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    operation = payload["paths"]["/api/v1/health"]["get"]

    assert operation["summary"] == "Verificar saúde da API"
    assert operation["operationId"] == "healthCheck"


def test_openapi_includes_health_path(
    client: TestClient,
) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    assert "/api/v1/health" in payload["paths"]
