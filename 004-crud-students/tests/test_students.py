from httpx import AsyncClient


async def create_student(
    client: AsyncClient,
    *,
    name: str,
    email: str,
    course: str,
    active: bool = True,
) -> dict[str, object]:
    response = await client.post(
        "/api/v1/alunos",
        json={
            "name": name,
            "email": email,
            "course": course,
            "active": active,
        },
    )

    assert response.status_code == 201, response.text
    return response.json()


SEED_FIXTURES = [
    ("GES", "Ana Clara Souza", "ana.clara@ges.inatel.br"),
    ("GES", "Bruno Lima", "bruno.lima@ges.inatel.br"),
    ("GES", "Carla Mendes", "carla.mendes@ges.inatel.br"),
    ("GEC", "Daniel Rocha", "daniel.rocha@gec.inatel.br"),
    ("GEC", "Elaine Costa", "elaine.costa@gec.inatel.br"),
    ("GEC", "Felipe Nunes", "felipe.nunes@gec.inatel.br"),
    ("GEB", "Gabriela Antunes", "gabriela.antunes@geb.inatel.br"),
    ("GEB", "Heitor Borges", "heitor.borges@geb.inatel.br"),
    ("GEB", "Isabela Castro", "isabela.castro@geb.inatel.br"),
    ("GEP", "Joao Pedro", "joao.pedro@gep.inatel.br"),
    ("GEP", "Karina Lopes", "karina.lopes@gep.inatel.br"),
    ("GEP", "Lucas Moreira", "lucas.moreira@gep.inatel.br"),
]


async def seed_three_students_per_course(client: AsyncClient) -> list[dict[str, object]]:
    return [
        await create_student(client, name=name, email=email, course=course)
        for course, name, email in SEED_FIXTURES
    ]


async def test_create_students_generates_sequential_ids_per_course(client: AsyncClient) -> None:
    students = await seed_three_students_per_course(client)

    by_course: dict[str, list[dict[str, object]]] = {"GES": [], "GEC": [], "GEB": [], "GEP": []}
    for student in students:
        by_course[student["course"]].append(student)

    for course, course_students in by_course.items():
        assert len(course_students) == 3, f"esperado 3 alunos em {course}"
        assert [s["id"] for s in course_students] == [f"{course}1", f"{course}2", f"{course}3"]
        assert [s["matricula"] for s in course_students] == [1, 2, 3]


async def test_list_students_returns_all_seeded_students(client: AsyncClient) -> None:
    await seed_three_students_per_course(client)

    response = await client.get("/api/v1/alunos")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 12
    assert [student["id"] for student in payload["items"]] == [
        "GES1", "GES2", "GES3",
        "GEC1", "GEC2", "GEC3",
        "GEB1", "GEB2", "GEB3",
        "GEP1", "GEP2", "GEP3",
    ]


async def test_get_student_returns_specific_student_by_id(client: AsyncClient) -> None:
    await seed_three_students_per_course(client)

    response = await client.get("/api/v1/alunos/GEC2")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "GEC2"
    assert payload["name"] == "Elaine Costa"
    assert payload["course"] == "GEC"
    assert payload["matricula"] == 2


async def test_patch_student_updates_partial_data(client: AsyncClient) -> None:
    await seed_three_students_per_course(client)

    response = await client.patch(
        "/api/v1/alunos/GES2",
        json={
            "name": "Bruno Lima Atualizado",
            "active": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "GES2"
    assert payload["name"] == "Bruno Lima Atualizado"
    assert payload["active"] is False
    assert payload["email"] == "bruno.lima@ges.inatel.br"
    assert payload["course"] == "GES"
    assert payload["matricula"] == 2


async def test_patch_student_changes_course_and_generates_new_id(client: AsyncClient) -> None:
    await seed_three_students_per_course(client)

    response = await client.patch(
        "/api/v1/alunos/GES2",
        json={
            "course": "GEC",
            "email": "bruno.lima@gec.inatel.br",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "GEC4"
    assert payload["course"] == "GEC"
    assert payload["matricula"] == 4

    old_response = await client.get("/api/v1/alunos/GES2")
    assert old_response.status_code == 404


async def test_patch_student_rejects_course_change_without_matching_email(
    client: AsyncClient,
) -> None:
    await seed_three_students_per_course(client)

    response = await client.patch(
        "/api/v1/alunos/GES2",
        json={
            "course": "GEC",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "dominio do email deve corresponder ao curso informado"


async def test_delete_student_does_not_reuse_id(client: AsyncClient) -> None:
    await seed_three_students_per_course(client)

    delete_response = await client.delete("/api/v1/alunos/GES2")
    assert delete_response.status_code == 204

    new_student = await create_student(
        client,
        name="Gabriel Teixeira",
        email="gabriel.teixeira@ges.inatel.br",
        course="GES",
    )

    assert new_student["id"] == "GES4"
    assert new_student["matricula"] == 4


async def test_delete_all_students_resets_list_without_reusing_sequence(
    client: AsyncClient,
) -> None:
    await seed_three_students_per_course(client)

    reset_response = await client.delete("/api/v1/alunos")
    assert reset_response.status_code == 204

    list_response = await client.get("/api/v1/alunos")
    assert list_response.status_code == 200
    assert list_response.json() == {"items": []}

    ges_student = await create_student(
        client,
        name="Helena Martins",
        email="helena.martins@ges.inatel.br",
        course="GES",
    )
    gec_student = await create_student(
        client,
        name="Igor Campos",
        email="igor.campos@gec.inatel.br",
        course="GEC",
    )

    assert ges_student["id"] == "GES4"
    assert gec_student["id"] == "GEC4"


async def test_create_student_rejects_duplicate_email(client: AsyncClient) -> None:
    await create_student(
        client,
        name="Ana Clara Souza",
        email="ana.clara@ges.inatel.br",
        course="GES",
    )

    response = await client.post(
        "/api/v1/alunos",
        json={
            "name": "Outro Nome",
            "email": "ana.clara@ges.inatel.br",
            "course": "GES",
            "active": True,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "email ja cadastrado"


async def test_create_student_accepts_geb_and_gep_emails(client: AsyncClient) -> None:
    geb_student = await create_student(
        client,
        name="Julia Prado",
        email="julia.prado@geb.inatel.br",
        course="GEB",
    )
    gep_student = await create_student(
        client,
        name="Kaique Moura",
        email="kaique.moura@gep.inatel.br",
        course="GEP",
    )

    assert geb_student["id"] == "GEB1"
    assert geb_student["email"] == "julia.prado@geb.inatel.br"
    assert gep_student["id"] == "GEP1"
    assert gep_student["email"] == "kaique.moura@gep.inatel.br"


async def test_create_student_rejects_non_inatel_email_format(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/alunos",
        json={
            "name": "Nome Invalido",
            "email": "nome.sobrenome@example.com",
            "course": "GES",
            "active": True,
        },
    )

    assert response.status_code == 422
    assert "aluno.sobrenome@curso.inatel.br" in str(response.json()["detail"])


async def test_create_student_rejects_email_with_course_different_from_payload(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/alunos",
        json={
            "name": "Marina Castro",
            "email": "marina.castro@gec.inatel.br",
            "course": "GES",
            "active": True,
        },
    )

    assert response.status_code == 422
    assert "course field" in str(response.json()["detail"])


async def test_operations_fail_for_missing_student_id(client: AsyncClient) -> None:
    response = await client.get("/api/v1/alunos/GES999")
    patch_response = await client.patch(
        "/api/v1/alunos/GES999", json={"name": "Nao Existe"}
    )
    delete_response = await client.delete("/api/v1/alunos/GES999")

    assert response.status_code == 404
    assert patch_response.status_code == 404
    assert delete_response.status_code == 404
    assert response.json()["detail"] == "aluno nao encontrado"


async def test_persistence_survives_new_connection(client: AsyncClient, db_pool_fixture) -> None:
    """Insere via API, lê via conexão asyncpg fresh — prova que dado foi persistido no PostgreSQL."""

    await create_student(
        client,
        name="Persistencia Verificada",
        email="persistencia.verificada@ges.inatel.br",
        course="GES",
    )

    async with db_pool_fixture.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, name, course, matricula FROM students WHERE email = $1",
            "persistencia.verificada@ges.inatel.br",
        )

    assert row is not None
    assert row["id"] == "GES1"
    assert row["course"] == "GES"
    assert row["matricula"] == 1
