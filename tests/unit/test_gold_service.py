import logging
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest

from synthetic_data_platform.config import Settings
from synthetic_data_platform.models.claim import Claim
from synthetic_data_platform.models.payment import Payment
from synthetic_data_platform.models.policy import Policy
from synthetic_data_platform.services.gold_service import GoldService
from synthetic_data_platform.telemetry.service import TelemetryService
from synthetic_data_platform.writers.parquet_writer import ParquetWriter


@pytest.fixture
def logger() -> logging.Logger:
    return logging.getLogger("test_gold_service")


def _settings(tmp_path: Path) -> Settings:
    return Settings(output_dir=tmp_path / "output")


def _write_silver_fixtures(settings: Settings) -> None:
    policy = Policy(
        policy_number="POL-A1B2C3D4",
        customer_id=uuid4(),
        agent_id=uuid4(),
        policy_type="auto",
        effective_date=date(2024, 1, 10),
        expiration_date=date(2024, 1, 20),
        premium_amount=1200.0,
    )
    claim = Claim(
        claim_number="CLM-A1B2C3D4",
        policy_id=policy.policy_id,
        claim_type="collision",
        date_of_loss=date(2024, 1, 5),
        report_date=date(2024, 1, 6),
        claim_amount=500.0,
    )
    payment = Payment(
        payment_number="PMT-A1B2C3D4",
        policy_id=policy.policy_id,
        payment_date=date(2024, 1, 25),
        amount=100.0,
        payment_method="credit_card",
    )
    ParquetWriter().write([policy], settings.silver_dir, "policies")
    ParquetWriter().write([claim], settings.silver_dir, "claims")
    ParquetWriter().write([payment], settings.silver_dir, "payments")


def test_build_dim_date_covers_full_range_from_silver(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)
    _write_silver_fixtures(settings)

    with TelemetryService().start_run("test") as run:
        rows = GoldService().build_dim_date(settings, run, logger)

    assert min(row.date for row in rows) == date(2024, 1, 5)
    assert max(row.date for row in rows) == date(2024, 1, 25)
    assert len(rows) == 21
    assert run.row_counts["dim_date"] == 21
    assert run.warnings == []


def test_build_dim_date_key_and_attributes_are_correct(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)
    _write_silver_fixtures(settings)

    with TelemetryService().start_run("test") as run:
        rows = GoldService().build_dim_date(settings, run, logger)

    saturday = next(row for row in rows if row.date == date(2024, 1, 6))
    assert saturday.date_key == 20240106
    assert saturday.day_of_week == 6
    assert saturday.day_name == "Saturday"
    assert saturday.is_weekend is True

    monday = next(row for row in rows if row.date == date(2024, 1, 15))
    assert monday.is_weekend is False
    assert monday.quarter == 1


def test_build_dim_date_without_silver_data_warns_without_raising(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)

    with TelemetryService().start_run("test") as run:
        rows = GoldService().build_dim_date(settings, run, logger)

    assert rows == []
    assert not (settings.gold_dir / "dim_date.parquet").exists()
    assert any("no Silver date columns" in w for w in run.warnings)
