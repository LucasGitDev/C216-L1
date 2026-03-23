import typer

from inas_cli.commands.student import app as student_app


def build_app() -> typer.Typer:
    cli = typer.Typer(
        no_args_is_help=True,
        help="Ferramentas de linha de comando da INAS.",
    )
    cli.add_typer(student_app, name="student")
    return cli
