from datetime import date
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from synthetic_data_platform.generators.sources import load_ids, load_ids_where
from synthetic_data_platform.models.customer import Customer
from synthetic_data_platform.models.policy import Policy
from synthetic_data_platform.writers.parquet_writer import ParquetWriter


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


def test_load_ids_returns_uuids(tmp_path: Path) -> None:
    customers = [_make_customer(), _make_customer(email="other@example.com")]
    output_path = ParquetWriter().write(customers, tmp_path, "customers")

    ids = load_ids(output_path, "customer_id")

    assert ids == [c.customer_id for c in customers]
    assert all(isinstance(customer_id, UUID) for customer_id in ids)


def test_load_ids_raises_when_file_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Generate the parent entity first"):
        load_ids(tmp_path / "customers.parquet", "customer_id")


def _make_policy(**overrides: object) -> Policy:
    kwargs: dict[str, object] = {
        "policy_number": "POL-A1B2C3D4",
        "customer_id": uuid4(),
        "agent_id": uuid4(),
        "policy_type": "auto",
        "effective_date": date(2024, 1, 1),
        "expiration_date": date(2025, 1, 1),
        "premium_amount": 1200.0,
    }
    kwargs.update(overrides)
    return Policy(**kwargs)


def test_load_ids_where_filters_by_column(tmp_path: Path) -> None:
    active = _make_policy(status="active")
    cancelled = _make_policy(
        policy_number="POL-Z9Y8X7W6",
        status="cancelled",
        effective_date=date(2023, 1, 1),
        expiration_date=date(2024, 1, 1),
    )
    output_path = ParquetWriter().write([active, cancelled], tmp_path, "policies")

    ids = load_ids_where(output_path, "policy_id", "status", "active")

    assert ids == [active.policy_id]


def test_load_ids_where_raises_when_file_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Generate the parent entity first"):
        load_ids_where(tmp_path / "policies.parquet", "policy_id", "status", "active")
