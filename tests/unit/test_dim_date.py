from datetime import date

from synthetic_data_platform.models.dim_date import DimDate


def test_dim_date_validates_successfully() -> None:
    row = DimDate(
        date_key=20240115,
        date=date(2024, 1, 15),
        year=2024,
        quarter=1,
        month=1,
        month_name="January",
        day=15,
        day_of_week=1,
        day_name="Monday",
        is_weekend=False,
    )

    assert row.date_key == 20240115


def test_dim_date_serializes_to_json() -> None:
    row = DimDate(
        date_key=20240115,
        date=date(2024, 1, 15),
        year=2024,
        quarter=1,
        month=1,
        month_name="January",
        day=15,
        day_of_week=1,
        day_name="Monday",
        is_weekend=False,
    )

    payload = row.model_dump_json()

    assert "20240115" in payload
