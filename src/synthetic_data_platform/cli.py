import typer

app = typer.Typer(
    name="synthetic-data",
    help="Generate realistic enterprise datasets for data engineering demos.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Modern Synthetic Data Platform CLI."""


if __name__ == "__main__":
    app()
