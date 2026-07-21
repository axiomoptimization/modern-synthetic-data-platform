import logging
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest

from synthetic_data_platform.config import Settings
from synthetic_data_platform.models.agent import Agent
from synthetic_data_platform.models.claim import Claim
from synthetic_data_platform.models.customer import Customer
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


def test_build_dim_customer_writes_all_rows_with_surrogate_keys(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)
    customers = [_make_customer(), _make_customer(email="other@example.com")]
    ParquetWriter().write(customers, settings.silver_dir, "customers")

    with TelemetryService().start_run("test") as run:
        rows = GoldService().build_dim_customer(settings, run, logger)

    assert len(rows) == 2
    assert {row.customer_key for row in rows} == {1, 2}
    assert {row.customer_id for row in rows} == {c.customer_id for c in customers}
    assert run.row_counts["dim_customer"] == 2


def test_build_dim_customer_surrogate_keys_are_deterministic(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)
    customers = [_make_customer(), _make_customer(email="other@example.com")]
    ParquetWriter().write(customers, settings.silver_dir, "customers")

    with TelemetryService().start_run("test") as run:
        first = GoldService().build_dim_customer(settings, run, logger)
        second = GoldService().build_dim_customer(settings, run, logger)

    first_keys = {row.customer_id: row.customer_key for row in first}
    second_keys = {row.customer_id: row.customer_key for row in second}
    assert first_keys == second_keys


def test_build_dim_customer_without_silver_data_warns_without_raising(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)

    with TelemetryService().start_run("test") as run:
        rows = GoldService().build_dim_customer(settings, run, logger)

    assert rows == []
    assert not (settings.gold_dir / "dim_customer.parquet").exists()
    assert any("Silver customers not found" in w for w in run.warnings)


def _make_agent(**overrides: object) -> Agent:
    kwargs: dict[str, object] = {
        "first_name": "Sam",
        "last_name": "Rivera",
        "email": "sam.rivera@example.com",
        "phone": "555-987-6543",
        "agency_name": "Rivera Insurance Group",
        "license_number": "ABC12345",
        "license_state": "IL",
        "hire_date": date(2015, 6, 1),
    }
    kwargs.update(overrides)
    return Agent(**kwargs)


def test_build_dim_agent_writes_all_rows_with_surrogate_keys(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)
    agents = [_make_agent(), _make_agent(email="other@example.com")]
    ParquetWriter().write(agents, settings.silver_dir, "agents")

    with TelemetryService().start_run("test") as run:
        rows = GoldService().build_dim_agent(settings, run, logger)

    assert len(rows) == 2
    assert {row.agent_key for row in rows} == {1, 2}
    assert {row.agent_id for row in rows} == {a.agent_id for a in agents}
    assert run.row_counts["dim_agent"] == 2


def test_build_dim_agent_without_silver_data_warns_without_raising(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)

    with TelemetryService().start_run("test") as run:
        rows = GoldService().build_dim_agent(settings, run, logger)

    assert rows == []
    assert not (settings.gold_dir / "dim_agent.parquet").exists()
    assert any("Silver agents not found" in w for w in run.warnings)


def _make_policy(**overrides: object) -> Policy:
    kwargs: dict[str, object] = {
        "policy_number": "POL-A1B2C3D4",
        "customer_id": uuid4(),
        "agent_id": uuid4(),
        "policy_type": "auto",
        "effective_date": date(2024, 1, 10),
        "expiration_date": date(2025, 1, 10),
        "premium_amount": 1200.0,
    }
    kwargs.update(overrides)
    return Policy(**kwargs)


def test_build_fact_policy_resolves_dimension_keys(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)
    customer = _make_customer()
    agent = _make_agent()
    policy = _make_policy(customer_id=customer.customer_id, agent_id=agent.agent_id)
    ParquetWriter().write([policy], settings.silver_dir, "policies")

    with TelemetryService().start_run("test") as run:
        rows = GoldService().build_fact_policy(
            settings,
            run,
            logger,
            customer_keys={customer.customer_id: 7},
            agent_keys={agent.agent_id: 9},
        )

    assert len(rows) == 1
    assert rows[0].customer_key == 7
    assert rows[0].agent_key == 9
    assert rows[0].effective_date_key == 20240110
    assert rows[0].expiration_date_key == 20250110
    assert rows[0].policy_key == 1
    assert run.row_counts["fact_policy"] == 1


def test_build_fact_policy_skips_rows_with_unresolved_dimension_keys(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)
    resolvable = _make_policy()
    unresolvable = _make_policy(policy_number="POL-Z9Y8X7W6")
    ParquetWriter().write([resolvable, unresolvable], settings.silver_dir, "policies")

    with TelemetryService().start_run("test") as run:
        rows = GoldService().build_fact_policy(
            settings,
            run,
            logger,
            customer_keys={resolvable.customer_id: 1},
            agent_keys={resolvable.agent_id: 1},
        )

    assert len(rows) == 1
    assert rows[0].policy_id == resolvable.policy_id
    assert any("unresolved dimension key" in w for w in run.warnings)


def test_build_fact_policy_without_silver_data_warns_without_raising(
    tmp_path: Path, logger: logging.Logger
) -> None:
    settings = _settings(tmp_path)

    with TelemetryService().start_run("test") as run:
        rows = GoldService().build_fact_policy(settings, run, logger, {}, {})

    assert rows == []
    assert not (settings.gold_dir / "fact_policy.parquet").exists()
    assert any("Silver policies not found" in w for w in run.warnings)
