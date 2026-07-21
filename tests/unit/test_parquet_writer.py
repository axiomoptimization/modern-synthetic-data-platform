from datetime import date
from pathlib import Path

import polars as pl
import pytest

from synthetic_data_platform.models.customer import Customer
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


def test_write_creates_output_directory_and_file(tmp_path: Path) -> None:
    writer = ParquetWriter()
    output_dir = tmp_path / "bronze"

    output_path = writer.write([_make_customer()], output_dir, "customers")

    assert output_path == output_dir / "customers.parquet"
    assert output_path.exists()


def test_write_contains_expected_rows(tmp_path: Path) -> None:
    writer = ParquetWriter()
    customers = [_make_customer(), _make_customer(email="other@example.com")]

    output_path = writer.write(customers, tmp_path, "customers")

    frame = pl.read_parquet(output_path)
    assert frame.height == 2
    assert set(frame["email"]) == {"jane.doe@example.com", "other@example.com"}


def test_write_overwrites_existing_file(tmp_path: Path) -> None:
    writer = ParquetWriter()
    writer.write(
        [_make_customer(), _make_customer(email="a@example.com")], tmp_path, "customers"
    )

    output_path = writer.write([_make_customer()], tmp_path, "customers")

    frame = pl.read_parquet(output_path)
    assert frame.height == 1


def test_write_empty_records_raises(tmp_path: Path) -> None:
    writer = ParquetWriter()

    with pytest.raises(ValueError, match="empty"):
        writer.write([], tmp_path, "customers")
