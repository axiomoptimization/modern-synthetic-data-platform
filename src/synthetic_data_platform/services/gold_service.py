from __future__ import annotations

import logging
from collections.abc import Iterator
from datetime import date, timedelta

import polars as pl

from synthetic_data_platform.config import Settings
from synthetic_data_platform.models.dim_agent import DimAgent
from synthetic_data_platform.models.dim_customer import DimCustomer
from synthetic_data_platform.models.dim_date import DimDate
from synthetic_data_platform.telemetry.models import PipelineRun
from synthetic_data_platform.writers.parquet_writer import ParquetWriter

# Silver files and date columns that determine dim_date's coverage range.
_SILVER_DATE_COLUMNS: dict[str, tuple[str, ...]] = {
    "policies": ("effective_date", "expiration_date"),
    "claims": ("date_of_loss", "report_date"),
    "payments": ("payment_date",),
}


class GoldService:
    """Builds Gold layer dimension and fact tables from validated Silver data."""

    def build_dim_date(
        self, settings: Settings, run: PipelineRun, logger: logging.Logger
    ) -> list[DimDate]:
        bounds = self._collect_date_bounds(settings)
        if bounds is None:
            self._warn(run, logger, "dim_date: no Silver date columns found, skipping")
            return []

        start, end = bounds
        dim_dates = [self._build_date_row(current) for current in self._date_range(start, end)]

        output_path = ParquetWriter().write(dim_dates, settings.gold_dir, "dim_date")
        run.record_row_count("dim_date", len(dim_dates))
        run.add_output_location(str(output_path))
        logger.info(f"Built dim_date with {len(dim_dates)} rows", extra={"run_id": run.run_id})
        return dim_dates

    def build_dim_customer(
        self, settings: Settings, run: PipelineRun, logger: logging.Logger
    ) -> list[DimCustomer]:
        path = settings.silver_dir / "customers.parquet"
        if not path.exists():
            self._warn(run, logger, "dim_customer: Silver customers not found, skipping")
            return []

        rows = pl.read_parquet(path).sort("customer_id").to_dicts()
        dim_customers = [
            DimCustomer(
                customer_key=index + 1,
                customer_id=row["customer_id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                phone=row["phone"],
                city=row["city"],
                state=row["state"],
                postal_code=row["postal_code"],
            )
            for index, row in enumerate(rows)
        ]

        output_path = ParquetWriter().write(dim_customers, settings.gold_dir, "dim_customer")
        run.record_row_count("dim_customer", len(dim_customers))
        run.add_output_location(str(output_path))
        logger.info(
            f"Built dim_customer with {len(dim_customers)} rows", extra={"run_id": run.run_id}
        )
        return dim_customers

    def build_dim_agent(
        self, settings: Settings, run: PipelineRun, logger: logging.Logger
    ) -> list[DimAgent]:
        path = settings.silver_dir / "agents.parquet"
        if not path.exists():
            self._warn(run, logger, "dim_agent: Silver agents not found, skipping")
            return []

        rows = pl.read_parquet(path).sort("agent_id").to_dicts()
        dim_agents = [
            DimAgent(
                agent_key=index + 1,
                agent_id=row["agent_id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                agency_name=row["agency_name"],
                license_number=row["license_number"],
                license_state=row["license_state"],
            )
            for index, row in enumerate(rows)
        ]

        output_path = ParquetWriter().write(dim_agents, settings.gold_dir, "dim_agent")
        run.record_row_count("dim_agent", len(dim_agents))
        run.add_output_location(str(output_path))
        logger.info(f"Built dim_agent with {len(dim_agents)} rows", extra={"run_id": run.run_id})
        return dim_agents

    @staticmethod
    def _collect_date_bounds(settings: Settings) -> tuple[date, date] | None:
        dates: list[date] = []
        for file_name, columns in _SILVER_DATE_COLUMNS.items():
            path = settings.silver_dir / f"{file_name}.parquet"
            if not path.exists():
                continue
            frame = pl.read_parquet(path, columns=list(columns))
            for column in columns:
                dates.extend(
                    date.fromisoformat(value) for value in frame[column].drop_nulls().to_list()
                )

        if not dates:
            return None
        return min(dates), max(dates)

    @staticmethod
    def _date_range(start: date, end: date) -> Iterator[date]:
        current = start
        while current <= end:
            yield current
            current += timedelta(days=1)

    @staticmethod
    def _build_date_row(current: date) -> DimDate:
        return DimDate(
            date_key=int(current.strftime("%Y%m%d")),
            date=current,
            year=current.year,
            quarter=(current.month - 1) // 3 + 1,
            month=current.month,
            month_name=current.strftime("%B"),
            day=current.day,
            day_of_week=current.isoweekday(),
            day_name=current.strftime("%A"),
            is_weekend=current.isoweekday() >= 6,
        )

    @staticmethod
    def _warn(run: PipelineRun, logger: logging.Logger, message: str) -> None:
        run.add_warning(message)
        logger.warning(message, extra={"run_id": run.run_id})
