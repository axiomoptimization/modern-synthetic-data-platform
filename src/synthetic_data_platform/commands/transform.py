import typer

from synthetic_data_platform.app import Application
from synthetic_data_platform.config import Settings
from synthetic_data_platform.services.gold_service import GoldService
from synthetic_data_platform.telemetry.service import TelemetryService
from synthetic_data_platform.utils.logging import get_logger

_SILVER_ENTITIES = ("customers", "agents", "policies", "claims", "payments")


def transform_gold() -> None:
    """Build Gold layer dimension and fact tables from validated Silver data."""
    application = Application.bootstrap()
    settings = application.get(Settings)
    telemetry = application.get(TelemetryService)
    logger = get_logger()

    if not any(
        (settings.silver_dir / f"{name}.parquet").exists() for name in _SILVER_ENTITIES
    ):
        typer.secho(
            f"No Silver data found in {settings.silver_dir}. Run 'validate' before 'transform'.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    gold = GoldService()

    with telemetry.start_run("transform") as run:
        logger.info("Starting Gold layer transformation", extra={"run_id": run.run_id})

        gold.build_dim_date(settings, run, logger)
        dim_customers = gold.build_dim_customer(settings, run, logger)
        dim_agents = gold.build_dim_agent(settings, run, logger)

        customer_keys = {row.customer_id: row.customer_key for row in dim_customers}
        agent_keys = {row.agent_id: row.agent_key for row in dim_agents}
        fact_policies = gold.build_fact_policy(settings, run, logger, customer_keys, agent_keys)

        policy_keys = {row.policy_id: row.policy_key for row in fact_policies}
        gold.build_fact_claim(settings, run, logger, policy_keys)
        gold.build_fact_payment(settings, run, logger, policy_keys)

        logger.info("Finished Gold layer transformation", extra={"run_id": run.run_id})

    typer.echo(
        f"Transformed Silver data into Gold layer with {len(run.warnings)} warning(s); "
        f"Gold output written to {settings.gold_dir}"
    )
