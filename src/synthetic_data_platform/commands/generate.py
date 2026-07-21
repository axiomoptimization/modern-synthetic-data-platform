import typer

from synthetic_data_platform.app import Application
from synthetic_data_platform.config import Settings
from synthetic_data_platform.constants import SUPPORTED_ENTITIES
from synthetic_data_platform.generators.agent_generator import AgentGenerator
from synthetic_data_platform.generators.customer_generator import CustomerGenerator
from synthetic_data_platform.telemetry.service import TelemetryService
from synthetic_data_platform.utils.logging import get_logger
from synthetic_data_platform.writers.parquet_writer import ParquetWriter

app = typer.Typer(help="Generate synthetic datasets.")


@app.command("list")
def list_entities() -> None:
    """List the entities that can be generated."""
    for entity in SUPPORTED_ENTITIES:
        typer.echo(entity)


@app.command("customers")
def generate_customers(
    count: int = typer.Option(
        100, "--count", "-n", min=1, help="Number of customer records to generate."
    ),
) -> None:
    """Generate synthetic customer records and write them to the Bronze layer."""
    application = Application.bootstrap()
    settings = application.get(Settings)
    telemetry = application.get(TelemetryService)
    logger = get_logger()

    with telemetry.start_run("generate_customers") as run:
        logger.info("Starting customer generation", extra={"run_id": run.run_id})

        generator = CustomerGenerator(seed=settings.random_seed)
        customers = generator.generate(count)

        output_path = ParquetWriter().write(customers, settings.bronze_dir, "customers")

        run.record_row_count("customers", len(customers))
        run.add_output_location(str(output_path))
        logger.info(
            "Finished customer generation",
            extra={"run_id": run.run_id},
        )

    typer.echo(f"Wrote {len(customers)} customers to {output_path}")


@app.command("agents")
def generate_agents(
    count: int = typer.Option(
        20, "--count", "-n", min=1, help="Number of agent records to generate."
    ),
) -> None:
    """Generate synthetic agent records and write them to the Bronze layer."""
    application = Application.bootstrap()
    settings = application.get(Settings)
    telemetry = application.get(TelemetryService)
    logger = get_logger()

    with telemetry.start_run("generate_agents") as run:
        logger.info("Starting agent generation", extra={"run_id": run.run_id})

        generator = AgentGenerator(seed=settings.random_seed)
        agents = generator.generate(count)

        output_path = ParquetWriter().write(agents, settings.bronze_dir, "agents")

        run.record_row_count("agents", len(agents))
        run.add_output_location(str(output_path))
        logger.info(
            "Finished agent generation",
            extra={"run_id": run.run_id},
        )

    typer.echo(f"Wrote {len(agents)} agents to {output_path}")
