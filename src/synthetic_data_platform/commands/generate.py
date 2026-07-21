import typer

from synthetic_data_platform.app import Application
from synthetic_data_platform.config import Settings
from synthetic_data_platform.constants import SUPPORTED_ENTITIES
from synthetic_data_platform.generators.agent_generator import AgentGenerator
from synthetic_data_platform.generators.claim_generator import ClaimGenerator
from synthetic_data_platform.generators.customer_generator import CustomerGenerator
from synthetic_data_platform.generators.payment_generator import PaymentGenerator
from synthetic_data_platform.generators.policy_generator import PolicyGenerator
from synthetic_data_platform.generators.sources import load_ids, load_ids_where
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


@app.command("policies")
def generate_policies(
    count: int = typer.Option(
        200, "--count", "-n", min=1, help="Number of policy records to generate."
    ),
) -> None:
    """Generate synthetic policy records referencing existing customers and agents."""
    application = Application.bootstrap()
    settings = application.get(Settings)
    telemetry = application.get(TelemetryService)
    logger = get_logger()

    try:
        customer_ids = load_ids(settings.bronze_dir / "customers.parquet", "customer_id")
        agent_ids = load_ids(settings.bronze_dir / "agents.parquet", "agent_id")
    except FileNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    with telemetry.start_run("generate_policies") as run:
        logger.info("Starting policy generation", extra={"run_id": run.run_id})

        generator = PolicyGenerator(
            seed=settings.random_seed, customer_ids=customer_ids, agent_ids=agent_ids
        )
        policies = generator.generate(count)

        output_path = ParquetWriter().write(policies, settings.bronze_dir, "policies")

        run.record_row_count("policies", len(policies))
        run.add_output_location(str(output_path))
        logger.info(
            "Finished policy generation",
            extra={"run_id": run.run_id},
        )

    typer.echo(f"Wrote {len(policies)} policies to {output_path}")


@app.command("claims")
def generate_claims(
    count: int = typer.Option(
        150, "--count", "-n", min=1, help="Number of claim records to generate."
    ),
) -> None:
    """Generate synthetic claim records referencing existing, active policies."""
    application = Application.bootstrap()
    settings = application.get(Settings)
    telemetry = application.get(TelemetryService)
    logger = get_logger()

    try:
        policy_ids = load_ids_where(
            settings.bronze_dir / "policies.parquet", "policy_id", "status", "active"
        )
    except FileNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    if not policy_ids:
        typer.secho(
            "No active policies found. Generate policies before generating claims.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    with telemetry.start_run("generate_claims") as run:
        logger.info("Starting claim generation", extra={"run_id": run.run_id})

        generator = ClaimGenerator(seed=settings.random_seed, policy_ids=policy_ids)
        claims = generator.generate(count)

        output_path = ParquetWriter().write(claims, settings.bronze_dir, "claims")

        run.record_row_count("claims", len(claims))
        run.add_output_location(str(output_path))
        logger.info(
            "Finished claim generation",
            extra={"run_id": run.run_id},
        )

    typer.echo(f"Wrote {len(claims)} claims to {output_path}")


@app.command("payments")
def generate_payments(
    count: int = typer.Option(
        300, "--count", "-n", min=1, help="Number of payment records to generate."
    ),
) -> None:
    """Generate synthetic payment records referencing existing policies."""
    application = Application.bootstrap()
    settings = application.get(Settings)
    telemetry = application.get(TelemetryService)
    logger = get_logger()

    try:
        policy_ids = load_ids(settings.bronze_dir / "policies.parquet", "policy_id")
    except FileNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    with telemetry.start_run("generate_payments") as run:
        logger.info("Starting payment generation", extra={"run_id": run.run_id})

        generator = PaymentGenerator(seed=settings.random_seed, policy_ids=policy_ids)
        payments = generator.generate(count)

        output_path = ParquetWriter().write(payments, settings.bronze_dir, "payments")

        run.record_row_count("payments", len(payments))
        run.add_output_location(str(output_path))
        logger.info(
            "Finished payment generation",
            extra={"run_id": run.run_id},
        )

    typer.echo(f"Wrote {len(payments)} payments to {output_path}")
