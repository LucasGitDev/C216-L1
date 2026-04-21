from fastapi.testclient import TestClient


def create_student(
    client: TestClient,
    *,
    name: str,
    email: str,
    course: str,
    active: bool = True,
) -> dict[str, object]:
    response = client.post(
        "/api/v1/alunos",
        json={
            "name": name,
            "email": email,
            "course": course,
            "active": active,
        },
    )

    assert response.status_code == 201
    return response.json()


def seed_three_students_per_course(client: TestClient) -> list[dict[str, object]]:
    students = [
        create_student(
            client,
            name="Ana Clara Souza",
            email="ana.clara@ges.inatel.br",
            course="GES",
        ),
        create_student(
            client,
            name="Bruno Lima",
            email="bruno.lima@ges.inatel.br",
            course="GES",
        ),
        create_student(
            client,
            name="Carla Mendes",
            email="carla.mendes@ges.inatel.br",
            course="GES",
        ),
        create_student(
            client,
            name="Daniel Rocha",
            email="daniel.rocha@gec.inatel.br",
            course="GEC",
        ),
        create_student(
            client,
            name="Elaine Costa",
            email="elaine.costa@gec.inatel.br",
            course="GEC",
        ),
        create_student(
            client,
            name="Felipe Nunes",
            email="felipe.nunes@gec.inatel.br",
            course="GEC",
        ),
    ]
    return students


def test_create_students_generates_sequential_ids_per_course(client: TestClient) -> None:
    students = seed_three_students_per_course(client)

    assert [student["id"] for student in students[:3]] == ["GES1", "GES2", "GES3"]
    assert [student["id"] for student in students[3:]] == ["GEC1", "GEC2", "GEC3"]
    assert [student["matricula"] for student in students[:3]] == [1, 2, 3]
    assert [student["matricula"] for student in students[3:]] == [1, 2, 3]


def test_list_students_returns_all_seeded_students(client: TestClient) -> None:
    seed_three_students_per_course(client)

    response = client.get("/api/v1/alunos")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 6
    assert [student["id"] for student in payload["items"]] == [
        "GES1",
        "GES2",
        "GES3",
        "GEC1",
        "GEC2",
        "GEC3",
    ]


def test_get_student_returns_specific_student_by_id(client: TestClient) -> None:
    seed_three_students_per_course(client)

    response = client.get("/api/v1/alunos/GEC2")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "GEC2"
    assert payload["name"] == "Elaine Costa"
    assert payload["course"] == "GEC"
    assert payload["matricula"] == 2


def test_patch_student_updates_partial_data(client: TestClient) -> None:
    seed_three_students_per_course(client)

    response = client.patch(
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


def test_patch_student_changes_course_and_generates_new_id(client: TestClient) -> None:
    seed_three_students_per_course(client)

    response = client.patch(
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

    old_response = client.get("/api/v1/alunos/GES2")
    assert old_response.status_code == 404


def test_patch_student_rejects_course_change_without_matching_email(client: TestClient) -> None:
    seed_three_students_per_course(client)

    response = client.patch(
        "/api/v1/alunos/GES2",
        json={
            "course": "GEC",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "dominio do email deve corresponder ao curso informado"


def test_delete_student_does_not_reuse_id(client: TestClient) -> None:
    seed_three_students_per_course(client)

    delete_response = client.delete("/api/v1/alunos/GES2")
    assert delete_response.status_code == 204

    new_student = create_student(
        client,
        name="Gabriel Teixeira",
        email="gabriel.teixeira@ges.inatel.br",
        course="GES",
    )

    assert new_student["id"] == "GES4"
    assert new_student["matricula"] == 4


def test_delete_all_students_resets_list_without_reusing_sequence(client: TestClient) -> None:
    seed_three_students_per_course(client)

    reset_response = client.delete("/api/v1/alunos")
    assert reset_response.status_code == 204

    list_response = client.get("/api/v1/alunos")
    assert list_response.status_code == 200
    assert list_response.json() == {"items": []}

    ges_student = create_student(
        client,
        name="Helena Martins",
        email="helena.martins@ges.inatel.br",
        course="GES",
    )
    gec_student = create_student(
        client,
        name="Igor Campos",
        email="igor.campos@gec.inatel.br",
        course="GEC",
    )

    assert ges_student["id"] == "GES4"
    assert gec_student["id"] == "GEC4"


def test_create_student_rejects_duplicate_email(client: TestClient) -> None:
    create_student(
        client,
        name="Ana Clara Souza",
        email="ana.clara@ges.inatel.br",
        course="GES",
    )

    response = client.post(
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


def test_create_student_accepts_geb_and_gep_emails(client: TestClient) -> None:
    geb_student = create_student(
        client,
        name="Julia Prado",
        email="julia.prado@geb.inatel.br",
        course="GEB",
    )
    gep_student = create_student(
        client,
        name="Kaique Moura",
        email="kaique.moura@gep.inatel.br",
        course="GEP",
    )

    assert geb_student["id"] == "GEB1"
    assert geb_student["email"] == "julia.prado@geb.inatel.br"
    assert gep_student["id"] == "GEP1"
    assert gep_student["email"] == "kaique.moura@gep.inatel.br"


def test_create_student_rejects_non_inatel_email_format(client: TestClient) -> None:
    response = client.post(
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


def test_create_student_rejects_email_with_course_different_from_payload(client: TestClient) -> None:
    response = client.post(
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


def test_operations_fail_for_missing_student_id(client: TestClient) -> None:
    response = client.get("/api/v1/alunos/GES999")
    patch_response = client.patch("/api/v1/alunos/GES999", json={"name": "Nao Existe"})
    delete_response = client.delete("/api/v1/alunos/GES999")

    assert response.status_code == 404
    assert patch_response.status_code == 404
    assert delete_response.status_code == 404
    assert response.json()["detail"] == "aluno nao encontrado"
