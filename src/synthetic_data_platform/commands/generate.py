import typer

from synthetic_data_platform.constants import SUPPORTED_ENTITIES

app = typer.Typer(help="Generate synthetic datasets.")


@app.command("list")
def list_entities() -> None:
    """List the entities that can be generated."""
    for entity in SUPPORTED_ENTITIES:
        typer.echo(entity)
