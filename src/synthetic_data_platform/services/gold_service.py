from __future__ import annotations

import logging
from collections.abc import Iterator
from datetime import date, timedelta
from uuid import UUID

import polars as pl

from synthetic_data_platform.config import Settings
from synthetic_data_platform.models.dim_agent import DimAgent
from synthetic_data_platform.models.dim_customer import DimCustomer
from synthetic_data_platform.models.dim_date import DimDate
from synthetic_data_platform.models.fact_claim import FactClaim
from synthetic_data_platform.models.fact_payment import FactPayment
from synthetic_data_platform.models.fact_policy import FactPolicy
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

    def build_fact_policy(
        self,
        settings: Settings,
        run: PipelineRun,
        logger: logging.Logger,
        customer_keys: dict[UUID, int],
        agent_keys: dict[UUID, int],
    ) -> list[FactPolicy]:
        path = settings.silver_dir / "policies.parquet"
        if not path.exists():
            self._warn(run, logger, "fact_policy: Silver policies not found, skipping")
            return []

        rows = pl.read_parquet(path).sort("policy_id").to_dicts()
        fact_policies: list[FactPolicy] = []
        next_key = 1
        for row in rows:
            customer_key = customer_keys.get(UUID(row["customer_id"]))
            agent_key = agent_keys.get(UUID(row["agent_id"]))
            if customer_key is None or agent_key is None:
                self._warn(
                    run,
                    logger,
                    f"fact_policy: skipped policy {row['policy_id']} with unresolved "
                    "dimension key",
                )
                continue

            fact_policies.append(
                FactPolicy(
                    policy_key=next_key,
                    policy_id=row["policy_id"],
                    customer_key=customer_key,
                    agent_key=agent_key,
                    effective_date_key=self._date_key(date.fromisoformat(row["effective_date"])),
                    expiration_date_key=self._date_key(
                        date.fromisoformat(row["expiration_date"])
                    ),
                    policy_number=row["policy_number"],
                    policy_type=row["policy_type"],
                    status=row["status"],
                    premium_amount=row["premium_amount"],
                )
            )
            next_key += 1

        output_path = ParquetWriter().write(fact_policies, settings.gold_dir, "fact_policy")
        run.record_row_count("fact_policy", len(fact_policies))
        run.add_output_location(str(output_path))
        logger.info(
            f"Built fact_policy with {len(fact_policies)} rows", extra={"run_id": run.run_id}
        )
        return fact_policies

    def build_fact_claim(
        self,
        settings: Settings,
        run: PipelineRun,
        logger: logging.Logger,
        policy_keys: dict[UUID, int],
    ) -> list[FactClaim]:
        path = settings.silver_dir / "claims.parquet"
        if not path.exists():
            self._warn(run, logger, "fact_claim: Silver claims not found, skipping")
            return []

        rows = pl.read_parquet(path).sort("claim_id").to_dicts()
        fact_claims: list[FactClaim] = []
        next_key = 1
        for row in rows:
            policy_key = policy_keys.get(UUID(row["policy_id"]))
            if policy_key is None:
                self._warn(
                    run,
                    logger,
                    f"fact_claim: skipped claim {row['claim_id']} with unresolved policy key",
                )
                continue

            fact_claims.append(
                FactClaim(
                    claim_key=next_key,
                    claim_id=row["claim_id"],
                    policy_key=policy_key,
                    date_of_loss_key=self._date_key(date.fromisoformat(row["date_of_loss"])),
                    report_date_key=self._date_key(date.fromisoformat(row["report_date"])),
                    claim_number=row["claim_number"],
                    claim_type=row["claim_type"],
                    status=row["status"],
                    claim_amount=row["claim_amount"],
                    paid_amount=row["paid_amount"],
                )
            )
            next_key += 1

        output_path = ParquetWriter().write(fact_claims, settings.gold_dir, "fact_claim")
        run.record_row_count("fact_claim", len(fact_claims))
        run.add_output_location(str(output_path))
        logger.info(
            f"Built fact_claim with {len(fact_claims)} rows", extra={"run_id": run.run_id}
        )
        return fact_claims

    def build_fact_payment(
        self,
        settings: Settings,
        run: PipelineRun,
        logger: logging.Logger,
        policy_keys: dict[UUID, int],
    ) -> list[FactPayment]:
        path = settings.silver_dir / "payments.parquet"
        if not path.exists():
            self._warn(run, logger, "fact_payment: Silver payments not found, skipping")
            return []

        rows = pl.read_parquet(path).sort("payment_id").to_dicts()
        fact_payments: list[FactPayment] = []
        next_key = 1
        for row in rows:
            policy_key = policy_keys.get(UUID(row["policy_id"]))
            if policy_key is None:
                self._warn(
                    run,
                    logger,
                    f"fact_payment: skipped payment {row['payment_id']} with unresolved "
                    "policy key",
                )
                continue

            fact_payments.append(
                FactPayment(
                    payment_key=next_key,
                    payment_id=row["payment_id"],
                    policy_key=policy_key,
                    payment_date_key=self._date_key(date.fromisoformat(row["payment_date"])),
                    payment_number=row["payment_number"],
                    payment_method=row["payment_method"],
                    status=row["status"],
                    amount=row["amount"],
                )
            )
            next_key += 1

        output_path = ParquetWriter().write(fact_payments, settings.gold_dir, "fact_payment")
        run.record_row_count("fact_payment", len(fact_payments))
        run.add_output_location(str(output_path))
        logger.info(
            f"Built fact_payment with {len(fact_payments)} rows", extra={"run_id": run.run_id}
        )
        return fact_payments

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
    def _date_key(current: date) -> int:
        return int(current.strftime("%Y%m%d"))

    @classmethod
    def _build_date_row(cls, current: date) -> DimDate:
        return DimDate(
            date_key=cls._date_key(current),
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
