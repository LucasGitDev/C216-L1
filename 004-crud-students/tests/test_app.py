from app.main import create_application


def test_create_application() -> None:
    application = create_application()

    assert application.title == "004 CRUD Alunos"
    assert application.version == "0.1.0"
