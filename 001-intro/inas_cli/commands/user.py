import typer

app = typer.Typer(no_args_is_help=True, help="Operacoes de usuarios.")


@app.command()
def create(name: str) -> None:
    typer.echo(f"Usuario criado: {name}")
