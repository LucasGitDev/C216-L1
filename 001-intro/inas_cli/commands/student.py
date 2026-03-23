import typer

from inas_cli.repositories.in_memory_student_repository import InMemoryStudentRepository
from inas_cli.repositories.json_student_repository import JsonStudentRepository
from inas_cli.services.errors import StudentError
from inas_cli.services.student_service import StudentService

app = typer.Typer(no_args_is_help=True, help="Operações de alunos.")


def _get_service(ctx: typer.Context) -> StudentService:
    return ctx.obj["student_service"]


@app.callback()
def configure(
    ctx: typer.Context,
    file_path: str | None = typer.Option(
        None,
        "--file",
        "-f",
        help="Arquivo JSON para persistência dos alunos.",
    ),
) -> None:
    repository = (
        JsonStudentRepository(file_path) if file_path else InMemoryStudentRepository()
    )
    ctx.obj = {"student_service": StudentService(repository)}


@app.command("create")
def create(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Nome do aluno."),
    email: str = typer.Argument(..., help="Email do aluno."),
    course: str = typer.Argument(..., help="Curso do aluno, ex: GES."),
) -> None:
    try:
        student = _get_service(ctx).create(name=name, email=email, course=course)
        typer.echo(f"Aluno criado com sucesso. Matrícula: {student.enrollment}")
    except StudentError as error:
        raise typer.BadParameter(str(error)) from error


@app.command("list")
def list_students(ctx: typer.Context) -> None:
    students = _get_service(ctx).list_all()
    if not students:
        typer.echo("Nenhum aluno cadastrado.")
        return

    for student in students:
        typer.echo(
            f"{student.enrollment} | {student.name} | {student.email} | {student.course.value}"
        )


@app.command("get")
def get_student(ctx: typer.Context, enrollment: str = typer.Argument(...)) -> None:
    try:
        student = _get_service(ctx).get(enrollment)
        typer.echo(
            f"{student.enrollment} | {student.name} | {student.email} | {student.course.value}"
        )
    except StudentError as error:
        raise typer.BadParameter(str(error)) from error


@app.command("update")
def update(
    ctx: typer.Context,
    enrollment: str = typer.Argument(..., help="Matrícula atual."),
    name: str | None = typer.Option(None, "--name", help="Novo nome."),
    email: str | None = typer.Option(None, "--email", help="Novo email."),
    course: str | None = typer.Option(None, "--course", help="Novo curso."),
) -> None:
    try:
        student = _get_service(ctx).update(
            enrollment=enrollment,
            name=name,
            email=email,
            course=course,
        )
        typer.echo(f"Aluno atualizado com sucesso. Matrícula: {student.enrollment}")
    except StudentError as error:
        raise typer.BadParameter(str(error)) from error


@app.command("delete")
def delete(ctx: typer.Context, enrollment: str = typer.Argument(...)) -> None:
    try:
        _get_service(ctx).delete(enrollment)
        typer.echo("Aluno removido com sucesso.")
    except StudentError as error:
        raise typer.BadParameter(str(error)) from error
