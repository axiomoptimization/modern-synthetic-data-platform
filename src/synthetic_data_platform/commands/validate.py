import typer

from synthetic_data_platform.app import Application
from synthetic_data_platform.config import Settings
from synthetic_data_platform.services.validation_service import ValidationService
from synthetic_data_platform.telemetry.service import TelemetryService
from synthetic_data_platform.utils.logging import get_logger


def validate_bronze() -> None:
    """Validate Bronze datasets and write cleansed output to the Silver layer."""
    application = Application.bootstrap()
    settings = application.get(Settings)
    telemetry = application.get(TelemetryService)
    logger = get_logger()

    with telemetry.start_run("validate") as run:
        logger.info("Starting Bronze validation", extra={"run_id": run.run_id})
        ValidationService().validate_all(settings, run, logger)
        logger.info("Finished Bronze validation", extra={"run_id": run.run_id})

    typer.echo(
        f"Validated Bronze data with {len(run.warnings)} warning(s); "
        f"Silver output written to {settings.silver_dir}"
    )
