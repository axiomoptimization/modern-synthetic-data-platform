import typer

from synthetic_data_platform import __version__
from synthetic_data_platform.commands import generate

app = typer.Typer(
    name="synthetic-data",
    help="Generate realistic enterprise datasets for data engineering demos.",
    no_args_is_help=True,
)
app.add_typer(generate.app, name="generate")


@app.callback()
def main() -> None:
    """Modern Synthetic Data Platform CLI."""


@app.command()
def version() -> None:
    """Show the installed package version."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
