import logging
from datetime import date
from pathlib import Path
from uuid import uuid4

import polars as pl
import pytest

from synthetic_data_platform.config import Settings
from synthetic_data_platform.models.customer import Customer
from synthetic_data_platform.models.policy import Policy
from synthetic_data_platform.services.validation_service import ValidationService
from synthetic_data_platform.telemetry.service import TelemetryService
from synthetic_data_platform.writers.parquet_writer import ParquetWriter


@pytest.fixture
def logger() -> logging.Logger:
    return logging.getLogger("test_validation_service")


def _settings(tmp_path: Path) -> Settings:
    return Settings(output_dir=tmp_path / "output")


def _make_customer(**overrides: object) -> Customer:
    kwargs: dict[str, object] = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone": "555-123-4567",
        "date_of_birth": date(1990, 1, 1),
        "address_line1": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "postal_code": "62704",
    }
    kwargs.update(overrides)
    return Customer(**kwargs)


def test_validate_entity_writes_valid_rows_to_silver(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)
    customers = [_make_customer(), _make_customer(email="other@example.com")]
    ParquetWriter().write(customers, settings.bronze_dir, "customers")

    with TelemetryService().start_run("test") as run:
        ids = ValidationService().validate_entity(
            settings, run, logger, Customer, "customers", "customer_id"
        )

    silver_path = settings.silver_dir / "customers.parquet"
    assert silver_path.exists()
    assert pl.read_parquet(silver_path).height == 2
    assert ids == {c.customer_id for c in customers}
    assert run.row_counts["customers"] == 2
    assert run.warnings == []


def test_validate_entity_skips_invalid_rows_and_warns(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)
    good = _make_customer()
    bad_row = good.model_dump(mode="json")
    bad_row["email"] = "not-an-email"
    bad_row["customer_id"] = str(uuid4())
    frame = pl.DataFrame([good.model_dump(mode="json"), bad_row])
    settings.bronze_dir.mkdir(parents=True)
    frame.write_parquet(settings.bronze_dir / "customers.parquet")

    with TelemetryService().start_run("test") as run:
        ids = ValidationService().validate_entity(
            settings, run, logger, Customer, "customers", "customer_id"
        )

    assert ids == {good.customer_id}
    assert pl.read_parquet(settings.silver_dir / "customers.parquet").height == 1
    assert len(run.warnings) == 1
    assert "invalid row" in run.warnings[0]


def test_validate_entity_skips_duplicate_primary_key(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)
    customer = _make_customer()
    duplicate_row = customer.model_dump(mode="json")
    frame = pl.DataFrame([customer.model_dump(mode="json"), duplicate_row])
    settings.bronze_dir.mkdir(parents=True)
    frame.write_parquet(settings.bronze_dir / "customers.parquet")

    with TelemetryService().start_run("test") as run:
        ids = ValidationService().validate_entity(
            settings, run, logger, Customer, "customers", "customer_id"
        )

    assert ids == {customer.customer_id}
    assert pl.read_parquet(settings.silver_dir / "customers.parquet").height == 1
    assert any("duplicate" in w for w in run.warnings)


def test_validate_entity_skips_rows_with_unknown_foreign_key(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)
    known_customer_id = uuid4()
    known_agent_id = uuid4()
    valid_policy = Policy(
        policy_number="POL-A1B2C3D4",
        customer_id=known_customer_id,
        agent_id=known_agent_id,
        policy_type="auto",
        effective_date=date(2024, 1, 1),
        expiration_date=date(2025, 1, 1),
        premium_amount=1200.0,
    )
    orphan_policy = valid_policy.model_copy(
        update={"policy_id": uuid4(), "policy_number": "POL-Z9Y8X7W6", "customer_id": uuid4()}
    )
    ParquetWriter().write([valid_policy, orphan_policy], settings.bronze_dir, "policies")

    with TelemetryService().start_run("test") as run:
        ids = ValidationService().validate_entity(
            settings,
            run,
            logger,
            Policy,
            "policies",
            "policy_id",
            foreign_keys={"customer_id": {known_customer_id}, "agent_id": {known_agent_id}},
        )

    assert ids == {valid_policy.policy_id}
    assert any("unknown customer_id" in w for w in run.warnings)


def test_validate_entity_missing_bronze_file_warns_without_raising(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)

    with TelemetryService().start_run("test") as run:
        ids = ValidationService().validate_entity(
            settings, run, logger, Customer, "customers", "customer_id"
        )

    assert ids == set()
    assert not (settings.silver_dir / "customers.parquet").exists()
    assert any("not found" in w for w in run.warnings)
