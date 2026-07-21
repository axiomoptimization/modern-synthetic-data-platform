import logging
from uuid import UUID

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
from synthetic_data_platform.models.agent import Agent
from synthetic_data_platform.models.claim import Claim
from synthetic_data_platform.models.customer import Customer
from synthetic_data_platform.models.payment import Payment
from synthetic_data_platform.models.policy import Policy
from synthetic_data_platform.telemetry.models import PipelineRun
from synthetic_data_platform.telemetry.service import TelemetryService
from synthetic_data_platform.utils.logging import get_logger
from synthetic_data_platform.writers.parquet_writer import ParquetWriter

app = typer.Typer(help="Generate synthetic datasets.")


@app.command("list")
def list_entities() -> None:
    """List the entities that can be generated."""
    for entity in SUPPORTED_ENTITIES:
        typer.echo(entity)


def _generate_customers(
    settings: Settings, run: PipelineRun, logger: logging.Logger, count: int
) -> list[Customer]:
    logger.info("Starting customer generation", extra={"run_id": run.run_id})

    customers = CustomerGenerator(seed=settings.random_seed).generate(count)
    output_path = ParquetWriter().write(customers, settings.bronze_dir, "customers")

    run.record_row_count("customers", len(customers))
    run.add_output_location(str(output_path))
    logger.info("Finished customer generation", extra={"run_id": run.run_id})
    return customers


def _generate_agents(
    settings: Settings, run: PipelineRun, logger: logging.Logger, count: int
) -> list[Agent]:
    logger.info("Starting agent generation", extra={"run_id": run.run_id})

    agents = AgentGenerator(seed=settings.random_seed).generate(count)
    output_path = ParquetWriter().write(agents, settings.bronze_dir, "agents")

    run.record_row_count("agents", len(agents))
    run.add_output_location(str(output_path))
    logger.info("Finished agent generation", extra={"run_id": run.run_id})
    return agents


def _generate_policies(
    settings: Settings,
    run: PipelineRun,
    logger: logging.Logger,
    count: int,
    customer_ids: list[UUID],
    agent_ids: list[UUID],
) -> list[Policy]:
    logger.info("Starting policy generation", extra={"run_id": run.run_id})

    policies = PolicyGenerator(
        seed=settings.random_seed, customer_ids=customer_ids, agent_ids=agent_ids
    ).generate(count)
    output_path = ParquetWriter().write(policies, settings.bronze_dir, "policies")

    run.record_row_count("policies", len(policies))
    run.add_output_location(str(output_path))
    logger.info("Finished policy generation", extra={"run_id": run.run_id})
    return policies


def _generate_claims(
    settings: Settings,
    run: PipelineRun,
    logger: logging.Logger,
    count: int,
    policy_ids: list[UUID],
) -> list[Claim]:
    if not policy_ids:
        run.add_warning("No active policies available; skipped claim generation.")
        logger.warning(
            "Skipping claim generation: no active policies", extra={"run_id": run.run_id}
        )
        return []

    logger.info("Starting claim generation", extra={"run_id": run.run_id})

    claims = ClaimGenerator(seed=settings.random_seed, policy_ids=policy_ids).generate(count)
    output_path = ParquetWriter().write(claims, settings.bronze_dir, "claims")

    run.record_row_count("claims", len(claims))
    run.add_output_location(str(output_path))
    logger.info("Finished claim generation", extra={"run_id": run.run_id})
    return claims


def _generate_payments(
    settings: Settings,
    run: PipelineRun,
    logger: logging.Logger,
    count: int,
    policy_ids: list[UUID],
) -> list[Payment]:
    logger.info("Starting payment generation", extra={"run_id": run.run_id})

    payments = PaymentGenerator(seed=settings.random_seed, policy_ids=policy_ids).generate(count)
    output_path = ParquetWriter().write(payments, settings.bronze_dir, "payments")

    run.record_row_count("payments", len(payments))
    run.add_output_location(str(output_path))
    logger.info("Finished payment generation", extra={"run_id": run.run_id})
    return payments


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
        customers = _generate_customers(settings, run, logger, count)

    typer.echo(f"Wrote {len(customers)} customers to {settings.bronze_dir / 'customers.parquet'}")


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
        agents = _generate_agents(settings, run, logger, count)

    typer.echo(f"Wrote {len(agents)} agents to {settings.bronze_dir / 'agents.parquet'}")


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
        policies = _generate_policies(settings, run, logger, count, customer_ids, agent_ids)

    typer.echo(f"Wrote {len(policies)} policies to {settings.bronze_dir / 'policies.parquet'}")


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
        claims = _generate_claims(settings, run, logger, count, policy_ids)

    typer.echo(f"Wrote {len(claims)} claims to {settings.bronze_dir / 'claims.parquet'}")


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
        payments = _generate_payments(settings, run, logger, count, policy_ids)

    typer.echo(f"Wrote {len(payments)} payments to {settings.bronze_dir / 'payments.parquet'}")


@app.command("all")
def generate_all(
    customers_count: int = typer.Option(
        100, "--customers", min=1, help="Number of customer records to generate."
    ),
    agents_count: int = typer.Option(
        20, "--agents", min=1, help="Number of agent records to generate."
    ),
    policies_count: int = typer.Option(
        200, "--policies", min=1, help="Number of policy records to generate."
    ),
    claims_count: int = typer.Option(
        150, "--claims", min=1, help="Number of claim records to generate."
    ),
    payments_count: int = typer.Option(
        300, "--payments", min=1, help="Number of payment records to generate."
    ),
) -> None:
    """Generate the full Bronze layer: customers, agents, policies, claims, and payments,
    in dependency order, under a single telemetry run.
    """
    application = Application.bootstrap()
    settings = application.get(Settings)
    telemetry = application.get(TelemetryService)
    logger = get_logger()

    with telemetry.start_run("generate_all") as run:
        logger.info("Starting full Bronze layer generation", extra={"run_id": run.run_id})

        customers = _generate_customers(settings, run, logger, customers_count)
        agents = _generate_agents(settings, run, logger, agents_count)
        policies = _generate_policies(
            settings,
            run,
            logger,
            policies_count,
            customer_ids=[customer.customer_id for customer in customers],
            agent_ids=[agent.agent_id for agent in agents],
        )
        active_policy_ids = [policy.policy_id for policy in policies if policy.status == "active"]
        _generate_claims(settings, run, logger, claims_count, active_policy_ids)
        _generate_payments(
            settings,
            run,
            logger,
            payments_count,
            policy_ids=[policy.policy_id for policy in policies],
        )

        logger.info("Finished full Bronze layer generation", extra={"run_id": run.run_id})

    typer.echo(
        f"Generated {run.row_counts.get('customers', 0)} customers, "
        f"{run.row_counts.get('agents', 0)} agents, "
        f"{run.row_counts.get('policies', 0)} policies, "
        f"{run.row_counts.get('claims', 0)} claims, "
        f"{run.row_counts.get('payments', 0)} payments "
        f"to {settings.bronze_dir}"
    )
