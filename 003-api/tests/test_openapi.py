from fastapi.testclient import TestClient


def test_openapi_schema_exposes_tag_metadata(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()

    assert payload["info"]["title"] == "003 API"
    assert payload["info"]["summary"] == "Controle de micro-ondas em memória via REST."
    assert "múltiplos micro-ondas em memória" in payload["info"]["description"]
    assert payload["tags"] == [
        {
            "name": "health",
            "description": "Endpoints de verificação básica da API.",
        },
        {
            "name": "microwaves",
            "description": "Operações para listar, criar e controlar micro-ondas em memória.",
        },
    ]


def test_openapi_start_endpoint_documents_requests_and_errors(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    operation = payload["paths"]["/api/v1/microwaves/{microwave_id}/start"]["post"]

    assert operation["summary"] == "Iniciar aquecimento"
    assert "conteúdo não vazio" in operation["description"]
    assert operation["operationId"] == "startMicrowave"
    assert operation["responses"]["404"]["description"] == "Micro-ondas não encontrado."
    assert (
        operation["responses"]["409"]["content"]["application/json"]["example"]["detail"]
        == "microwave is already running"
    )
    assert "content_empty" in operation["responses"]["422"]["content"]["application/json"]["examples"]
    assert operation["requestBody"]["required"] is True


def test_openapi_components_include_examples_for_microwave_schemas(
    client: TestClient,
) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    schemas = payload["components"]["schemas"]

    assert schemas["MicrowaveStartRequest"]["example"] == {
        "duration_seconds": 30,
        "power": 7,
        "content": "pizza",
    }
    assert schemas["MicrowaveStateResponse"]["example"]["status"] == "running"
    assert schemas["ErrorResponse"]["example"] == {"detail": "microwave not found"}
