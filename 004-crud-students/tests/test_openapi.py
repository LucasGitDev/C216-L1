from httpx import AsyncClient


async def test_openapi_schema_exposes_tag_metadata(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()

    assert payload["info"]["title"] == "004 CRUD Alunos"
    assert payload["info"]["summary"] == "CRUD de alunos via REST com persistência em PostgreSQL."
    assert "PostgreSQL" in payload["info"]["description"]
    assert payload["tags"] == [
        {
            "name": "health",
            "description": "Endpoints de verificação básica da API.",
        },
        {
            "name": "alunos",
            "description": "Operações para listar, criar, consultar, atualizar, remover e resetar alunos persistidos no PostgreSQL.",
        },
    ]


async def test_openapi_student_endpoint_documents_requests_and_errors(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    operation = payload["paths"]["/api/v1/alunos"]["post"]

    assert operation["summary"] == "Cadastrar aluno"
    assert "matrícula automática" in operation["description"]
    assert operation["operationId"] == "createStudent"
    assert operation["responses"]["409"]["description"] == "Conflito de unicidade para `email`."
    assert "email_conflict" in operation["responses"]["409"]["content"]["application/json"]["examples"]
    assert operation["requestBody"]["required"] is True


async def test_openapi_components_include_examples_for_student_schemas(
    client: AsyncClient,
) -> None:
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    schemas = payload["components"]["schemas"]

    assert schemas["StudentCreateRequest"]["example"]["course"] == "GES"
    assert schemas["StudentCreateRequest"]["example"]["email"] == "ana.clara@ges.inatel.br"
    assert schemas["StudentResponse"]["example"]["id"] == "GES1"
    assert schemas["StudentResponse"]["example"]["matricula"] == 1
    assert schemas["ErrorResponse"]["example"] == {"detail": "aluno nao encontrado"}
