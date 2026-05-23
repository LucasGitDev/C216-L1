from httpx import AsyncClient


async def test_list_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/professores")
    assert response.status_code == 200
    assert response.json() == {"items": []}


async def test_create_and_get(client: AsyncClient) -> None:
    payload = {
        "nome": "Lucas Teles",
        "email": "lucas.teles@inatel.br",
        "sala_de_atendimento": "Sala 101",
    }
    created = await client.post("/api/v1/professores", json=payload)
    assert created.status_code == 201
    body = created.json()
    assert body["id"] >= 1
    assert body["nome"] == payload["nome"]

    fetched = await client.get(f"/api/v1/professores/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["email"] == payload["email"]


async def test_create_email_conflict(client: AsyncClient) -> None:
    payload = {
        "nome": "Prof A",
        "email": "dup@inatel.br",
        "sala_de_atendimento": "S1",
    }
    first = await client.post("/api/v1/professores", json=payload)
    assert first.status_code == 201
    dup = await client.post("/api/v1/professores", json={**payload, "nome": "Prof B"})
    assert dup.status_code == 409
    assert dup.json() == {"detail": "email ja cadastrado"}


async def test_get_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/professores/99999")
    assert response.status_code == 404


async def test_patch_partial(client: AsyncClient) -> None:
    created = await client.post(
        "/api/v1/professores",
        json={"nome": "Foo", "email": "foo@inatel.br", "sala_de_atendimento": "S1"},
    )
    pid = created.json()["id"]
    patched = await client.patch(
        f"/api/v1/professores/{pid}", json={"sala_de_atendimento": "S2"}
    )
    assert patched.status_code == 200
    assert patched.json()["sala_de_atendimento"] == "S2"
    assert patched.json()["nome"] == "Foo"


async def test_delete(client: AsyncClient) -> None:
    created = await client.post(
        "/api/v1/professores",
        json={"nome": "Del", "email": "del@inatel.br", "sala_de_atendimento": "S1"},
    )
    pid = created.json()["id"]
    deleted = await client.delete(f"/api/v1/professores/{pid}")
    assert deleted.status_code == 204
    missing = await client.get(f"/api/v1/professores/{pid}")
    assert missing.status_code == 404


async def test_reset(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/professores",
        json={"nome": "A", "email": "a@inatel.br", "sala_de_atendimento": "S1"},
    )
    response = await client.delete("/api/v1/professores")
    assert response.status_code == 204
    after = await client.get("/api/v1/professores")
    assert after.json() == {"items": []}
